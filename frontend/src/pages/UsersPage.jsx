import { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { useSettings } from '../context/SettingsContext';
import { apiFetch, mensajeDeError } from '../services/api';
import { useApiData } from '../services/useApiData';
import { styles, tone } from '../styles/styles';

export default function UsersPage() {
  const { token } = useAuth();
  const { t, lang } = useSettings();
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [role, setRole] = useState('operador');
  const [message, setMessage] = useState(null); // { type: 'ok' | 'err', text }

  const { data, reload: cargar } = useApiData('/admin/usuarios', { token, lang });
  const users = data || [];

  const crear = async (e) => {
    e.preventDefault();
    setMessage(null);
    try {
      const data = await apiFetch('/admin/usuarios', { method: 'POST', token, lang, body: { username, password, rol: role } });
      setUsername('');
      setPassword('');
      setRole('operador');
      setMessage({ type: 'ok', text: t('users.created', { username: data.username, role: data.rol.toUpperCase() }) });
      cargar();
    } catch (err) {
      setMessage({ type: 'err', text: mensajeDeError(err, t) });
    }
  };

  const cambiarRol = async (id, rol) => {
    try {
      await apiFetch(`/admin/usuarios/${id}/rol`, { method: 'PATCH', token, lang, body: { rol } });
      cargar();
    } catch (err) {
      console.error('Error cambiando rol:', err);
    }
  };

  const alternarEstado = async (id) => {
    try {
      await apiFetch(`/admin/usuarios/${id}/estado`, { method: 'PATCH', token, lang });
      cargar();
    } catch (err) {
      alert(mensajeDeError(err, t));
    }
  };

  return (
    <main style={styles.panelSection}>
      <div style={styles.panelTopBar}>
        <div>
          <h3 style={{ margin: 0, color: 'var(--text)' }}>{t('users.title')}</h3>
          <span style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>{t('users.subtitle')}</span>
        </div>
      </div>

      <div style={styles.subCard}>
        <h4 style={styles.subTitle}>{t('users.createTitle')}</h4>
        {message && (
          <div style={{ ...tone(message.type === 'ok' ? 'ok' : 'err'), padding: '0.6rem 0.9rem', borderRadius: '6px', marginBottom: '0.85rem', fontSize: '0.88rem' }} role="status">
            {message.text}
          </div>
        )}
        <form onSubmit={crear} style={{ display: 'flex', gap: '0.75rem', flexWrap: 'wrap' }}>
          <input type="text" placeholder={t('users.usernamePh')} aria-label={t('users.usernamePh')} value={username} onChange={(e) => setUsername(e.target.value)} required style={{ ...styles.input, flex: 1, minWidth: '11rem' }} />
          <input type="password" placeholder={t('users.passwordPh')} aria-label={t('users.passwordPh')} value={password} onChange={(e) => setPassword(e.target.value)} required style={{ ...styles.input, flex: 1, minWidth: '11rem' }} />
          <select value={role} onChange={(e) => setRole(e.target.value)} aria-label="Rol" style={{ ...styles.input, minWidth: '11rem' }}>
            <option value="operador">{t('users.roleOperator')}</option>
            <option value="admin">{t('users.roleAdmin')}</option>
            <option value="superadmin">{t('users.roleSuper')}</option>
          </select>
          <button type="submit" className="btn" style={styles.primaryBtn}>{t('users.create')}</button>
        </form>
      </div>

      <div style={styles.subCard}>
        <h4 style={styles.subTitle}>{t('users.directory')}</h4>
        <div style={{ overflowX: 'auto' }}>
          <table style={styles.table}>
            <thead>
              <tr>
                {['colId', 'colUser', 'colEmail', 'colRole', 'colStatus', 'colActions'].map((k) => (
                  <th key={k} style={styles.th}>{t(`users.${k}`)}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {users.map((u) => (
                <tr key={u.id} style={styles.tr}>
                  <td style={styles.td}>#{u.id}</td>
                  <td style={{ ...styles.td, fontWeight: 800 }}>{u.username}</td>
                  <td style={styles.td}>{u.email || t('users.noEmail')}</td>
                  <td style={styles.td}>
                    <select value={u.rol} onChange={(e) => cambiarRol(u.id, e.target.value)} aria-label="Rol" style={styles.roleSelect}>
                      <option value="operador">operador</option>
                      <option value="admin">admin</option>
                      <option value="superadmin">superadmin</option>
                    </select>
                  </td>
                  <td style={styles.td}>
                    <span style={{ ...styles.statusChip, ...tone(u.is_active ? 'ok' : 'err') }}>
                      {u.is_active ? t('users.active') : t('users.suspended')}
                    </span>
                  </td>
                  <td style={styles.td}>
                    <button type="button" className="btn" onClick={() => alternarEstado(u.id)} style={u.is_active ? styles.suspendBtn : styles.activateBtn}>
                      {u.is_active ? t('users.suspend') : t('users.reactivate')}
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </main>
  );
}
