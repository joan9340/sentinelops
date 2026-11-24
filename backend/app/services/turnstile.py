"""Verificación del robot autenticador (Cloudflare Turnstile) en el servidor."""
import json
import logging
import urllib.error
import urllib.parse
import urllib.request

from app import config

logger = logging.getLogger("sentinelops")


def verificar_turnstile(token: str | None, remote_ip: str | None = None) -> tuple[bool, str]:
    """Devuelve (ok, motivo). motivo: 'disabled' | 'missing-token' | 'network-error' | código de Cloudflare."""
    if not config.TURNSTILE_ENABLED:
        return True, "disabled"
    if not token:
        return False, "missing-token"

    campos = {"secret": config.TURNSTILE_SECRET_KEY, "response": token}
    if remote_ip:
        campos["remoteip"] = remote_ip
    req = urllib.request.Request(
        config.TURNSTILE_VERIFY_URL,
        data=urllib.parse.urlencode(campos).encode(),
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=8) as resp:
            datos = json.loads(resp.read().decode())
    except (urllib.error.URLError, TimeoutError, ValueError) as e:
        logger.error("No se pudo contactar a Cloudflare Turnstile: %s", e)
        return False, "network-error"

    if datos.get("success"):
        return True, "ok"
    return False, ",".join(datos.get("error-codes", [])) or "rejected"
