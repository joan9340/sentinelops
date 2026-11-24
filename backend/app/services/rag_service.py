"""Motor GraphRAG: consulta la ontología en Fuseki y sintetiza la respuesta con Groq.

El parámetro `idioma` ('es' | 'en') solo cambia el idioma del texto redactado;
la lógica y los valores canónicos guardados en la base de datos no cambian.
"""
import logging
import re

from groq import Groq
from SPARQLWrapper import JSON, SPARQLWrapper

from app import config

logger = logging.getLogger("sentinelops")

FUSEKI_URL = config.FUSEKI_URL
GROQ_MODEL = config.GROQ_MODEL
client_groq = Groq(api_key=config.GROQ_API_KEY) if config.GROQ_API_KEY else None

# Stopwords en español/inglés para aislar términos técnicos del prompt sin listas de dominio estáticas
STOPWORDS = {
    "el", "la", "los", "las", "un", "una", "unos", "unas", "de", "del", "al",
    "a", "en", "con", "por", "para", "sin", "sobre", "entre", "hasta", "desde",
    "que", "cual", "quien", "como", "cuando", "donde", "porque", "por qué",
    "es", "son", "esta", "estan", "está", "están", "hay", "tiene", "tienen",
    "mi", "tu", "su", "nuestro", "me", "te", "se", "nos", "lo", "le", "les",
    "y", "o", "pero", "si", "no", "mas", "más", "muy", "ya", "hola", "favor",
    "ayuda", "necesito", "puedes", "decir", "dime", "revisar", "problema", "falla",
    # inglés
    "the", "and", "for", "with", "that", "this", "what", "how", "why", "can", "you",
    "please", "help", "need", "have", "has", "are", "was", "not", "hello", "hey", "problem",
}

MSG = {
    "es": {
        "sin_tokens_inc": "Consulta sin términos técnicos reconocibles",
        "sin_tokens_txt": "No se detectaron términos técnicos asociados a la ontología activa en Fuseki.",
        "fuseki_inc": "Triplestore no disponible",
        "fuseki_txt": "No fue posible establecer conexión con el endpoint SPARQL de Apache Jena Fuseki en el puerto 3030.",
        "fuera_inc": "Entidad no modelada en la ontología activa",
        "fuera_txt": ("La consulta no corresponde a ningún componente, falla o vulnerabilidad registrada "
                      "en la ontología actualmente cargada en Apache Jena Fuseki."),
        "fuera_cli": "N/A - Consulta fuera del dominio ontológico activo",
        "fallback_sin_llm": ("Diagnóstico ontológico sobre {componente}: se detectó '{incidente}' "
                             "(gravedad {gravedad}). Ejecuta el comando CLI recuperado del grafo para remediarlo."),
        "fallback_error_llm": ("Se identificó '{incidente}' afectando a {componente}. "
                               "Aplica la acción '{accion}' mediante el comando CLI recuperado."),
        "idioma_llm": "Redacta en español técnico, claro y directo en máximo 3 oraciones.",
    },
    "en": {
        "sin_tokens_inc": "Query without recognizable technical terms",
        "sin_tokens_txt": "No technical terms associated with the active ontology in Fuseki were detected.",
        "fuseki_inc": "Triplestore unavailable",
        "fuseki_txt": "Could not connect to the Apache Jena Fuseki SPARQL endpoint on port 3030.",
        "fuera_inc": "Entity not modeled in the active ontology",
        "fuera_txt": ("The query does not match any component, failure or vulnerability registered "
                      "in the ontology currently loaded in Apache Jena Fuseki."),
        "fuera_cli": "N/A - Query outside the active ontology domain",
        "fallback_sin_llm": ("Ontology diagnosis for {componente}: '{incidente}' was detected "
                             "(severity {gravedad}). Run the CLI command retrieved from the graph to remediate it."),
        "fallback_error_llm": ("'{incidente}' was identified affecting {componente}. "
                               "Apply the action '{accion}' using the retrieved CLI command."),
        "idioma_llm": "Write in clear, direct technical English in at most 3 sentences.",
    },
}


def extraer_tokens_busqueda(prompt: str) -> list[str]:
    limpio = re.sub(r"[^a-zA-Z0-9áéíóúÁÉÍÓÚñÑ_-]+", " ", prompt.lower())
    tokens = [t.strip() for t in limpio.split() if len(t.strip()) >= 3 and t.strip() not in STOPWORDS]
    return list(dict.fromkeys(tokens))  # sin duplicados, conservando el orden


def _nombre_local(uri: str) -> str:
    if not uri:
        return "Desconocido"
    if "#" in uri:
        return uri.split("#")[-1].replace("_", " ")
    return uri.rstrip("/").split("/")[-1].replace("_", " ")


def generar_respuesta_humana_llama3(prompt_usuario: str, evidencia: dict, idioma: str = "es") -> str:
    m = MSG[idioma]
    if not client_groq:
        return m["fallback_sin_llm"].format(
            componente=evidencia["componente"], incidente=evidencia["incidente"],
            gravedad=evidencia.get("gravedad", "N/A"),
        )

    system_prompt = (
        "Eres SentinelOps AI, un ingeniero senior especialista en diagnóstico sobre grafos de conocimiento RDF. "
        "REGLA ESTRICTA: Responde ÚNICAMENTE utilizando los hechos exactos proporcionados en la sección 'EVIDENCIA DEL GRAFO'. "
        "Tienes TERMINANTEMENTE PROHIBIDO inventar comandos CLI, rutas, parámetros, direcciones IP o causas que no aparezcan "
        "en la evidencia. Si mencionas el comando de remediación, debe ser exactamente el entregado en la evidencia. "
        + m["idioma_llm"]
    )
    user_content = f"""
Consulta del operador: "{prompt_usuario}"

EVIDENCIA DEL GRAFO (Apache Jena Fuseki):
- Componente afectado: {evidencia.get('componente')}
- Incidente o vulnerabilidad detectada: {evidencia.get('incidente')}
- Nivel de gravedad: {evidencia.get('gravedad', 'No especificado')}
- Código CVE (si aplica): {evidencia.get('cve', 'N/A')}
- Acción de remediación: {evidencia.get('accion')}
- Comando CLI exacto del grafo: {evidencia.get('comando_cli')}

Explica brevemente el diagnóstico y la acción recomendada usando solo esta evidencia.
"""
    try:
        completion = client_groq.chat.completions.create(
            model=GROQ_MODEL,
            messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": user_content}],
            temperature=0.1,
            max_tokens=220,
        )
        return completion.choices[0].message.content.strip()
    except Exception as e:
        logger.error("Error al invocar Groq (%s): %s", GROQ_MODEL, e)
        return m["fallback_error_llm"].format(
            incidente=evidencia["incidente"], componente=evidencia["componente"], accion=evidencia["accion"],
        )


def construir_consulta_sparql(tokens: list[str]) -> str:
    # Los tokens ya vienen saneados ([a-z0-9áéíóúñ_-]); en una regex el guion fuera de [] es literal,
    # por eso NO se usa re.escape (que convertía '-' en '\-', inválido dentro de un literal SPARQL).
    regex_tokens = "|".join(tokens)
    return f"""
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX owl: <http://www.w3.org/2002/07/owl#>

    SELECT DISTINCT ?incidente ?componente ?accion ?comandoCLI ?gravedad ?cve
    WHERE {{
      ?incidente ?predImpacto ?componente ;
                 ?predResolucion ?accion .
      ?accion ?predCLI ?comandoCLI .

      FILTER(REGEX(STR(?predImpacto), "(impactaA|afectaA)$", "i"))
      FILTER(REGEX(STR(?predResolucion), "(seResuelveCon|tieneSolucion)$", "i"))
      FILTER(REGEX(STR(?predCLI), "comandoCLI$", "i"))

      OPTIONAL {{ ?incidente ?predGrav ?gravedad . FILTER(REGEX(STR(?predGrav), "nivelGravedad$", "i")) }}
      OPTIONAL {{ ?incidente ?predCVE ?cve . FILTER(REGEX(STR(?predCVE), "codigoCVE$", "i")) }}
      OPTIONAL {{ ?incidente rdfs:label ?labelInc . }}
      OPTIONAL {{ ?componente rdfs:label ?labelComp . }}

      BIND(
        CONCAT(
          REPLACE(STR(?incidente), "^.*[/#]", ""), " ",
          REPLACE(STR(?componente), "^.*[/#]", ""), " ",
          COALESCE(STR(?labelInc), ""), " ",
          COALESCE(STR(?labelComp), ""), " ",
          COALESCE(STR(?cve), "")
        ) AS ?textoBuscable
      )

      FILTER(REGEX(?textoBuscable, "({regex_tokens})", "i"))
    }}
    LIMIT 1
    """


def consultar_ontologia_sparql(prompt_usuario: str, idioma: str = "es") -> dict:
    """Motor GraphRAG desacoplado de dominio. `componente` siempre se devuelve en su valor canónico (español)."""
    idioma = idioma if idioma in MSG else "es"
    m = MSG[idioma]

    tokens = extraer_tokens_busqueda(prompt_usuario)
    if not tokens:
        return {"encontrado": False, "componente": "Fuera de Dominio", "incidente": m["sin_tokens_inc"],
                "analisis_humano": m["sin_tokens_txt"], "comando_cli": "N/A", "confianza": "0%"}

    sparql = SPARQLWrapper(FUSEKI_URL)
    sparql.setQuery(construir_consulta_sparql(tokens))
    sparql.setReturnFormat(JSON)

    try:
        results = sparql.query().convert()
        bindings = results.get("results", {}).get("bindings", [])
    except Exception as e:
        logger.error("Error conectando con Apache Jena Fuseki (%s): %s", FUSEKI_URL, e)
        return {"encontrado": False, "componente": "Apache Jena Fuseki", "incidente": m["fuseki_inc"],
                "analisis_humano": m["fuseki_txt"], "comando_cli": "docker compose up -d fuseki", "confianza": "0%"}

    if not bindings:  # rechazo estricto fuera de dominio (0%)
        return {"encontrado": False, "componente": "Fuera de Dominio", "incidente": m["fuera_inc"],
                "analisis_humano": m["fuera_txt"], "comando_cli": m["fuera_cli"], "confianza": "0%"}

    res = bindings[0]
    evidencia = {
        "encontrado": True,
        "componente": _nombre_local(res.get("componente", {}).get("value", "")),
        "incidente": _nombre_local(res.get("incidente", {}).get("value", "")),
        "accion": _nombre_local(res.get("accion", {}).get("value", "")),
        "comando_cli": res.get("comandoCLI", {}).get("value", ""),
        "gravedad": res.get("gravedad", {}).get("value", "ALTO"),
        "cve": res.get("cve", {}).get("value", "N/A"),
        "confianza": "96%",
    }
    evidencia["analisis_humano"] = generar_respuesta_humana_llama3(prompt_usuario, evidencia, idioma)
    return evidencia
