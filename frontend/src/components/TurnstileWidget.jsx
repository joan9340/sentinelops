import { useEffect, useRef } from 'react';
import { TURNSTILE_SITE_KEY } from '../config';

const SCRIPT_SRC = 'https://challenges.cloudflare.com/turnstile/v0/api.js?render=explicit';
let scriptPromise = null;

function cargarScript() {
  if (window.turnstile) return Promise.resolve(window.turnstile);
  if (!scriptPromise) {
    scriptPromise = new Promise((resolve, reject) => {
      const s = document.createElement('script');
      s.src = SCRIPT_SRC;
      s.async = true;
      s.defer = true;
      s.onload = () => resolve(window.turnstile);
      s.onerror = () => {
        scriptPromise = null;
        reject(new Error('turnstile-load'));
      };
      document.head.appendChild(s);
    });
  }
  return scriptPromise;
}

/**
 * Robot autenticador de Cloudflare Turnstile.
 * - onToken(token | null): entrega el token al formulario (se envía al backend, que lo verifica).
 * - resetSignal: al cambiar su valor se vuelve a pedir un token (cada token sirve una sola vez).
 * - Se vuelve a dibujar al cambiar el tema o el idioma.
 */
export default function TurnstileWidget({ onToken, onError, theme, language, resetSignal }) {
  const contenedor = useRef(null);
  const widgetId = useRef(null);

  useEffect(() => {
    let cancelado = false;
    cargarScript()
      .then((turnstile) => {
        if (cancelado || !contenedor.current) return;
        widgetId.current = turnstile.render(contenedor.current, {
          sitekey: TURNSTILE_SITE_KEY,
          theme: theme === 'light' ? 'light' : 'dark',
          language,
          callback: (token) => onToken(token),
          'expired-callback': () => onToken(null),
          'error-callback': () => {
            onToken(null);
            onError?.();
          },
        });
      })
      .catch(() => onError?.());

    return () => {
      cancelado = true;
      onToken(null);
      if (widgetId.current !== null && window.turnstile) {
        try { window.turnstile.remove(widgetId.current); } catch { /* ya eliminado */ }
      }
      widgetId.current = null;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [theme, language]);

  useEffect(() => {
    if (resetSignal && widgetId.current !== null && window.turnstile) {
      try { window.turnstile.reset(widgetId.current); } catch { /* sin widget */ }
      onToken(null);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [resetSignal]);

  return <div ref={contenedor} style={{ minHeight: '65px', display: 'flex', justifyContent: 'center' }} />;
}
