"""Punto de entrada de la API SentinelOps."""
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app import config
from app.database import Base, SessionLocal, UserDB, engine, esperar_base_de_datos, run_light_migrations
from app.routers import admin, auth, health, rag
from app.security import get_password_hash

logging.basicConfig(level=logging.INFO)


def crear_usuarios_base() -> None:
    """Cuentas de demostración (se pueden desactivar con CREATE_DEFAULT_USERS=false)."""
    if not config.CREATE_DEFAULT_USERS:
        return
    cuentas = [("admin", "superadmin"), ("auditor", "admin"), ("operador", "operador")]
    db = SessionLocal()
    try:
        for username, rol in cuentas:
            if not db.query(UserDB).filter(UserDB.username == username).first():
                db.add(UserDB(username=username, hashed_password=get_password_hash(config.DEFAULT_USERS_PASSWORD),
                              rol=rol, is_active=True))
        db.commit()
    finally:
        db.close()


@asynccontextmanager
async def lifespan(app: FastAPI):
    esperar_base_de_datos()
    Base.metadata.create_all(bind=engine)
    run_light_migrations()
    crear_usuarios_base()
    yield


app = FastAPI(title="SentinelOps DevSecOps API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=config.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

for router in (health.router, auth.router, rag.router, admin.router):
    app.include_router(router)
