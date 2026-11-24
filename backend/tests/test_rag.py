import pathlib

import pytest

TTL = pathlib.Path(__file__).resolve().parents[2] / "ontology" / "ontolog_a_devsecops_enriquecida_100_individuos.ttl"


def test_diagnostico_pasa_el_idioma_y_guarda_valor_canonico(client, monkeypatch):
    llamadas = []

    def falso(prompt, idioma="es"):
        llamadas.append(idioma)
        return {"componente": "Fuera de Dominio", "analisis_humano": "x", "comando_cli": "N/A", "confianza": "0%"}

    monkeypatch.setattr("app.routers.rag.consultar_ontologia_sparql", falso)
    tok = client.post("/api/v1/auth/login", json={"username": "operador", "password": "admin123", "turnstile_token": "token-ok"}).json()["access_token"]
    h = {"Authorization": f"Bearer {tok}"}
    en = client.post("/api/v1/rag/diagnose", json={"prompt": "pizza"}, headers={**h, "X-Lang": "en"}).json()
    es = client.post("/api/v1/rag/diagnose", json={"prompt": "pizza"}, headers=h).json()
    assert llamadas == ["en", "es"]
    assert en["componente"] == "Out of Domain" and es["componente"] == "Fuera de Dominio"
    # en la BD siempre queda el valor canónico en español
    tok_admin = client.post("/api/v1/auth/login", json={"username": "admin", "password": "admin123", "turnstile_token": "token-ok"}).json()["access_token"]
    stats = client.get("/api/v1/admin/stats", headers={"Authorization": f"Bearer {tok_admin}"}).json()
    assert {x["componente"] for x in stats["historial_chat"]} == {"Fuera de Dominio"}


def test_tokens_con_guion_generan_sparql_valido():
    from app.services.rag_service import construir_consulta_sparql, extraer_tokens_busqueda

    tokens = extraer_tokens_busqueda("¿Qué pasa con CVE-2024-3094?")
    assert "cve-2024-3094" in tokens
    consulta = construir_consulta_sparql(tokens)
    assert "\\-" not in consulta  # el escape que rompía SPARQL ya no aparece


def test_consulta_sparql_funciona_contra_la_ontologia_real():
    rdflib = pytest.importorskip("rdflib")
    from app.services.rag_service import construir_consulta_sparql

    g = rdflib.Graph()
    g.parse(TTL, format="turtle")
    filas = list(g.query(construir_consulta_sparql(["postgres"])))
    assert len(filas) >= 1
    assert len(list(g.query(construir_consulta_sparql(["pizza-hawaiana"])))) == 0
