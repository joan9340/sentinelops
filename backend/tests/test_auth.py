OK = "token-ok"
NUEVO = {"username": "maria.perez", "email": "Maria@Correo.com", "password": "Segura2026", "turnstile_token": OK}


def login(client, user, pwd, token=OK, lang="es"):
    return client.post("/api/v1/auth/login", headers={"X-Lang": lang},
                       json={"username": user, "password": pwd, "turnstile_token": token})


def test_login_cuenta_demo_con_captcha(client):
    r = login(client, "admin", "admin123")
    assert r.status_code == 200 and r.json()["rol"] == "superadmin"


def test_login_sin_captcha_valido_se_rechaza(client):
    assert login(client, "admin", "admin123", token=None).status_code == 400
    assert login(client, "admin", "admin123", token="falso").status_code == 400


def test_registro_crea_operador_y_permite_login(client):
    r = client.post("/api/v1/auth/register", json=NUEVO)
    assert r.status_code == 201
    r = login(client, "maria.perez", "Segura2026")
    assert r.status_code == 200 and r.json()["rol"] == "operador"


def test_registro_valida_datos_y_duplicados(client):
    assert client.post("/api/v1/auth/register", json={**NUEVO, "password": "corta"}).status_code == 400
    assert client.post("/api/v1/auth/register", json={**NUEVO, "password": "sinnumeros"}).status_code == 400
    assert client.post("/api/v1/auth/register", json={**NUEVO, "email": "no-es-correo"}).status_code == 400
    assert client.post("/api/v1/auth/register", json={**NUEVO, "username": "a b"}).status_code == 400
    assert client.post("/api/v1/auth/register", json={**NUEVO, "turnstile_token": "falso"}).status_code == 400
    assert client.post("/api/v1/auth/register", json=NUEVO).status_code == 201
    assert client.post("/api/v1/auth/register", json={**NUEVO, "email": "otro@correo.com"}).status_code == 409   # usuario
    assert client.post("/api/v1/auth/register", json={**NUEVO, "username": "otra"}).status_code == 409            # correo
    assert client.post("/api/v1/auth/register", json={**NUEVO, "username": "ADMIN", "email": "x@y.co"}).status_code == 409


def test_registro_no_permite_elegir_rol(client):
    client.post("/api/v1/auth/register", json={**NUEVO, "rol": "superadmin"})
    assert login(client, "maria.perez", "Segura2026").json()["rol"] == "operador"


def test_recuperar_contrasena_flujo_completo(client):
    client.post("/api/v1/auth/register", json=NUEVO)
    r = client.post("/api/v1/auth/forgot-password", json={"email": "maria@correo.com", "turnstile_token": OK})
    assert r.status_code == 200 and len(client.enviados) == 1
    destino, usuario, codigo, _ = client.enviados[0]
    assert destino == "maria@correo.com" and usuario == "maria.perez" and len(codigo) == 6

    malo = client.post("/api/v1/auth/reset-password",
                       json={"email": "maria@correo.com", "code": "000000", "new_password": "NuevaClave9"})
    assert malo.status_code == 400
    ok = client.post("/api/v1/auth/reset-password",
                     json={"email": "maria@correo.com", "code": codigo, "new_password": "NuevaClave9"})
    assert ok.status_code == 200
    assert login(client, "maria.perez", "Segura2026").status_code == 401
    assert login(client, "maria.perez", "NuevaClave9").status_code == 200
    # el código es de un solo uso
    otra = client.post("/api/v1/auth/reset-password",
                       json={"email": "maria@correo.com", "code": codigo, "new_password": "OtraClave77"})
    assert otra.status_code == 400


def test_recuperar_no_revela_si_el_correo_existe(client):
    a = client.post("/api/v1/auth/forgot-password", json={"email": "nadie@correo.com", "turnstile_token": OK})
    client.post("/api/v1/auth/register", json=NUEVO)
    b = client.post("/api/v1/auth/forgot-password", json={"email": "maria@correo.com", "turnstile_token": OK})
    assert a.status_code == b.status_code == 200 and a.json() == b.json()
    assert len(client.enviados) == 1  # solo se envió al correo registrado


def test_recuperar_exige_captcha(client):
    r = client.post("/api/v1/auth/forgot-password", json={"email": "maria@correo.com", "turnstile_token": "falso"})
    assert r.status_code == 400


def test_recuperar_bloquea_tras_demasiados_intentos(client):
    client.post("/api/v1/auth/register", json=NUEVO)
    client.post("/api/v1/auth/forgot-password", json={"email": "maria@correo.com", "turnstile_token": OK})
    codigo = client.enviados[0][2]
    for _ in range(5):
        client.post("/api/v1/auth/reset-password",
                    json={"email": "maria@correo.com", "code": "999999", "new_password": "NuevaClave9"})
    r = client.post("/api/v1/auth/reset-password",
                    json={"email": "maria@correo.com", "code": codigo, "new_password": "NuevaClave9"})
    assert r.status_code == 429  # ni el código correcto sirve después de 5 fallos


def test_limite_de_solicitudes_por_hora(client):
    client.post("/api/v1/auth/register", json=NUEVO)
    for _ in range(5):
        client.post("/api/v1/auth/forgot-password", json={"email": "maria@correo.com", "turnstile_token": OK})
    assert len(client.enviados) == 3


def test_mensajes_en_ingles(client):
    r = login(client, "admin", "mala", lang="en")
    assert r.status_code == 401 and r.json()["detail"] == "Invalid credentials"
    r = login(client, "admin", "mala", lang="es")
    assert r.json()["detail"] == "Credenciales inválidas"


def test_roles_siguen_protegidos(client):
    tok = login(client, "operador", "admin123").json()["access_token"]
    h = {"Authorization": f"Bearer {tok}"}
    assert client.get("/api/v1/admin/stats", headers=h).status_code == 403
    assert client.get("/api/v1/admin/usuarios", headers=h).status_code == 403
    tok = login(client, "admin", "admin123").json()["access_token"]
    r = client.get("/api/v1/admin/usuarios", headers={"Authorization": f"Bearer {tok}"})
    assert r.status_code == 200 and {u["username"] for u in r.json()} >= {"admin", "auditor", "operador"}
