import { useState } from 'react';
import TurnstileWidget from '../components/TurnstileWidget';
import { useAuth } from '../context/AuthContext';
import { useSettings } from '../context/SettingsContext';
import { apiFetch, mensajeDeError } from '../services/api';
import { styles } from '../styles/styles';

const USERNAME_RE = /^[A-Za-z0-9_.-]{3,30}$/;
const EMAIL_RE = /^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$/;
const passwordValida = (p) => p.length >= 8 && p.length <= 72 && /[A-Za-z]/.test(p) && /\d/.test(p);

// Modos: 'login' | 'register' | 'forgot' | 'reset'
export default function AuthPage() {
  const { login } = useAuth();
  const { t, lang, theme } = useSettings();

  const [mode, setMode] = useState('login');
  const [username, setUsername] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirm, setConfirm] = useState('');
  const [code, setCode] = useState('');
  const [captcha, setCaptcha] = useState(null);
  const [captchaReset, setCaptchaReset] = useState(0);
  const [captchaFailed, setCaptchaFailed] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [notice, setNotice] = useState(null);

  const needsCaptcha = mode !== 'reset';

  const goTo = (nextMode, message = null) => {
    setMode(nextMode);
    setError(null);
    setNotice(message);
    setPassword('');
    setConfirm('');
    setCode('');
    setCaptchaFailed(false);
  };

  const validar = () => {
    if (mode === 'register') {
      if (!USERNAME_RE.test(username.trim())) return t('auth.errors.usernameInvalid');
      if (!EMAIL_RE.test(email.trim())) return t('auth.errors.emailInvalid');
      if (!passwordValida(password)) return t('auth.errors.passwordWeak');
      if (password !== confirm) return t('auth.errors.passwordMismatch');
    }
    if (mode === 'forgot' && !EMAIL_RE.test(email.trim())) return t('auth.errors.emailInvalid');
    if (mode === 'reset') {
      if (!EMAIL_RE.test(email.trim())) return t('auth.errors.emailInvalid');
      if (!/^\d{6}$/.test(code.trim())) return t('auth.errors.codeInvalid');
      if (!passwordValida(password)) return t('auth.errors.passwordWeak');
      if (password !== confirm) return t('auth.errors.passwordMismatch');
    }
    if (needsCaptcha && !captcha) return t('auth.captchaRequired');
    return null;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);
    setNotice(null);
    const problema = validar();
    if (problema) {
      setError(problema);
      return;
    }

    setLoading(true);
    try {
      if (mode === 'login') {
        const data = await apiFetch('/auth/login', {
          method: 'POST', lang,
          body: { username, password, turnstile_token: captcha },
        });
        login(data.access_token);
        return;
      }
      if (mode === 'register') {
        const data = await apiFetch('/auth/register', {
          method: 'POST', lang,
          body: { username: username.trim(), email: email.trim(), password, turnstile_token: captcha },
        });
        goTo('login', data.message);
      } else if (mode === 'forgot') {
        const data = await apiFetch('/auth/forgot-password', {
          method: 'POST', lang,
          body: { email: email.trim(), turnstile_token: captcha },
        });
        goTo('reset', data.message);
      } else if (mode === 'reset') {
        const data = await apiFetch('/auth/reset-password', {
          method: 'POST', lang,
          body: { email: email.trim(), code: code.trim(), new_password: password },
        });
        goTo('login', data.message);
      }
    } catch (err) {
      setError(mensajeDeError(err, t));
    } finally {
      setLoading(false);
      setCaptchaReset((n) => n + 1); // el token de Turnstile solo sirve una vez
    }
  };

  const titulo = { login: 'auth.login.title', register: 'auth.register.title', forgot: 'auth.forgot.title', reset: 'auth.reset.title' }[mode];
  const submitKey = { login: 'login', register: 'register', forgot: 'forgot', reset: 'reset' }[mode];

  const campo = (id, label, props) => (
    <div style={styles.fieldGroup}>
      <label htmlFor={id} style={styles.label}>{label}</label>
      <input id={id} style={styles.input} required {...props} />
    </div>
  );

  return (
    <div style={styles.authPage}>
      <div style={styles.authCard}>
        <div style={styles.logoBadge}>{t('app.badge')}</div>
        <h2 style={styles.title}>SentinelOps</h2>
        <p style={styles.subtitle}>{t('app.subtitle')}</p>

        <h3 style={styles.modeTitle}>{t(titulo)}</h3>
        {mode === 'forgot' && <p style={{ ...styles.hint, marginBottom: '1rem' }}>{t('auth.forgot.intro')}</p>}
        {mode === 'reset' && <p style={{ ...styles.hint, marginBottom: '1rem' }}>{t('auth.reset.intro')}</p>}
        {mode === 'register' && <p style={{ ...styles.hint, marginBottom: '1rem' }}>{t('auth.register.info')}</p>}

        <form onSubmit={handleSubmit} style={styles.form} noValidate>
          {notice && <div style={styles.successBox} role="status">{notice}</div>}
          {error && <div style={styles.errorBox} role="alert">{error}</div>}

          {mode === 'login' && (
            <>
              {campo('username', t('auth.login.username'), { type: 'text', value: username, onChange: (e) => setUsername(e.target.value), placeholder: t('auth.login.usernamePh'), autoComplete: 'username' })}
              {campo('password', t('auth.login.password'), { type: 'password', value: password, onChange: (e) => setPassword(e.target.value), placeholder: t('auth.login.passwordPh'), autoComplete: 'current-password' })}
            </>
          )}

          {mode === 'register' && (
            <>
              <div>
                {campo('r-username', t('auth.register.username'), { type: 'text', value: username, onChange: (e) => setUsername(e.target.value), placeholder: t('auth.register.usernamePh'), autoComplete: 'username' })}
                <p style={{ ...styles.hint, marginTop: '0.3rem' }}>{t('auth.register.usernameHint')}</p>
              </div>
              {campo('r-email', t('auth.register.email'), { type: 'email', value: email, onChange: (e) => setEmail(e.target.value), placeholder: t('auth.register.emailPh'), autoComplete: 'email' })}
              <div>
                {campo('r-password', t('auth.register.password'), { type: 'password', value: password, onChange: (e) => setPassword(e.target.value), autoComplete: 'new-password' })}
                <p style={{ ...styles.hint, marginTop: '0.3rem' }}>{t('auth.register.passwordHint')}</p>
              </div>
              {campo('r-confirm', t('auth.register.confirm'), { type: 'password', value: confirm, onChange: (e) => setConfirm(e.target.value), autoComplete: 'new-password' })}
            </>
          )}

          {mode === 'forgot' &&
            campo('f-email', t('auth.forgot.email'), { type: 'email', value: email, onChange: (e) => setEmail(e.target.value), placeholder: t('auth.register.emailPh'), autoComplete: 'email' })}

          {mode === 'reset' && (
            <>
              {campo('x-email', t('auth.reset.email'), { type: 'email', value: email, onChange: (e) => setEmail(e.target.value), autoComplete: 'email' })}
              {campo('x-code', t('auth.reset.code'), { type: 'text', inputMode: 'numeric', maxLength: 6, value: code, onChange: (e) => setCode(e.target.value.replace(/\D/g, '')), placeholder: '000000', autoComplete: 'one-time-code' })}
              {campo('x-password', t('auth.reset.newPassword'), { type: 'password', value: password, onChange: (e) => setPassword(e.target.value), autoComplete: 'new-password' })}
              <p style={{ ...styles.hint, marginTop: '-0.6rem' }}>{t('auth.register.passwordHint')}</p>
              {campo('x-confirm', t('auth.reset.confirm'), { type: 'password', value: confirm, onChange: (e) => setConfirm(e.target.value), autoComplete: 'new-password' })}
            </>
          )}

          {needsCaptcha && (
            <div>
              <div style={{ ...styles.label, marginBottom: '0.4rem' }}>{t('auth.captchaLabel')}</div>
              <TurnstileWidget
                key={mode}
                theme={theme}
                language={lang}
                resetSignal={captchaReset}
                onToken={setCaptcha}
                onError={() => setCaptchaFailed(true)}
              />
              {captchaFailed && <p style={{ ...styles.hint, color: 'var(--err-text)', marginTop: '0.3rem' }}>{t('auth.captchaLoadError')}</p>}
            </div>
          )}

          <button type="submit" disabled={loading} className="btn" style={styles.primaryBtn}>
            {loading ? t(`auth.${submitKey}.loading`) : t(`auth.${submitKey}.submit`)}
          </button>
        </form>

        <div style={styles.linksRow}>
          {mode === 'login' ? (
            <>
              <button type="button" style={styles.linkBtn} onClick={() => goTo('forgot')}>{t('auth.login.forgotLink')}</button>
              <button type="button" style={styles.linkBtn} onClick={() => goTo('register')}>{t('auth.login.registerLink')}</button>
            </>
          ) : (
            <>
              <button type="button" style={styles.linkBtn} onClick={() => goTo('login')}>{t('auth.back')}</button>
              {mode === 'forgot' && (
                <button type="button" style={styles.linkBtn} onClick={() => goTo('reset')}>{t('auth.forgot.haveCode')}</button>
              )}
            </>
          )}
        </div>
      </div>
    </div>
  );
}
