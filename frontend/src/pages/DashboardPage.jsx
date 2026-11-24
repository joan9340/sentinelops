import { useState } from 'react';
import InfraSidebar from '../components/InfraSidebar';
import { useAuth } from '../context/AuthContext';
import { useSettings } from '../context/SettingsContext';
import { roleBadge, styles } from '../styles/styles';
import AuditPage from './AuditPage';
import ConsolePage from './ConsolePage';
import UsersPage from './UsersPage';

export default function DashboardPage() {
  const { username, role, isAdmin, isSuperAdmin, logout } = useAuth();
  const { t } = useSettings();
  const [tab, setTab] = useState('console'); // 'console' | 'audit' | 'users'

  const tabs = [
    { id: 'console', label: t('nav.console'), visible: true },
    { id: 'audit', label: t('nav.audit'), visible: isAdmin },
    { id: 'users', label: t('nav.users'), visible: isSuperAdmin },
  ].filter((x) => x.visible);

  return (
    <div style={styles.dashboardContainer}>
      <header style={styles.header}>
        <div>
          <h3 style={{ margin: 0, color: 'var(--text)', letterSpacing: '0.5px', fontSize: '1.2rem' }}>
            Sentinel<span style={{ color: 'var(--accent)' }}>Ops</span>{' '}
            <span style={{ color: 'var(--text-muted)', fontWeight: 400 }}>| {t('app.commandCenter')}</span>
          </h3>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginTop: '0.25rem', flexWrap: 'wrap' }}>
            <span style={{ fontSize: '0.78rem', color: 'var(--ok-text)', fontWeight: 700 }}>{t('app.engineActive')}</span>
            <span style={{ color: 'var(--text-muted)' }}>•</span>
            <span style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>
              {t('app.session')}: <strong style={{ color: 'var(--text)' }}>{username}</strong>
            </span>
            <span style={{ ...styles.rolePill, ...roleBadge(role) }}>{role.toUpperCase()}</span>
          </div>
        </div>

        <nav style={styles.navTabs} aria-label="Principal">
          {tabs.map((x) => (
            <button
              key={x.id}
              type="button"
              className="btn"
              onClick={() => setTab(x.id)}
              aria-current={tab === x.id ? 'page' : undefined}
              style={tab === x.id ? styles.navTabActive : styles.navTab}
            >
              {x.label}
            </button>
          ))}
        </nav>

        <button type="button" className="btn" onClick={logout} style={styles.logoutBtn}>
          {t('nav.logout')}
        </button>
      </header>

      <div style={styles.mainContent}>
        <InfraSidebar />
        {tab === 'console' && <ConsolePage />}
        {tab === 'audit' && isAdmin && <AuditPage />}
        {tab === 'users' && isSuperAdmin && <UsersPage />}
      </div>
    </div>
  );
}
