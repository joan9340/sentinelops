"""Autenticación: login, registro de cuentas y recuperación de contraseña por correo."""
import hashlib
import hmac
import re
import secrets
from datetime import timedelta

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Request, status
from pydantic import BaseModel
from sqlalchemy import func
from sqlalchemy.orm import Session

from app import config
from app.database import PasswordResetDB, UserDB, get_db, utcnow
from app.i18n import get_lang, msg
from app.security import crear_token, get_password_hash, verify_password
from app.services.audit import registrar_auditoria
from app.services.email_service import enviar_codigo_recuperacion
from app.services.turnstile import verificar_turnstile

router = APIRouter(prefix="/api/v1/auth", tags=["Autenticación"])

USERNAME_RE = re.compile(r"^[A-Za-z0-9_.-]{3,30}$")
EMAIL_RE = re.compile(r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$")


# --- Modelos de entrada ---
class LoginRequest(BaseModel):
    username: str
    password: str
    turnstile_token: str | None = None


class RegisterRequest(BaseModel):
    username: str
    email: str
    password: str
    turnstile_token: str | None = None


class ForgotRequest(BaseModel):
    email: str
    turnstile_token: str | None = None


class ResetRequest(BaseModel):
    email: str
    code: str
    new_password: str


# --- Utilidades ---
def _exigir_captcha(db: Session, request: Request, token: str | None, actor: str, lang: str) -> None:
    ip = request.client.host if request.client else None
    ok, motivo = verificar_turnstile(token, ip)
    if ok:
        return
    registrar_auditoria(db, actor or "anónimo", "CAPTCHA_FALLIDO", f"Verificación Turnstile rechazada: {motivo}", "ALERTA")
    if motivo == "network-error":
        raise HTTPException(status.HTTP_503_SERVICE_UNAVAILABLE, msg("captcha_unavailable", lang))
    raise HTTPException(status.HTTP_400_BAD_REQUEST, msg("captcha_failed", lang))


def _normalizar_email(email: str, lang: str) -> str:
    limpio = (email or "").strip().lower()
    if len(limpio) > 255 or not EMAIL_RE.match(limpio):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, msg("email_invalid", lang))
    return limpio


def _validar_password(password: str, lang: str) -> None:
    ok = (
        8 <= len(password or "") <= 72  # 72 = límite real de bcrypt
        and re.search(r"[A-Za-z]", password)
        and re.search(r"\d", password)
    )
    if not ok:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, msg("password_weak", lang))


def _hash_codigo(user_id: int, codigo: str) -> str:
    return hashlib.sha256(f"{user_id}:{codigo}:{config.JWT_SECRET}".encode()).hexdigest()


# --- Login ---
@router.post("/login")
def login(credentials: LoginRequest, request: Request, db: Session = Depends(get_db), lang: str = Depends(get_lang)):
    _exigir_captcha(db, request, credentials.turnstile_token, credentials.username, lang)

    user = db.query(UserDB).filter(UserDB.username == credentials.username).first()
    if not user or not verify_password(credentials.password, user.hashed_password):
        registrar_auditoria(db, credentials.username, "LOGIN_FALLIDO",
                            "Intento de acceso con contraseña incorrecta o usuario inexistente", "ALERTA")
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, msg("invalid_credentials", lang))

    if not user.is_active:
        registrar_auditoria(db, user.username, "LOGIN_BLOQUEADO", "Intento de acceso desde cuenta suspendida", "ALERTA")
        raise HTTPException(status.HTTP_403_FORBIDDEN, msg("account_suspended", lang))

    registrar_auditoria(db, user.username, "LOGIN_EXITOSO", f"Inicio de sesión correcto con perfil [{user.rol}]")
    return {"access_token": crear_token(user.username, user.rol), "token_type": "bearer",
            "username": user.username, "rol": user.rol}


# --- Registro de cuentas nuevas (siempre con rol 'operador') ---
@router.post("/register", status_code=status.HTTP_201_CREATED)
def register(datos: RegisterRequest, request: Request, db: Session = Depends(get_db), lang: str = Depends(get_lang)):
    _exigir_captcha(db, request, datos.turnstile_token, datos.username, lang)

    username = (datos.username or "").strip()
    if not USERNAME_RE.match(username):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, msg("username_invalid", lang))
    email = _normalizar_email(datos.email, lang)
    _validar_password(datos.password, lang)

    if db.query(UserDB).filter(func.lower(UserDB.username) == username.lower()).first():
        raise HTTPException(status.HTTP_409_CONFLICT, msg("username_taken", lang))
    if db.query(UserDB).filter(UserDB.email == email).first():
        raise HTTPException(status.HTTP_409_CONFLICT, msg("email_taken", lang))

    nuevo = UserDB(username=username, email=email, hashed_password=get_password_hash(datos.password),
                   rol="operador", is_active=True)
    db.add(nuevo)
    db.commit()
    registrar_auditoria(db, username, "REGISTRO_CUENTA", f"Autorregistro de cuenta nueva con perfil [{nuevo.rol}]")
    return {"message": msg("register_ok", lang), "username": nuevo.username}


# --- Recuperar contraseña: paso 1 (enviar código) ---
@router.post("/forgot-password")
def forgot_password(
    datos: ForgotRequest,
    request: Request,
    background: BackgroundTasks,
    db: Session = Depends(get_db),
    lang: str = Depends(get_lang),
):
    _exigir_captcha(db, request, datos.turnstile_token, "recuperacion", lang)
    email = _normalizar_email(datos.email, lang)
    respuesta = {"message": msg("reset_requested", lang)}  # misma respuesta exista o no el correo

    user = db.query(UserDB).filter(UserDB.email == email).first()
    if not user or not user.is_active:
        return respuesta

    hace_una_hora = utcnow() - timedelta(hours=1)
    recientes = (
        db.query(func.count(PasswordResetDB.id))
        .filter(PasswordResetDB.user_id == user.id, PasswordResetDB.created_at >= hace_una_hora)
        .scalar() or 0
    )
    if recientes >= config.RESET_MAX_REQUESTS_PER_HOUR:
        registrar_auditoria(db, user.username, "RESET_LIMITE", "Demasiadas solicitudes de recuperación en 1 hora", "ALERTA")
        return respuesta

    codigo = f"{secrets.randbelow(10**6):06d}"
    db.query(PasswordResetDB).filter(PasswordResetDB.user_id == user.id, PasswordResetDB.used.is_(False)) \
        .update({"used": True})
    db.add(PasswordResetDB(user_id=user.id, code_hash=_hash_codigo(user.id, codigo),
                           expires_at=utcnow() + timedelta(minutes=config.RESET_CODE_MINUTES)))
    db.commit()

    background.add_task(enviar_codigo_recuperacion, email, user.username, codigo, lang)
    registrar_auditoria(db, user.username, "RESET_SOLICITADO", "Se envió un código de recuperación al correo registrado")
    return respuesta


# --- Recuperar contraseña: paso 2 (código + nueva contraseña) ---
@router.post("/reset-password")
def reset_password(datos: ResetRequest, db: Session = Depends(get_db), lang: str = Depends(get_lang)):
    email = _normalizar_email(datos.email, lang)
    _validar_password(datos.new_password, lang)

    user = db.query(UserDB).filter(UserDB.email == email).first()
    reset = None
    if user and user.is_active:
        reset = (
            db.query(PasswordResetDB)
            .filter(PasswordResetDB.user_id == user.id, PasswordResetDB.used.is_(False))
            .order_by(PasswordResetDB.id.desc())
            .first()
        )
    if not reset or reset.expires_at < utcnow():
        raise HTTPException(status.HTTP_400_BAD_REQUEST, msg("reset_invalid_code", lang))

    if reset.attempts >= config.RESET_MAX_ATTEMPTS:
        reset.used = True
        db.commit()
        raise HTTPException(status.HTTP_429_TOO_MANY_REQUESTS, msg("reset_too_many", lang))

    codigo = (datos.code or "").strip()
    if not hmac.compare_digest(_hash_codigo(user.id, codigo), reset.code_hash):
        reset.attempts += 1
        db.commit()
        registrar_auditoria(db, user.username, "RESET_CODIGO_INVALIDO", "Código de recuperación incorrecto", "ALERTA")
        raise HTTPException(status.HTTP_400_BAD_REQUEST, msg("reset_invalid_code", lang))

    user.hashed_password = get_password_hash(datos.new_password)
    reset.used = True
    db.commit()
    registrar_auditoria(db, user.username, "RESET_EXITOSO", "Contraseña restablecida mediante código enviado por correo")
    return {"message": msg("reset_ok", lang)}
