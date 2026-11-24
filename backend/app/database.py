"""Conexión a PostgreSQL y modelos SQLAlchemy."""
import time
from datetime import datetime, timezone

from sqlalchemy import (
    Boolean, Column, DateTime, ForeignKey, Integer, Numeric, String, Text, create_engine, text,
)
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import declarative_base, sessionmaker

from app import config


def utcnow() -> datetime:
    """UTC "naive" (sin tzinfo), consistente con lo que ya guardaba el proyecto."""
    return datetime.now(timezone.utc).replace(tzinfo=None)


_is_sqlite = config.DATABASE_URL.startswith("sqlite")
engine = create_engine(
    config.DATABASE_URL,
    connect_args={"check_same_thread": False} if _is_sqlite else {},
    pool_pre_ping=not _is_sqlite,
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class UserDB(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=True)  # nuevo: registro y recuperación
    hashed_password = Column(String, nullable=False)
    rol = Column(String(20), nullable=False, default="operador")  # 'operador' | 'admin' | 'superadmin'
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=utcnow)


class PasswordResetDB(Base):
    """Códigos de un solo uso para recuperar contraseña (se guarda solo el hash)."""
    __tablename__ = "password_resets"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    code_hash = Column(String(64), nullable=False)
    expires_at = Column(DateTime, nullable=False)
    attempts = Column(Integer, default=0, nullable=False)
    used = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=utcnow, index=True)


class ChatLogDB(Base):
    __tablename__ = "logs_chat"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, index=True)
    prompt = Column(Text, nullable=False)
    response = Column(Text, nullable=False)
    componente_detectado = Column(String(100), default="General")
    confianza = Column(Numeric(5, 2), default=0.00)
    comando_cli = Column(Text, nullable=True)
    verificado = Column(Boolean, default=False)
    timestamp = Column(DateTime, default=utcnow)


class AuditLogDB(Base):
    __tablename__ = "logs_auditoria"

    id = Column(Integer, primary_key=True, index=True)
    actor_username = Column(String(120), nullable=False)
    accion = Column(String(80), nullable=False)
    detalle = Column(Text, nullable=True)
    estado = Column(String(20), nullable=False, default="OK")  # 'OK' | 'ALERTA'
    timestamp = Column(DateTime, default=utcnow)


def esperar_base_de_datos(intentos: int = 30, pausa: float = 2.0) -> None:
    """PostgreSQL puede tardar en aceptar conexiones al levantar Docker: reintenta en vez de caerse."""
    for n in range(1, intentos + 1):
        try:
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            return
        except OperationalError:
            if n == intentos:
                raise
            time.sleep(pausa)


def run_light_migrations() -> None:
    """Agrega columnas nuevas a bases de datos ya existentes (create_all no altera tablas)."""
    if engine.dialect.name != "postgresql":
        return
    with engine.begin() as conn:
        conn.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS email VARCHAR(255)"))
        conn.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS created_at TIMESTAMP"))
        conn.execute(text("CREATE UNIQUE INDEX IF NOT EXISTS ix_users_email ON users (email)"))


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
