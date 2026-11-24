import os
import requests
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes, serialization

# 1. Generar o cargar las llaves RSA de prueba
PRIVATE_KEY_PATH = "private_key.pem"
PUBLIC_KEY_PATH = "public_key.pem"

def inicializar_llaves_rsa():
    """Genera un par de llaves RSA si no existen en el directorio."""
    if not os.path.exists(PRIVATE_KEY_PATH) or not os.path.exists(PUBLIC_KEY_PATH):
        print("[*] Generando nuevo par de llaves criptográficas RSA...")
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
        )
        public_key = private_key.public_key()

        # Guardar clave privada
        with open(PRIVATE_KEY_PATH, "wb") as f:
            f.write(private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption()
            ))

        # Guardar clave pública (para que la lea main.py)
        with open(PUBLIC_KEY_PATH, "wb") as f:
            f.write(public_key.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            ))
        print("[+] Llaves RSA generadas y guardadas con éxito.")

# Inicializar las llaves al ejecutar
inicializar_llaves_rsa()

def cargar_clave_privada():
    with open(PRIVATE_KEY_PATH, "rb") as key_file:
        return serialization.load_pem_private_key(key_file.read(), password=None)

# 2. Preparar los datos de la licencia y firmarlos digitalmente
private_key = cargar_clave_privada()
license_data = "ClienteAutorizado:DevSecOps_Project_2026:AccessGranted"

# Crear la firma digital usando padding PKCS1v15 y SHA256
signature = private_key.sign(
    license_data.encode("utf-8"),
    padding.PKCS1v15(),
    hashes.SHA256()
)

# Convertir la firma a formato hexadecimal para enviarla por headers HTTP
signature_hex = signature.hex()

# 3. Consumir el endpoint protegido de FastAPI
url = "http://localhost:8000/api/v1/rag/diagnose"

headers = {
    "Content-Type": "application/json",
    "X-License-Data": license_data,
    "X-License-Signature": signature_hex
}

payload = {
    "incidente": "Timeout",
    "pregunta": "¿Qué debo hacer para solucionar este problema en el servidor?"
}

print(f"\n[*] Enviando petición segura al servidor con firma RSA...")
response = requests.post(url, headers=headers, json=payload)

print(f"\n[+] Código de Estado HTTP: {response.status_code}")
print("[-] Respuesta del Servidor:")
print(response.json())