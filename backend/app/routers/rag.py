"""Diagnóstico GraphRAG (todos los roles activos)."""
import logging

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import ChatLogDB, get_db
from app.i18n import get_lang
from app.security import obtener_usuario_actual
from app.services.rag_service import consultar_ontologia_sparql

logger = logging.getLogger("sentinelops")
router = APIRouter(prefix="/api/v1/rag", tags=["GraphRAG"])

# El valor canónico (español) se guarda en la BD; para la pantalla se traduce.
COMPONENTE_EN = {"Fuera de Dominio": "Out of Domain"}


class DiagnosticQuery(BaseModel):
    prompt: str


@router.post("/diagnose")
def get_diagnosis(
    query: DiagnosticQuery,
    db: Session = Depends(get_db),
    current_user: dict = Depends(obtener_usuario_actual),
    lang: str = Depends(get_lang),
):
    diagnostico = consultar_ontologia_sparql(query.prompt, lang)

    componente = diagnostico.get("componente", "General")
    analisis = diagnostico.get("analisis_humano", "")
    comando_cli = diagnostico.get("comando_cli", "")

    try:
        conf_num = float(str(diagnostico.get("confianza", 0)).replace("%", "").strip())
    except ValueError:
        conf_num = 0.0

    try:
        db.add(ChatLogDB(username=current_user["username"], prompt=query.prompt, response=analisis,
                         componente_detectado=componente, confianza=conf_num, comando_cli=comando_cli, verificado=False))
        db.commit()
    except Exception as e:
        db.rollback()
        logger.error("Error guardando log_chat: %s", e)

    visible = COMPONENTE_EN.get(componente, componente) if lang == "en" else componente
    prefijo = "Diagnosis" if lang == "en" else "Diagnóstico"
    return {
        "status": "success",
        "incident": f"{prefijo}: {visible}",
        "componente": visible,
        "confidence": f"{int(conf_num)}%",
        "analysis": analisis,
        "recommended_cli": comando_cli,
    }
