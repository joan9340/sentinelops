"""Estadísticas, auditoría (admin/superadmin) y gestión de usuarios (superadmin)."""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database import AuditLogDB, ChatLogDB, UserDB, get_db
from app.i18n import get_lang, msg
from app.security import get_password_hash, requerir_admin, requerir_superadmin
from app.services.audit import registrar_auditoria

router = APIRouter(prefix="/api/v1/admin", tags=["Administración"])
ROLES = ("operador", "admin", "superadmin")


class CreateUserRequest(BaseModel):
    username: str
    password: str
    rol: str  # 'operador' | 'admin' | 'superadmin'


class UpdateRoleRequest(BaseModel):
    rol: str


def _fecha(ts) -> str:
    return ts.strftime("%Y-%m-%d %H:%M:%S") if ts else ""


# --- Estadísticas y auditoría ---
@router.get("/stats")
def obtener_estadisticas_y_auditoria(db: Session = Depends(get_db), current_user: dict = Depends(requerir_admin)):
    total = db.query(func.count(ChatLogDB.id)).scalar() or 0
    exitosas = db.query(func.count(ChatLogDB.id)).filter(ChatLogDB.confianza > 0).scalar() or 0

    top = (
        db.query(ChatLogDB.componente_detectado, func.count(ChatLogDB.id).label("total"))
        .group_by(ChatLogDB.componente_detectado)
        .order_by(func.count(ChatLogDB.id).desc())
        .limit(5)
        .all()
    )
    logs_chat = db.query(ChatLogDB).order_by(ChatLogDB.timestamp.desc()).limit(30).all()
    logs_sec = db.query(AuditLogDB).order_by(AuditLogDB.timestamp.desc()).limit(30).all()

    return {
        "kpis": {
            "total_consultas": total,
            "consultas_exitosas": exitosas,
            "consultas_rechazadas": total - exitosas,
            "tasa_precision": round((exitosas / total) * 100, 1) if total > 0 else 0,
        },
        "top_componentes": [{"componente": c[0] or "General", "total": c[1]} for c in top],
        "historial_chat": [
            {"id": l.id, "username": l.username, "prompt": l.prompt, "response": l.response,
             "componente": l.componente_detectado, "confianza": float(l.confianza or 0),
             "comando_cli": l.comando_cli, "verificado": l.verificado, "timestamp": _fecha(l.timestamp)}
            for l in logs_chat
        ],
        "bitacora_seguridad": [
            {"id": a.id, "actor": a.actor_username, "accion": a.accion, "detalle": a.detalle,
             "estado": a.estado, "timestamp": _fecha(a.timestamp)}
            for a in logs_sec
        ],
    }


@router.patch("/logs/{log_id}/verificar")
def verificar_diagnostico(
    log_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(requerir_admin),
    lang: str = Depends(get_lang),
):
    log = db.query(ChatLogDB).filter(ChatLogDB.id == log_id).first()
    if not log:
        raise HTTPException(404, msg("log_not_found", lang))

    log.verificado = not log.verificado
    db.commit()
    estado_txt = "verificado" if log.verificado else "desmarcado"
    registrar_auditoria(db, current_user["username"], "VERIFICAR_DIAGNOSTICO",
                        f"Diagnóstico #{log.id} ({log.componente_detectado}) marcado como {estado_txt}")
    return {"id": log.id, "verificado": log.verificado}


# --- Gestión de usuarios (solo superadmin) ---
@router.get("/usuarios")
def listar_usuarios(db: Session = Depends(get_db), current_user: dict = Depends(requerir_superadmin)):
    return [
        {"id": u.id, "username": u.username, "email": u.email, "rol": u.rol, "is_active": u.is_active}
        for u in db.query(UserDB).order_by(UserDB.id.asc()).all()
    ]


@router.post("/usuarios")
def crear_usuario(
    datos: CreateUserRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(requerir_superadmin),
    lang: str = Depends(get_lang),
):
    if datos.rol not in ROLES:
        raise HTTPException(400, msg("invalid_role", lang))
    if db.query(UserDB).filter(UserDB.username == datos.username).first():
        raise HTTPException(400, msg("username_taken", lang))

    nuevo = UserDB(username=datos.username, hashed_password=get_password_hash(datos.password),
                   rol=datos.rol, is_active=True)
    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)
    registrar_auditoria(db, current_user["username"], "CREAR_USUARIO",
                        f"Creó el usuario '{nuevo.username}' con rol [{nuevo.rol}]")
    return {"id": nuevo.id, "username": nuevo.username, "rol": nuevo.rol, "is_active": nuevo.is_active}


@router.patch("/usuarios/{user_id}/rol")
def cambiar_rol_usuario(
    user_id: int,
    datos: UpdateRoleRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(requerir_superadmin),
    lang: str = Depends(get_lang),
):
    if datos.rol not in ROLES:
        raise HTTPException(400, msg("invalid_role", lang))
    user = db.query(UserDB).filter(UserDB.id == user_id).first()
    if not user:
        raise HTTPException(404, msg("user_not_found", lang))

    anterior = user.rol
    user.rol = datos.rol
    db.commit()
    registrar_auditoria(db, current_user["username"], "CAMBIO_ROL",
                        f"Cambió el rol de '{user.username}' de [{anterior}] a [{datos.rol}]", "ALERTA")
    return {"id": user.id, "username": user.username, "rol": user.rol}


@router.patch("/usuarios/{user_id}/estado")
def alternar_estado_usuario(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(requerir_superadmin),
    lang: str = Depends(get_lang),
):
    user = db.query(UserDB).filter(UserDB.id == user_id).first()
    if not user:
        raise HTTPException(404, msg("user_not_found", lang))
    if user.username == current_user["username"]:
        raise HTTPException(400, msg("cannot_suspend_self", lang))

    user.is_active = not user.is_active
    db.commit()
    registrar_auditoria(
        db, current_user["username"],
        "ACTIVAR_USUARIO" if user.is_active else "SUSPENDER_USUARIO",
        f"Estado de cuenta '{user.username}' actualizado a {'Activo' if user.is_active else 'Suspendido'}",
        "OK" if user.is_active else "ALERTA",
    )
    return {"id": user.id, "username": user.username, "is_active": user.is_active}
