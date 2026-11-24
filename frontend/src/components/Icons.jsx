// Íconos SVG simples (sin dependencias externas). Heredan el color con currentColor.
const base = { width: 20, height: 20, viewBox: '0 0 24 24', fill: 'none', stroke: 'currentColor', strokeWidth: 2, strokeLinecap: 'round', strokeLinejoin: 'round', 'aria-hidden': true };

// Letra "A" con signo + o -  (tamaño de letra)
export const FontLargerIcon = () => (
  <svg {...base}><path d="M3 20 9 5l6 15M5.2 15h7.6" /><path d="M18 5v6M15 8h6" /></svg>
);
export const FontSmallerIcon = () => (
  <svg {...base}><path d="M3 20 9 5l6 15M5.2 15h7.6" /><path d="M15 8h6" /></svg>
);
export const FontResetIcon = () => (
  <svg {...base}><path d="M4 12a8 8 0 1 0 2.5-5.8L4 8" /><path d="M4 3v5h5" /></svg>
);
export const GlobeIcon = () => (
  <svg {...base}><circle cx="12" cy="12" r="9" /><path d="M3 12h18M12 3c3 3 3 15 0 18M12 3c-3 3-3 15 0 18" /></svg>
);
export const PaletteIcon = () => (
  <svg {...base}><circle cx="12" cy="12" r="9" /><path d="M12 3v18" /><path d="M12 3a9 9 0 0 1 0 18" fill="currentColor" stroke="none" /></svg>
);
