import { API_BASE } from '../config';

export class ApiError extends Error {
  constructor(message, status = 0, network = false) {
    super(message);
    this.status = status;
    this.network = network; // true si el servidor no respondió (backend caído, CORS, sin red)
  }
}

// Envía la petición con el idioma elegido (X-Lang) para que la API responda en ese idioma.
export async function apiFetch(path, { method = 'GET', body, token, lang = 'es' } = {}) {
  const headers = { 'Content-Type': 'application/json', 'X-Lang': lang };
  if (token) headers.Authorization = `Bearer ${token}`;

  let res;
  try {
    res = await fetch(`${API_BASE}${path}`, {
      method,
      headers,
      body: body !== undefined ? JSON.stringify(body) : undefined,
    });
  } catch {
    throw new ApiError('network', 0, true);
  }

  let data = null;
  try {
    data = await res.json();
  } catch {
    /* respuesta sin cuerpo JSON */
  }

  if (!res.ok) {
    const detail = data?.detail;
    // FastAPI devuelve una lista en errores 422 de validación: se trata como "datos inválidos".
    throw new ApiError(typeof detail === 'string' ? detail : '', res.status);
  }
  return data;
}

// Convierte un ApiError en el texto que ve el usuario.
export function mensajeDeError(err, t) {
  if (err?.network) return t('errors.network');
  if (err?.message) return err.message;
  if (err?.status === 422) return t('errors.invalid');
  return t('errors.generic');
}
