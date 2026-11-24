"""Contraseñas, JWT y guardias RBAC."""
from datetime import timedelta

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from app import config
from app.database import UserDB, get_db, utcnow
from app.i18n import get_lang, msg

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def crear_token(username: str, rol: str) -> str:
    expire = utcnow() + timedelta(minutes=config.ACCESS_TOKEN_EXPIRE_MINUTES)
    return jwt.encode({"sub": username, "rol": rol, "exp": expire}, config.JWT_SECRET, algorithm=config.JWT_ALGORITHM)


def obtener_usuario_actual(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
    lang: str = Depends(get_lang),
):
    try:
        payload = jwt.decode(token, config.JWT_SECRET, algorithms=[config.JWT_ALGORITHM])
        username = payload.get("sub")
        if username is None:
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, msg("invalid_token", lang))
    except jwt.PyJWTError:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, msg("invalid_token", lang))

    user = db.query(UserDB).filter(UserDB.username == username).first()
    if not user or not user.is_active:
        raise HTTPException(status.HTTP_403_FORBIDDEN, msg("inactive_user", lang))
    return {"username": user.username, "rol": user.rol}


def requerir_admin(current_user: dict = Depends(obtener_usuario_actual), lang: str = Depends(get_lang)):
    if current_user["rol"] not in ("admin", "superadmin"):
        raise HTTPException(status.HTTP_403_FORBIDDEN, msg("forbidden_admin", lang))
    return current_user


def requerir_superadmin(current_user: dict = Depends(obtener_usuario_actual), lang: str = Depends(get_lang)):
    if current_user["rol"] != "superadmin":
        raise HTTPException(status.HTTP_403_FORBIDDEN, msg("forbidden_super", lang))
    return current_user
