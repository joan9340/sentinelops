import { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { useSettings } from '../context/SettingsContext';
import { apiFetch, mensajeDeError } from '../services/api';
import { styles, tone } from '../styles/styles';

export default function ConsolePage() {
  const { token } = useAuth();
  const { t, lang } = useSettings();
  const [input, setInput] = useState('');
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(false);
  const [copiedIndex, setCopiedIndex] = useState(null);

  const enviar = async (e) => {
    e.preventDefault();
    const pregunta = input.trim();
    if (!pregunta) return;

    setInput('');
    setHistory((prev) => [...prev, { sender: 'user', text: pregunta }]);
    setLoading(true);
    try {
      const data = await apiFetch('/rag/diagnose', { method: 'POST', token, lang, body: { prompt: pregunta } });
      setHistory((prev) => [...prev, { sender: 'bot', data }]);
    } catch (err) {
      const texto = err.status === 401 || err.status === 403 ? t('console.sessionError') : mensajeDeError(err, t);
      setHistory((prev) => [...prev, { sender: 'bot', error: texto }]);
    } finally {
      setLoading(false);
    }
  };

  const copiar = async (texto, i) => {
    try {
      await navigator.clipboard.writeText(texto);
      setCopiedIndex(i);
      setTimeout(() => setCopiedIndex(null), 1500);
    } catch {
      /* portapapeles no disponible */
    }
  };

  return (
    <main style={styles.chatSection}>
      <div style={styles.messageList} aria-live="polite">
        {history.length === 0 && (
          <div style={styles.welcomeCard}>
            <h4 style={{ color: 'var(--accent)', marginTop: 0, fontSize: '1.15rem' }}>{t('console.welcomeTitle')}</h4>
            <p style={{ color: 'var(--text-muted)', fontSize: '0.95rem', maxWidth: '34rem', margin: '0 auto', lineHeight: 1.5 }}>
              {t('console.welcomeText')}
            </p>
          </div>
        )}

        {history.map((msg, i) => (
          <div key={i} style={msg.sender === 'user' ? styles.userRow : styles.botRow}>
            {msg.sender === 'user' ? (
              <div style={styles.userBubble}>{msg.text}</div>
            ) : msg.error ? (
              <div style={styles.errorBubble}>{msg.error}</div>
            ) : (
              <div style={styles.diagCard}>
                <div style={styles.diagHeader}>
                  <span style={{ fontWeight: 800, color: 'var(--text)' }}>{msg.data.incident}</span>
                  <span style={{ ...styles.badge, ...tone(msg.data.confidence === '0%' ? 'err' : 'ok') }}>
                    {t('console.confidence')}: {msg.data.confidence}
                  </span>
                </div>
                <p style={{ margin: '0.85rem 0', color: 'var(--text)', fontSize: '0.95rem', lineHeight: 1.55 }}>{msg.data.analysis}</p>
                {msg.data.recommended_cli && (
                  <div style={styles.cliBox}>
                    <code style={{ color: 'var(--accent)', fontFamily: 'ui-monospace, monospace', fontSize: '0.88rem', fontWeight: 700, wordBreak: 'break-all' }}>
                      $ {msg.data.recommended_cli}
                    </code>
                    <button type="button" className="btn" onClick={() => copiar(msg.data.recommended_cli, i)} style={styles.copyBtn}>
                      {copiedIndex === i ? t('console.copied') : t('console.copyCli')}
                    </button>
                  </div>
                )}
              </div>
            )}
          </div>
        ))}

        {loading && (
          <div style={styles.botRow}>
            <div style={styles.loadingBubble}>{t('console.loading')}</div>
          </div>
        )}
      </div>

      <form onSubmit={enviar} style={styles.inputForm}>
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder={t('console.placeholder')}
          aria-label={t('console.placeholder')}
          style={styles.chatInput}
        />
        <button type="submit" disabled={loading} className="btn" style={styles.sendBtn}>
          {t('console.send')}
        </button>
      </form>
    </main>
  );
}
