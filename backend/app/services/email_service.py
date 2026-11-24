"""Envío de correos por SMTP (Gmail con contraseña de aplicación)."""
import html
import logging
import smtplib
import ssl
from email.message import EmailMessage
from email.utils import formataddr

from app import config

logger = logging.getLogger("sentinelops")


def smtp_configurado() -> bool:
    return bool(config.SMTP_USER and config.SMTP_PASSWORD)


def _plantilla_recuperacion(username: str, codigo: str, lang: str) -> tuple[str, str, str]:
    minutos = config.RESET_CODE_MINUTES
    user = html.escape(username)
    if lang == "en":
        asunto = "SentinelOps — Your password reset code"
        texto = (f"Hello {username},\n\nYour password reset code is: {codigo}\n"
                 f"It expires in {minutos} minutes. If you did not request it, ignore this email.\n\n— SentinelOps")
        cuerpo = (f"<p>Hello <b>{user}</b>,</p><p>Your password reset code is:</p>"
                  f"<p style='font-size:30px;letter-spacing:8px;font-weight:700'>{codigo}</p>"
                  f"<p>It expires in {minutos} minutes. If you did not request it, ignore this email.</p>")
    else:
        asunto = "SentinelOps — Tu código para restablecer la contraseña"
        texto = (f"Hola {username},\n\nTu código para restablecer la contraseña es: {codigo}\n"
                 f"Vence en {minutos} minutos. Si no lo solicitaste, ignora este correo.\n\n— SentinelOps")
        cuerpo = (f"<p>Hola <b>{user}</b>,</p><p>Tu código para restablecer la contraseña es:</p>"
                  f"<p style='font-size:30px;letter-spacing:8px;font-weight:700'>{codigo}</p>"
                  f"<p>Vence en {minutos} minutos. Si no lo solicitaste, ignora este correo.</p>")
    return asunto, texto, f"<div style='font-family:Arial,sans-serif;color:#0F172A'>{cuerpo}<p>— SentinelOps</p></div>"


def enviar_codigo_recuperacion(destino: str, username: str, codigo: str, lang: str = "es") -> bool:
    if not smtp_configurado():
        logger.error("SMTP no configurado (SMTP_USER / SMTP_PASSWORD): no se envió el código de recuperación.")
        return False

    asunto, texto, cuerpo_html = _plantilla_recuperacion(username, codigo, lang)
    mensaje = EmailMessage()
    mensaje["Subject"] = asunto
    mensaje["From"] = formataddr((config.SMTP_FROM_NAME, config.SMTP_FROM))
    mensaje["To"] = destino
    mensaje.set_content(texto)
    mensaje.add_alternative(cuerpo_html, subtype="html")

    try:
        with smtplib.SMTP(config.SMTP_HOST, config.SMTP_PORT, timeout=15) as smtp:
            smtp.starttls(context=ssl.create_default_context())
            smtp.login(config.SMTP_USER, config.SMTP_PASSWORD)
            smtp.send_message(mensaje)
        return True
    except Exception as e:
        logger.error("Fallo enviando correo de recuperación: %s", e)
        return False
