"""Bitácora de seguridad (tabla logs_auditoria)."""
import logging

from sqlalchemy.orm import Session

from app.database import AuditLogDB

logger = logging.getLogger("sentinelops")


def registrar_auditoria(db: Session, actor: str, accion: str, detalle: str, estado: str = "OK") -> None:
    try:
        db.add(AuditLogDB(actor_username=actor, accion=accion, detalle=detalle, estado=estado))
        db.commit()
    except Exception as e:  # la auditoría nunca debe romper la petición principal
        db.rollback()
        logger.error("Error registrando auditoría: %s", e)
