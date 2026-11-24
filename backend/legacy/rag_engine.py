import os
from fastapi import FastAPI, Request, HTTPException, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.exceptions import InvalidSignature

# Importamos las funciones desarrolladas en generador_grafo.py
from generador_grafo import (
    consultar_grafo_incidente,
    construir_prompt_enriquecido,
    generar_diagnostico_con_groq
)

app = FastAPI(
    title="Sistema DevSecOps GraphRAG API",
    version="1.0.0",
    description="API para diagnóstico de incidentes basado en grafos semánticos y Groq"
)

# ==========================================
# 1. Configuración de Clave Pública RSA
# ==========================================
PUBLIC_KEY_PATH = "public_key.pem"

def cargar_clave_publica():
    """Carga la clave pública RSA utilizada para validar la firma de la licencia."""
    if not os.path.exists(PUBLIC_KEY_PATH):
        return None
    with open(PUBLIC_KEY_PATH, "rb") as key_file:
        return serialization.load_pem_public_key(key_file.read())

PUBLIC_KEY = cargar_clave_publica()

# ==========================================
# 2. Middleware de Validación de Firma RSA
# ==========================================
@app.middleware("http")
async def validar_firma_licencia_middleware(request: Request, call_next):
    """
    Middleware que intercepta peticiones HTTP y valida la firma criptográfica RSA
    proporcionada en los encabezados HTTP (X-License-Data y X-License-Signature).
    """
  
## Rutas públicas permitidas sin licencia
#Sin llave RSA
    rutas_publicas = ["/docs", "/openapi.json", "/redoc", "/health", "/api/v1/rag/diagnose"]
#Con Proteccion llave RSA
#rutas_publicas = ["/docs", "/openapi.json", "/redoc", "/health"]
    if request.url.path in rutas_publicas:
        return await call_next(request)

    # Obtener encabezados de licencia y firma
    license_data = request.headers.get("X-License-Data")
    license_signature_hex = request.headers.get("X-License-Signature")

    if not license_data or not license_signature_hex:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"detail": "Acceso denegado: Encabezados de licencia RSA faltantes (X-License-Data, X-License-Signature)."}
        )

    try:
        # Convertir la firma desde hexadecimal a bytes
        signature_bytes = bytes.fromhex(license_signature_hex)
        
        # Validar la firma RSA si existe la clave pública cargada
        if PUBLIC_KEY:
            PUBLIC_KEY.verify(
                signature_bytes,
                license_data.encode("utf-8"),
                padding.PKCS1v15(),
                hashes.SHA256()
            )
    except InvalidSignature:
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content={"detail": "Licencia inválida: La firma criptográfica RSA no coincide o fue alterada."}
        )
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"detail": f"Error procesando la firma de la licencia: {str(e)}"}
        )

    response = await call_next(request)
    return response

# ==========================================
# 3. Modelos de Datos (Pydantic)
# ==========================================
class DiagnosticoRequest(BaseModel):
    incidente: str
    pregunta: str = "¿Qué debo hacer para solucionar este problema en el servidor?"

class DiagnosticoResponse(BaseModel):
    incidente: str
    contexto_grafo: dict
    diagnostico: str

# ==========================================
# 4. Endpoints de la API
# ==========================================
@app.get("/health")
def health_check():
    return {"status": "ok", "service": "DevSecOps GraphRAG API"}

@app.post("/api/v1/rag/diagnose", response_model=DiagnosticoResponse)
def diagnosticar_incidente(payload: DiagnosticoRequest):
    """
    Endpoint RAG real:
    1. Consulta Jena Fuseki recuperando el contexto semántico.
    2. Construye el prompt enriquecido.
    3. Invoca la API de Groq para obtener la solución técnica.
    """
    try:
        # Paso 1: Consultar grafo semántico en Apache Jena Fuseki
        contexto_grafo = consultar_grafo_incidente(payload.incidente)
        
        if not contexto_grafo:
            raise HTTPException(
                status_code=404,
                detail=f"No se encontró información semántica en el grafo para el incidente '{payload.incidente}'."
            )

        # Paso 2: Construir prompt enriquecido con el conocimiento recuperado
        prompt_enriquecido = construir_prompt_enriquecido(contexto_grafo, payload.pregunta)

        # Paso 3: Generar respuesta con el LLM vía Groq
        diagnostico_llm = generar_diagnostico_con_groq(prompt_enriquecido)

        return DiagnosticoResponse(
            incidente=payload.incidente,
            contexto_grafo=contexto_grafo,
            diagnostico=diagnostico_llm
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error interno en el servidor GraphRAG: {str(e)}"
        )