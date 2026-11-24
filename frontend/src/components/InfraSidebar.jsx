import { useAuth } from '../context/AuthContext';
import { useSettings } from '../context/SettingsContext';
import { useApiData } from '../services/useApiData';
import { styles } from '../styles/styles';

// Panel lateral: estado de la infraestructura y alcance del perfil activo.
export default function InfraSidebar() {
  const { role, isAdmin } = useAuth();
  const { t, lang } = useSettings();
  const { data, reload: cargar } = useApiData('/health/components', { lang });
  const components = data || [];

  return (
    <aside style={styles.sidebar}>
      <div style={styles.sidebarHeader}>
        <h4 style={{ margin: 0, color: 'var(--text)', fontSize: '0.95rem' }}>{t('infra.title')}</h4>
        <button type="button" className="btn" onClick={cargar} style={styles.refreshBtn} title={t('infra.refresh')} aria-label={t('infra.refresh')}>
          ↻
        </button>
      </div>

      <div style={styles.componentList}>
        {components.map((c) => (
          <div key={c.id} style={styles.componentCard}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', gap: '0.5rem' }}>
              <span style={{ fontWeight: 700, color: 'var(--text)', fontSize: '0.85rem' }}>{c.name}</span>
              <span style={styles.statusBadge}>{c.status}</span>
            </div>
            <div style={styles.componentFooter}>
              <span>
                {t('infra.port')}: <code style={{ color: 'var(--accent)', fontWeight: 700 }}>{c.port}</code>
              </span>
              {isAdmin && <span>{t('infra.sla')}: {c.uptime}</span>}
            </div>
          </div>
        ))}
      </div>

      <div style={styles.roleInfoBox}>
        <div style={{ fontSize: '0.74rem', fontWeight: 800, color: 'var(--text-muted)', marginBottom: '0.35rem' }}>
          {t('role.scopeTitle')} ({role.toUpperCase()})
        </div>
        <p style={{ margin: 0, fontSize: '0.8rem', color: 'var(--text)', lineHeight: 1.45 }}>{t(`role.${role}`)}</p>
      </div>
    </aside>
  );
}
