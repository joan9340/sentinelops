import os
import sys

# Base de datos temporal en SQLite: las pruebas no necesitan PostgreSQL ni Docker.
os.environ["DATABASE_URL"] = "sqlite:///./test_sentinelops.db"
os.environ["JWT_SECRET"] = "secreto-de-pruebas"
os.environ["TURNSTILE_SECRET_KEY"] = "1x0000000000000000000000000000000AA"
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import pytest
from fastapi.testclient import TestClient


@pytest.fixture()
def client(monkeypatch):
    from app.database import Base, engine
    from app.main import app

    Base.metadata.drop_all(bind=engine)
    enviados = []
    # Turnstile simulado: solo acepta el token "token-ok"
    monkeypatch.setattr("app.routers.auth.verificar_turnstile",
                        lambda token, ip=None: (token == "token-ok", "ok" if token == "token-ok" else "invalid-input-response"))
    # Correo simulado: guarda (destino, usuario, código, idioma)
    monkeypatch.setattr("app.routers.auth.enviar_codigo_recuperacion",
                        lambda destino, usuario, codigo, lang="es": enviados.append((destino, usuario, codigo, lang)) or True)
    with TestClient(app) as c:
        c.enviados = enviados
        yield c
    Base.metadata.drop_all(bind=engine)
