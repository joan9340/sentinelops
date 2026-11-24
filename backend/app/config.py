"""Configuración central de SentinelOps.

Todo se lee desde variables de entorno (archivo .env en la raíz del proyecto,
cargado por docker compose). Ningún secreto debe escribirse en el código.
"""
import logging
import os
import secrets

logger = logging.getLogger("sentinelops")


def _env(name: str, default: str = "") -> str:
    return os.getenv(name, default).strip()


def _env_bool(name: str, default: bool = False) -> bool:
    return _env(name, str(default)).lower() in ("1", "true", "yes", "si", "sí")


# --- Base de datos ---
_db_url = _env("DATABASE_URL", "postgresql+psycopg://devuser:devpassword123@postgres_db:5432/devsecops_logs")
if _db_url.startswith("postgresql://"):
    _db_url = _db_url.replace("postgresql://", "postgresql+psycopg://", 1)
DATABASE_URL = _db_url

# --- JWT ---
JWT_SECRET = _env("JWT_SECRET")
if not JWT_SECRET:
    JWT_SECRET = secrets.token_urlsafe(48)
    logger.warning("JWT_SECRET no definido: se generó uno temporal (las sesiones se pierden al reiniciar).")
JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(_env("ACCESS_TOKEN_EXPIRE_MINUTES", "120"))

# --- CORS ---
CORS_ORIGINS = [o.strip() for o in _env("CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173").split(",") if o.strip()]

# --- Cloudflare Turnstile (robot autenticador) ---
TURNSTILE_SECRET_KEY = _env("TURNSTILE_SECRET_KEY")
TURNSTILE_VERIFY_URL = "https://challenges.cloudflare.com/turnstile/v0/siteverify"
TURNSTILE_ENABLED = bool(TURNSTILE_SECRET_KEY)
if not TURNSTILE_ENABLED:
    logger.warning("TURNSTILE_SECRET_KEY no definido: la verificación anti-robots está DESACTIVADA.")

# --- Correo (Gmail con contraseña de aplicación) ---
SMTP_HOST = _env("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(_env("SMTP_PORT", "587"))
SMTP_USER = _env("SMTP_USER")
SMTP_PASSWORD = _env("SMTP_PASSWORD").replace(" ", "")  # Google la muestra con espacios
SMTP_FROM = _env("SMTP_FROM") or SMTP_USER
SMTP_FROM_NAME = _env("SMTP_FROM_NAME", "SentinelOps")

# --- Recuperación de contraseña ---
RESET_CODE_MINUTES = int(_env("RESET_CODE_MINUTES", "15"))
RESET_MAX_ATTEMPTS = int(_env("RESET_MAX_ATTEMPTS", "5"))
RESET_MAX_REQUESTS_PER_HOUR = int(_env("RESET_MAX_REQUESTS_PER_HOUR", "3"))

# --- Cuentas de demostración ---
CREATE_DEFAULT_USERS = _env_bool("CREATE_DEFAULT_USERS", True)
DEFAULT_USERS_PASSWORD = _env("DEFAULT_USERS_PASSWORD", "admin123")

# --- Motor GraphRAG ---
FUSEKI_URL = _env("FUSEKI_URL", "http://fuseki:3030/ds/query")
GROQ_API_KEY = _env("GROQ_API_KEY")
GROQ_MODEL = _env("GROQ_MODEL", "openai/gpt-oss-120b")
