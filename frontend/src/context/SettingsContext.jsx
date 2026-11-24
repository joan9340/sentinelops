import { createContext, useCallback, useContext, useEffect, useMemo, useState } from 'react';
import { LANGUAGES, translate } from '../i18n';

const THEMES = ['light', 'dark', 'blue'];
const FONT_STEPS = [85, 100, 115, 130, 150]; // % del tamaño base del navegador
const DEFAULT_FONT_STEP = 1; // 100%

const SettingsContext = createContext(null);

const leer = (clave) => {
  try {
    return localStorage.getItem(clave);
  } catch {
    return null;
  }
};
const guardar = (clave, valor) => {
  try {
    localStorage.setItem(clave, String(valor));
  } catch {
    /* modo privado: se ignora */
  }
};

export function SettingsProvider({ children }) {
  const [theme, setTheme] = useState(() => {
    const v = leer('sentinelops.theme');
    return THEMES.includes(v) ? v : 'light';
  });
  const [lang, setLang] = useState(() => {
    const v = leer('sentinelops.lang');
    if (LANGUAGES.includes(v)) return v;
    return (navigator.language || 'es').toLowerCase().startsWith('en') ? 'en' : 'es';
  });
  const [fontStep, setFontStep] = useState(() => {
    const guardado = leer('sentinelops.fontStep');
    const v = guardado === null ? NaN : Number(guardado); // Number(null) sería 0: no es un valor guardado
    return Number.isInteger(v) && v >= 0 && v < FONT_STEPS.length ? v : DEFAULT_FONT_STEP;
  });

  // Aplica los ajustes a toda la página (los tamaños están en rem, así que todo escala).
  useEffect(() => {
    const root = document.documentElement;
    root.dataset.theme = theme;
    root.lang = lang;
    root.style.fontSize = `${FONT_STEPS[fontStep]}%`;
    guardar('sentinelops.theme', theme);
    guardar('sentinelops.lang', lang);
    guardar('sentinelops.fontStep', fontStep);
  }, [theme, lang, fontStep]);

  const increaseFont = useCallback(() => setFontStep((s) => Math.min(s + 1, FONT_STEPS.length - 1)), []);
  const decreaseFont = useCallback(() => setFontStep((s) => Math.max(s - 1, 0)), []);
  const resetFont = useCallback(() => setFontStep(DEFAULT_FONT_STEP), []);
  const t = useCallback((key, vars) => translate(lang, key, vars), [lang]);

  const value = useMemo(
    () => ({
      theme, setTheme, lang, setLang, t,
      fontPercent: FONT_STEPS[fontStep],
      canIncrease: fontStep < FONT_STEPS.length - 1,
      canDecrease: fontStep > 0,
      increaseFont, decreaseFont, resetFont,
    }),
    [theme, lang, t, fontStep, increaseFont, decreaseFont, resetFont],
  );
  return <SettingsContext.Provider value={value}>{children}</SettingsContext.Provider>;
}

// eslint-disable-next-line react-refresh/only-export-components
export const useSettings = () => useContext(SettingsContext);
