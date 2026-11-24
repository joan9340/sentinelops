# SentinelOps — Diagnóstico semántico DevSecOps (GraphRAG)

Plataforma que recibe un síntoma técnico, lo busca en una **ontología RDF** (Apache Jena Fuseki), y un LLM (Groq)
redacta el diagnóstico usando **solo** la evidencia del grafo, junto con el comando CLI de remediación.

## Estructura del proyecto

```
SentinelOps/
├── docker-compose.yml        Orquesta PostgreSQL, Fuseki, backend, frontend y el cargador de la ontología
├── .env.example              Plantilla de configuración (copiar a .env)
├── backend/                  API FastAPI
│   ├── Dockerfile · requirements.txt
│   ├── app/
│   │   ├── main.py           Arranque, CORS y registro de routers
│   │   ├── config.py         Variables de entorno
│   │   ├── database.py       Modelos SQLAlchemy (users, password_resets, logs_chat, logs_auditoria)
│   │   ├── security.py       JWT, contraseñas y roles (RBAC)
│   │   ├── i18n.py           Mensajes de la API en español / inglés
│   │   ├── routers/          auth · rag · admin · health
│   │   └── services/         rag_service · turnstile · email_service · audit
│   ├── tests/                Pruebas automáticas (pytest)
│   └── legacy/               Scripts antiguos que ya no usa la app (RSA, generador de grafo)
├── frontend/                 React + Vite
│   └── src/
│       ├── pages/            AuthPage · DashboardPage · ConsolePage · AuditPage · UsersPage
│       ├── components/       SettingsBar · TurnstileWidget · InfraSidebar · Icons
│       ├── context/          SettingsContext (tema, letra, idioma) · AuthContext (sesión)
│       ├── i18n/             es.js · en.js
│       ├── services/         api.js · useApiData.js
│       └── styles/           theme.css (3 temas) · styles.js
├── ontology/                 Ontología (.ttl)
└── docs/                     consultas/ (SPARQL) · maquetas/ (HTML de diseño) · capturas/
```

## Puesta en marcha

1. `cp .env.example .env` y completa al menos: `JWT_SECRET`, `GROQ_API_KEY`, `SMTP_USER` y `SMTP_PASSWORD`.
2. `docker compose up -d --build`
3. Abre **http://localhost:5173** (aplicación) y **http://localhost:8000/docs** (API).

El servicio `fuseki_loader` carga automáticamente `ontology/*.ttl` en el dataset `ds`. Si falla, súbelo a mano en
http://localhost:3030 → dataset `ds` → *upload files*, o con:
`curl -u admin:TU_CLAVE -X POST -H "Content-Type: text/turtle" --data-binary @ontology/ontolog_a_devsecops_enriquecida_100_individuos.ttl http://localhost:3030/ds/data`

Cuentas de demostración (contraseña = `DEFAULT_USERS_PASSWORD`, por defecto `admin123`): `admin` (superadmin), `auditor` (admin), `operador`.

## Funciones nuevas

| Mejora | Dónde |
|---|---|
| **3 temas de color** (blanco, negro, azul) con contraste WCAG AA ≥ 5,2:1 | `frontend/src/styles/theme.css` |
| **Registrar cuenta** desde el login (siempre rol *operador*) | `AuthPage.jsx` · `POST /api/v1/auth/register` |
| **Robot autenticador** Cloudflare Turnstile en login, registro y recuperación (verificado en el servidor) | `TurnstileWidget.jsx` · `services/turnstile.py` |
| **Recuperar contraseña por correo**: código de 6 dígitos, vence en 15 min, un solo uso, máx. 5 intentos y 3 solicitudes/hora | `POST /auth/forgot-password` y `/auth/reset-password` |
| **Tamaño de letra** (85 %–150 %) con íconos A+ / A− / restablecer | `SettingsBar.jsx` (barra fija a la derecha) |
| **Idioma español / inglés** (interfaz, mensajes de la API, correo y respuesta del diagnóstico) | `i18n/` · cabecera `X-Lang` |
| **Carpetas reorganizadas** (backend, frontend, ontology, docs) | este árbol |

Las preferencias (tema, letra, idioma) se guardan en el navegador.

## Configurar Cloudflare Turnstile
Las claves de `.env.example` son de **prueba** (siempre aprueban). Para usar el verificador real: Cloudflare Dashboard → *Turnstile* →
*Add widget* → agrega el hostname `localhost` → copia la *Site key* a `TURNSTILE_SITE_KEY` y la *Secret key* a `TURNSTILE_SECRET_KEY`.

## Configurar el correo (Gmail)
Activa la verificación en 2 pasos en tu cuenta Google → crea una **contraseña de aplicación** en https://myaccount.google.com/apppasswords →
ponla en `SMTP_PASSWORD` (con o sin espacios) y tu correo en `SMTP_USER`.

## Pruebas
```bash
cd backend && pip install -r requirements-dev.txt && pytest      # 15 pruebas, no necesitan Docker
cd frontend && npm install && npm run lint && npm run build
```

## Seguridad: pendiente del equipo
- **Revoca las API keys de Groq** que estaban en el proyecto original y crea una nueva (va solo en `.env`).
- La **clave privada RSA** (`private_key.pem`) estaba en el repositorio: se quitó de esta entrega, pero sigue en el historial de git. Genera un par nuevo si lo vas a usar.
- Cambia `DEFAULT_USERS_PASSWORD` o pon `CREATE_DEFAULT_USERS=false` fuera de la demostración.
