// Configuración del frontend (se define en el archivo .env de la raíz y llega vía docker compose).
export const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

// Clave PÚBLICA de Cloudflare Turnstile. Por defecto usa la clave de prueba (siempre pasa).
export const TURNSTILE_SITE_KEY = import.meta.env.VITE_TURNSTILE_SITE_KEY || '1x00000000000000000000AA';
