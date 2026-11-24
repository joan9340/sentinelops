"""Mensajes de la API en español e inglés (el idioma llega en la cabecera X-Lang)."""
from fastapi import Request

SUPPORTED = ("es", "en")

MESSAGES = {
    "invalid_credentials": ("Credenciales inválidas", "Invalid credentials"),
    "account_suspended": ("Cuenta suspendida por el Superadministrador", "Account suspended by the Superadmin"),
    "invalid_token": ("Token inválido o expirado", "Invalid or expired token"),
    "inactive_user": ("Usuario inactivo o inexistente", "Inactive or unknown user"),
    "forbidden_admin": ("Acceso denegado: se requiere rol Administrador o Superadministrador",
                        "Access denied: Administrator or Superadmin role required"),
    "forbidden_super": ("Acceso denegado: se requiere rol Superadministrador",
                        "Access denied: Superadmin role required"),
    "captcha_failed": ("No se pudo verificar que eres una persona. Inténtalo de nuevo.",
                       "We could not verify you are human. Please try again."),
    "captcha_unavailable": ("El servicio de verificación anti-robots no responde. Inténtalo en unos minutos.",
                            "The anti-bot verification service is not responding. Try again in a few minutes."),
    "username_invalid": ("El usuario debe tener entre 3 y 30 caracteres: letras, números, punto, guion o guion bajo.",
                         "Username must be 3-30 characters: letters, numbers, dot, hyphen or underscore."),
    "email_invalid": ("El correo electrónico no es válido.", "The email address is not valid."),
    "password_weak": ("La contraseña debe tener entre 8 y 72 caracteres, con al menos una letra y un número.",
                      "Password must be 8-72 characters long with at least one letter and one number."),
    "username_taken": ("Ese nombre de usuario ya está en uso.", "That username is already taken."),
    "email_taken": ("Ese correo electrónico ya está registrado.", "That email address is already registered."),
    "register_ok": ("Cuenta creada correctamente. Ya puedes iniciar sesión.",
                    "Account created successfully. You can now sign in."),
    "reset_requested": ("Si el correo está registrado, te enviamos un código de 6 dígitos. Revisa tu bandeja de entrada y spam.",
                        "If the email is registered, we sent you a 6-digit code. Check your inbox and spam folder."),
    "reset_invalid_code": ("El código es incorrecto o ya venció.", "The code is incorrect or has expired."),
    "reset_too_many": ("Demasiados intentos. Solicita un código nuevo.", "Too many attempts. Request a new code."),
    "reset_ok": ("Contraseña actualizada. Ya puedes iniciar sesión.", "Password updated. You can now sign in."),
    "invalid_role": ("Rol inválido", "Invalid role"),
    "user_not_found": ("Usuario no encontrado", "User not found"),
    "log_not_found": ("Registro de consulta no encontrado", "Query record not found"),
    "cannot_suspend_self": ("No puedes suspender tu propia cuenta activa", "You cannot suspend your own active account"),
}


def get_lang(request: Request) -> str:
    """Dependencia FastAPI: devuelve 'es' o 'en' según X-Lang / Accept-Language."""
    raw = request.headers.get("x-lang") or request.headers.get("accept-language") or "es"
    code = raw.strip().lower()[:2]
    return code if code in SUPPORTED else "es"


def msg(code: str, lang: str = "es") -> str:
    es, en = MESSAGES[code]
    return en if lang == "en" else es
