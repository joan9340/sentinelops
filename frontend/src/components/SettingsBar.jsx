import { useSettings } from '../context/SettingsContext';
import { FontLargerIcon, FontResetIcon, FontSmallerIcon, GlobeIcon, PaletteIcon } from './Icons';

const SWATCHES = [
  { id: 'light', color: '#ffffff', labelKey: 'settings.themeLight' },
  { id: 'dark', color: '#000000', labelKey: 'settings.themeDark' },
  { id: 'blue', color: '#0f3470', labelKey: 'settings.themeBlue' },
];

// Barra fija a la derecha de la pantalla: tamaño de letra, idioma y color de fondo.
export default function SettingsBar() {
  const { t, lang, setLang, theme, setTheme, fontPercent, canIncrease, canDecrease, increaseFont, decreaseFont, resetFont } = useSettings();

  return (
    <aside className="settings-bar" aria-label={t('settings.title')}>
      <span className="group-label" title={t('settings.fontSize')}>Aa</span>
      <button type="button" className="sb-btn" onClick={increaseFont} disabled={!canIncrease} title={t('settings.fontLarger')} aria-label={t('settings.fontLarger')}>
        <FontLargerIcon />
      </button>
      <span className="pct" aria-live="polite">{fontPercent}%</span>
      <button type="button" className="sb-btn" onClick={decreaseFont} disabled={!canDecrease} title={t('settings.fontSmaller')} aria-label={t('settings.fontSmaller')}>
        <FontSmallerIcon />
      </button>
      <button type="button" className="sb-btn" onClick={resetFont} title={t('settings.fontReset')} aria-label={t('settings.fontReset')}>
        <FontResetIcon />
      </button>

      <span className="sep" />
      <span className="group-label" title={t('settings.language')}><GlobeIcon /></span>
      <button type="button" className="sb-btn" aria-pressed={lang === 'es'} onClick={() => setLang('es')} title={t('settings.langEs')} aria-label={t('settings.langEs')}>ES</button>
      <button type="button" className="sb-btn" aria-pressed={lang === 'en'} onClick={() => setLang('en')} title={t('settings.langEn')} aria-label={t('settings.langEn')}>EN</button>

      <span className="sep" />
      <span className="group-label" title={t('settings.theme')}><PaletteIcon /></span>
      {SWATCHES.map((s) => (
        <button
          key={s.id}
          type="button"
          className="sb-swatch"
          style={{ background: s.color }}
          aria-pressed={theme === s.id}
          onClick={() => setTheme(s.id)}
          title={t(s.labelKey)}
          aria-label={t(s.labelKey)}
        />
      ))}
    </aside>
  );
}
