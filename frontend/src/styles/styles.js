// Estilos en línea de la interfaz. Todos los colores vienen de variables CSS (ver theme.css),
// y los tamaños están en rem para que el botón de tamaño de letra escale toda la pantalla.
const line = '1px solid var(--border)';

const button = {
  padding: '0.55rem 1rem',
  borderRadius: '8px',
  fontSize: '0.85rem',
  fontWeight: 700,
  cursor: 'pointer',
};
const primary = { ...button, border: 'none', background: 'var(--btn-bg)', color: 'var(--btn-text)' };
const secondary = { ...button, border: line, background: 'var(--surface-2)', color: 'var(--text)' };
const panel = { backgroundColor: 'var(--surface)', borderRadius: '12px', border: line };
const inner = { backgroundColor: 'var(--surface-2)', border: line, borderRadius: '10px' };
const chip = { padding: '0.15rem 0.55rem', borderRadius: '5px', fontSize: '0.74rem', fontWeight: 700 };

export const tone = (kind) => ({
  backgroundColor: `var(--${kind}-bg)`,
  color: `var(--${kind}-text)`,
  border: `1px solid var(--${kind}-border)`,
});

export const roleBadge = (role) => tone(role === 'superadmin' ? 'purple' : role === 'admin' ? 'warn' : 'cyan');

export const styles = {
  // ---- Autenticación ----
  authPage: { minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center', padding: '1.5rem', boxSizing: 'border-box' },
  authCard: { width: '100%', maxWidth: '27rem', padding: '2rem', borderRadius: '14px', backgroundColor: 'var(--surface)', border: line, boxShadow: 'var(--shadow)' },
  logoBadge: { display: 'inline-block', padding: '0.25rem 0.7rem', borderRadius: '999px', ...tone('cyan'), fontSize: '0.72rem', fontWeight: 800, letterSpacing: '0.6px', marginBottom: '0.75rem' },
  title: { fontSize: '1.9rem', fontWeight: 800, margin: '0 0 0.35rem 0', color: 'var(--text)' },
  subtitle: { color: 'var(--text-muted)', fontSize: '0.9rem', marginBottom: '1.4rem', lineHeight: 1.45 },
  modeTitle: { fontSize: '1.1rem', fontWeight: 800, margin: '0 0 1rem 0', color: 'var(--text)' },
  form: { display: 'flex', flexDirection: 'column', gap: '1rem' },
  fieldGroup: { display: 'flex', flexDirection: 'column', gap: '0.4rem' },
  label: { fontSize: '0.85rem', fontWeight: 700, color: 'var(--text)' },
  hint: { fontSize: '0.78rem', color: 'var(--text-muted)', margin: 0 },
  input: { padding: '0.7rem 0.9rem', borderRadius: '8px', border: '1px solid var(--border)', backgroundColor: 'var(--surface-2)', color: 'var(--text)', fontSize: '0.95rem' },
  primaryBtn: { ...primary, padding: '0.8rem 1.25rem', fontSize: '0.95rem' },
  errorBox: { ...tone('err'), padding: '0.7rem', borderRadius: '8px', fontSize: '0.88rem', textAlign: 'center' },
  successBox: { ...tone('ok'), padding: '0.7rem', borderRadius: '8px', fontSize: '0.88rem', textAlign: 'center' },
  linksRow: { display: 'flex', justifyContent: 'space-between', flexWrap: 'wrap', gap: '0.5rem', marginTop: '1.1rem' },
  linkBtn: { background: 'none', border: 'none', padding: '0.2rem 0', color: 'var(--accent)', fontSize: '0.88rem', fontWeight: 700, cursor: 'pointer', textDecoration: 'underline' },

  // ---- Estructura del panel ----
  dashboardContainer: { minHeight: '100vh', backgroundColor: 'var(--bg)', color: 'var(--text)', display: 'flex', flexDirection: 'column' },
  header: { padding: '0.9rem 1.5rem', backgroundColor: 'var(--surface)', borderBottom: line, display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '1rem' },
  rolePill: { padding: '0.12rem 0.6rem', borderRadius: '999px', fontSize: '0.7rem', fontWeight: 800, letterSpacing: '0.5px' },
  navTabs: { display: 'flex', gap: '0.4rem', flexWrap: 'wrap', backgroundColor: 'var(--surface-2)', padding: '0.3rem', borderRadius: '10px', border: line },
  navTab: { ...button, padding: '0.5rem 1rem', border: '1px solid transparent', backgroundColor: 'transparent', color: 'var(--text-muted)', fontWeight: 700 },
  navTabActive: { ...button, padding: '0.5rem 1rem', border: '1px solid var(--accent)', backgroundColor: 'var(--surface-3)', color: 'var(--text)' },
  logoutBtn: secondary,
  mainContent: { flex: 1, display: 'flex', gap: '1.25rem', padding: '1.25rem', boxSizing: 'border-box', flexWrap: 'wrap', alignItems: 'stretch' },
  sidebar: { ...panel, width: '19rem', maxWidth: '100%', padding: '1.15rem', display: 'flex', flexDirection: 'column', gap: '0.9rem', boxSizing: 'border-box' },
  sidebarHeader: { display: 'flex', justifyContent: 'space-between', alignItems: 'center', borderBottom: line, paddingBottom: '0.7rem' },
  refreshBtn: { background: 'none', border: 'none', color: 'var(--accent)', cursor: 'pointer', fontSize: '1.25rem', fontWeight: 800 },
  componentList: { display: 'flex', flexDirection: 'column', gap: '0.75rem' },
  componentCard: { ...inner, padding: '0.8rem', borderRadius: '8px' },
  statusBadge: { ...tone('ok'), ...chip, fontSize: '0.7rem' },
  componentFooter: { display: 'flex', justifyContent: 'space-between', marginTop: '0.45rem', fontSize: '0.78rem', color: 'var(--text-muted)' },
  roleInfoBox: { marginTop: 'auto', padding: '0.85rem', borderRadius: '8px', backgroundColor: 'var(--surface-2)', border: line },

  // ---- Consola ----
  chatSection: { ...panel, flex: 1, minWidth: '18rem', display: 'flex', flexDirection: 'column', padding: '1.25rem' },
  messageList: { flex: 1, display: 'flex', flexDirection: 'column', gap: '1.1rem', overflowY: 'auto', paddingBottom: '1rem', minHeight: '16rem' },
  welcomeCard: { ...inner, padding: '2rem', textAlign: 'center', marginTop: '1.5rem' },
  userRow: { display: 'flex', justifyContent: 'flex-end' },
  botRow: { display: 'flex', justifyContent: 'flex-start' },
  userBubble: { background: 'var(--btn-bg)', color: 'var(--btn-text)', padding: '0.75rem 1.2rem', borderRadius: '12px 12px 0 12px', maxWidth: '75%', fontSize: '0.95rem', fontWeight: 600 },
  errorBubble: { ...tone('err'), padding: '0.75rem 1rem', borderRadius: '8px', fontSize: '0.9rem' },
  loadingBubble: { color: 'var(--accent)', fontStyle: 'italic', fontSize: '0.9rem', fontWeight: 600 },
  diagCard: { ...inner, padding: '1.2rem', width: '100%', maxWidth: '42rem', boxSizing: 'border-box' },
  diagHeader: { display: 'flex', justifyContent: 'space-between', alignItems: 'center', gap: '0.75rem', flexWrap: 'wrap', borderBottom: line, paddingBottom: '0.55rem' },
  badge: chip,
  cliBox: { backgroundColor: 'var(--surface)', padding: '0.75rem', borderRadius: '6px', display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: '0.75rem', border: line, gap: '0.75rem', flexWrap: 'wrap' },
  copyBtn: { ...secondary, padding: '0.38rem 0.75rem', fontSize: '0.78rem', whiteSpace: 'nowrap' },
  inputForm: { display: 'flex', gap: '0.75rem', marginTop: '1rem', flexWrap: 'wrap' },
  chatInput: { flex: 1, minWidth: '12rem', padding: '0.85rem 1.1rem', borderRadius: '8px', border: '1px solid var(--border)', backgroundColor: 'var(--surface-2)', color: 'var(--text)', fontSize: '0.95rem' },
  sendBtn: { ...primary, padding: '0.85rem 1.5rem', fontSize: '0.95rem' },

  // ---- Paneles de auditoría y usuarios ----
  panelSection: { ...panel, flex: 1, minWidth: '18rem', display: 'flex', flexDirection: 'column', gap: '1.1rem', padding: '1.35rem', overflowY: 'auto', boxSizing: 'border-box' },
  panelTopBar: { display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '0.75rem', borderBottom: line, paddingBottom: '0.85rem' },
  secondaryBtn: secondary,
  exportBtn: { ...button, border: '1px solid var(--accent)', backgroundColor: 'var(--surface-2)', color: 'var(--accent)' },
  kpiGrid: { display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(10.5rem, 1fr))', gap: '0.9rem' },
  kpiCard: { ...inner, padding: '1rem', display: 'flex', flexDirection: 'column', gap: '0.35rem' },
  kpiLabel: { fontSize: '0.74rem', fontWeight: 800, color: 'var(--text-muted)', letterSpacing: '0.5px' },
  kpiValue: { fontSize: '1.7rem', fontWeight: 800, color: 'var(--text)' },
  subCard: { ...inner, padding: '1.1rem' },
  subTitle: { margin: '0 0 0.85rem 0', color: 'var(--text)', fontSize: '1rem', fontWeight: 800 },
  barTrack: { width: '100%', height: '0.55rem', backgroundColor: 'var(--surface-3)', borderRadius: '999px', overflow: 'hidden' },
  barFill: { height: '100%', background: 'var(--accent)', borderRadius: '999px' },
  table: { width: '100%', borderCollapse: 'collapse', fontSize: '0.85rem' },
  th: { textAlign: 'left', padding: '0.65rem', borderBottom: '2px solid var(--border)', color: 'var(--text-muted)', fontWeight: 800 },
  tr: { borderBottom: line },
  td: { padding: '0.65rem', color: 'var(--text)', verticalAlign: 'middle' },
  verifiedBtn: { ...tone('ok'), ...chip, cursor: 'pointer' },
  unverifiedBtn: { ...chip, border: '1px solid var(--border)', backgroundColor: 'var(--surface)', color: 'var(--text)', cursor: 'pointer' },
  roleSelect: { padding: '0.3rem 0.5rem', borderRadius: '5px', border: '1px solid var(--border)', backgroundColor: 'var(--surface-2)', color: 'var(--text)', fontSize: '0.85rem' },
  suspendBtn: { ...tone('err'), ...chip, cursor: 'pointer' },
  activateBtn: { ...tone('ok'), ...chip, cursor: 'pointer' },
  statusChip: chip,
};
