import os
from SPARQLWrapper import SPARQLWrapper, JSON
from groq import Groq  # Importamos el cliente oficial de Groq

# ==========================================
# 1. Configuración de Conexión a Jena Fuseki
# ==========================================
FUSEKI_ENDPOINT = "http://localhost:3030/Sistema_DevSecOps/sparql"

def consultar_grafo_incidente(nombre_incidente_parcial: str) -> dict:
    """
    Conecta a Apache Jena Fuseki usando SPARQLWrapper y extrae 
    el incidente, componente afectado, gravedad y comando CLI.
    """
    sparql = SPARQLWrapper(FUSEKI_ENDPOINT)
    
    query = f"""
    PREFIX : <http://www.semanticweb.org/munoz/ontologies/2026/8/untitled-ontology-4/>
    
    SELECT ?incidente ?componente ?gravedad ?comando
    WHERE {{
      ?incidente :impactaA ?componente ;
                 :nivelGravedad ?gravedad ;
                 :seResuelveCon ?accion .
      ?accion :comandoCLI ?comando .
      
      FILTER(CONTAINS(LCASE(STR(?incidente)), LCASE("{nombre_incidente_parcial}")))
    }}
    LIMIT 1
    """
    
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    
    try:
        results = sparql.query().convert()
        bindings = results["results"]["bindings"]
        
        if not bindings:
            return None
        
        row = bindings[0]
        contexto = {
            "incidente": row["incidente"]["value"].split("/")[-1],
            "componente": row["componente"]["value"].split("/")[-1],
            "gravedad": row["gravedad"]["value"],
            "comando": row["comando"]["value"]
        }
        return contexto
        
    except Exception as e:
        print(f"Error al consultar Jena Fuseki: {e}")
        return None

# ==========================================
# 2. Plantilla de Prompt & Inyección GraphRAG
# ==========================================
def construir_prompt_enriquecido(contexto_grafo: dict, consulta_usuario: str) -> str:
    """
    Diseña la plantilla de prompt inyectando el conocimiento estructurado 
    del grafo SPARQL antes de enviarlo al LLM.
    """
    prompt = f"""
    [CONTEXTO DEL GRAFO DE CONOCIMIENTO SEMÁNTICO (DevSecOps)]
    - Incidente Detectado: {contexto_grafo['incidente']}
    - Componente Afectado: {contexto_grafo['componente']}
    - Nivel de Gravedad: {contexto_grafo['gravedad']}
    - Comando CLI de Solución Oficial: {contexto_grafo['comando']}

    [INSTRUCCIÓN]
    Eres un asistente experto en DevSecOps y respuesta a incidentes. Utilizando estrictamente el contexto del grafo anterior, responde al usuario. Explica brevemente la falla y proporciona el comando CLI exacto formateado en un bloque de código para que el operador pueda copiarlo y ejecutarlo.

    [CONSULTA DEL OPERADOR]
    {consulta_usuario}
    """
    return prompt

# ==========================================
# 3. Integración con la API Oficial de Groq
# ==========================================
def generar_diagnostico_con_groq(prompt_enriquecido: str) -> str:
    """
    Envía el prompt enriquecido a la API de Groq usando su SDK oficial.
    """
    GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
    
    # Inicializar cliente oficial de Groq
    client = Groq(api_key=GROQ_API_KEY)
    
    try:
        completion = client.chat.completions.create(
            model="qwen/qwen3.8-27b",
            messages=[
                {"role": "system", "content": "Eres un asistente técnico de DevSecOps especializado en diagnóstico basado en grafos semánticos."},
                {"role": "user", "content": prompt_enriquecido}
            ],
            temperature=0.1,
            max_tokens=500
        )
        return completion.choices[0].message.content
    except Exception as e:
        return f"Error al comunicarse con la API de Groq: {e}"

# ==========================================
# FLUJO DE PRUEBA (E2E del Motor GraphRAG)
# ==========================================
if __name__ == "__main__":
    termino_busqueda = "Timeout"
    print(f"[*] Consultando grafo para el incidente: '{termino_busqueda}'...")
    
    datos_grafo = consultar_grafo_incidente(termino_busqueda)
    
    if datos_grafo:
        print("[+] Grafo recuperado con éxito:", datos_grafo)
        
        pregunta = "¿Qué debo hacer para solucionar este problema en el servidor?"
        prompt_final = construir_prompt_enriquecido(datos_grafo, pregunta)
        
        print("\n[*] Enviando Prompt Enriquecido a Groq (Llama 3)...")
        respuesta_ia = generar_diagnostico_con_groq(prompt_final)
        
        print("\n=== RESPUESTA DEL AGENTE GRAPHRAG ===")
        print(respuesta_ia)
    else:
        print("[-] No se encontró información en el grafo para ese incidente.")