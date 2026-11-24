import { useAuth } from '../context/AuthContext';
import { useSettings } from '../context/SettingsContext';
import { apiFetch } from '../services/api';
import { useApiData } from '../services/useApiData';
import { styles, tone } from '../styles/styles';

const escaparCsv = (valor) => `"${String(valor ?? '').replace(/"/g, '""')}"`;

export default function AuditPage() {
  const { token } = useAuth();
  const { t, lang } = useSettings();
  const { data: stats, reload: cargar } = useApiData('/admin/stats', { token, lang });

  const verificar = async (id) => {
    try {
      await apiFetch(`/admin/logs/${id}/verificar`, { method: 'PATCH', token, lang });
      cargar();
    } catch (err) {
      console.error('Error verificando registro:', err);
    }
  };

  const exportarCsv = () => {
    if (!stats?.historial_chat?.length) return;
    const filas = stats.historial_chat.map((r) =>
      [
        r.id, escaparCsv(r.username), escaparCsv(r.componente), `${r.confianza}%`,
        escaparCsv(r.prompt), escaparCsv(r.comando_cli), r.verificado ? t('audit.yes') : t('audit.no'), r.timestamp,
      ].join(','),
    );
    const contenido = [t('audit.csvHeaders').join(','), ...filas].join('\n');
    // BOM para que Excel respete las tildes; Blob para que '#' y otros símbolos no corten el archivo.
    const blob = new Blob(['\uFEFF' + contenido], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `sentinelops_auditoria_${new Date().toISOString().slice(0, 10)}.csv`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  return (
    <main style={styles.panelSection}>
      <div style={styles.panelTopBar}>
        <div>
          <h3 style={{ margin: 0, color: 'var(--text)' }}>{t('audit.title')}</h3>
          <span style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>{t('audit.subtitle')}</span>
        </div>
        <div style={{ display: 'flex', gap: '0.6rem', flexWrap: 'wrap' }}>
          <button type="button" className="btn" onClick={cargar} style={styles.secondaryBtn}>{t('audit.refresh')}</button>
          <button type="button" className="btn" onClick={exportarCsv} style={styles.exportBtn}>{t('audit.export')}</button>
        </div>
      </div>

      {!stats ? (
        <div style={{ color: 'var(--text-muted)', padding: '2rem', textAlign: 'center' }}>{t('audit.loading')}</div>
      ) : (
        <>
          <div style={styles.kpiGrid}>
            <div style={styles.kpiCard}>
              <span style={styles.kpiLabel}>{t('audit.kpiTotal')}</span>
              <span style={styles.kpiValue}>{stats.kpis.total_consultas}</span>
            </div>
            <div style={styles.kpiCard}>
              <span style={styles.kpiLabel}>{t('audit.kpiOk')}</span>
              <span style={{ ...styles.kpiValue, color: 'var(--ok-text)' }}>{stats.kpis.consultas_exitosas}</span>
            </div>
            <div style={styles.kpiCard}>
              <span style={styles.kpiLabel}>{t('audit.kpiOut')}</span>
              <span style={{ ...styles.kpiValue, color: 'var(--err-text)' }}>{stats.kpis.consultas_rechazadas}</span>
            </div>
            <div style={styles.kpiCard}>
              <span style={styles.kpiLabel}>{t('audit.kpiPrecision')}</span>
              <span style={{ ...styles.kpiValue, color: 'var(--accent)' }}>{stats.kpis.tasa_precision}%</span>
            </div>
          </div>

          <div style={styles.subCard}>
            <h4 style={styles.subTitle}>{t('audit.topTitle')}</h4>
            {stats.top_componentes.length === 0 ? (
              <span style={{ color: 'var(--text-muted)', fontSize: '0.9rem' }}>{t('audit.noQueries')}</span>
            ) : (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.6rem' }}>
                {stats.top_componentes.map((item, idx) => {
                  const max = stats.top_componentes[0].total || 1;
                  return (
                    <div key={idx}>
                      <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.85rem', marginBottom: '0.2rem' }}>
                        <span style={{ color: 'var(--text)' }}>{item.componente}</span>
                        <span style={{ color: 'var(--accent)', fontWeight: 800 }}>{item.total} {t('audit.queries')}</span>
                      </div>
                      <div style={styles.barTrack}>
                        <div style={{ ...styles.barFill, width: `${Math.round((item.total / max) * 100)}%` }} />
                      </div>
                    </div>
                  );
                })}
              </div>
            )}
          </div>

          <div style={styles.subCard}>
            <h4 style={styles.subTitle}>{t('audit.chatTitle')}</h4>
            <div style={{ overflowX: 'auto' }}>
              <table style={styles.table}>
                <thead>
                  <tr>
                    {['colDate', 'colUser', 'colComponent', 'colQuery', 'colConfidence', 'colReview'].map((k) => (
                      <th key={k} style={styles.th}>{t(`audit.${k}`)}</th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {stats.historial_chat.map((row) => (
                    <tr key={row.id} style={styles.tr}>
                      <td style={styles.td}>{row.timestamp}</td>
                      <td style={{ ...styles.td, color: 'var(--accent)', fontWeight: 700 }}>{row.username}</td>
                      <td style={styles.td}>{row.componente}</td>
                      <td style={{ ...styles.td, maxWidth: '18rem' }}>{row.prompt}</td>
                      <td style={styles.td}>{row.confianza}%</td>
                      <td style={styles.td}>
                        <button type="button" className="btn" onClick={() => verificar(row.id)} style={row.verificado ? styles.verifiedBtn : styles.unverifiedBtn}>
                          {row.verificado ? t('audit.verified') : t('audit.markOk')}
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          <div style={styles.subCard}>
            <h4 style={styles.subTitle}>{t('audit.secTitle')}</h4>
            <div style={{ overflowX: 'auto' }}>
              <table style={styles.table}>
                <thead>
                  <tr>
                    {['colDate', 'colActor', 'colEvent', 'colDetail', 'colLevel'].map((k) => (
                      <th key={k} style={styles.th}>{t(`audit.${k}`)}</th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {stats.bitacora_seguridad.map((ev) => (
                    <tr key={ev.id} style={styles.tr}>
                      <td style={styles.td}>{ev.timestamp}</td>
                      <td style={{ ...styles.td, fontWeight: 700 }}>{ev.actor}</td>
                      <td style={styles.td}><code>{ev.accion}</code></td>
                      <td style={styles.td}>{ev.detalle}</td>
                      <td style={styles.td}>
                        <span style={{ ...styles.statusChip, ...tone(ev.estado === 'ALERTA' ? 'err' : 'ok') }}>{ev.estado}</span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </>
      )}
    </main>
  );
}
