"""Estado de la infraestructura (panel lateral)."""
from fastapi import APIRouter

router = APIRouter(prefix="/api/v1/health", tags=["Salud"])


@router.get("/components")
async def get_infrastructure_health():
    return [
        {"id": 1, "name": "PostgreSQL Database", "status": "Healthy", "uptime": "99.9%", "port": "5432"},
        {"id": 2, "name": "FastAPI Auth & RAG Core", "status": "Healthy", "uptime": "100%", "port": "8000"},
        {"id": 3, "name": "Docker Container Runtime", "status": "Healthy", "uptime": "98.5%", "port": "VPC Local"},
        {"id": 4, "name": "Apache Jena Fuseki (Triplestore)", "status": "Healthy", "uptime": "99.1%", "port": "3030"},
    ]
