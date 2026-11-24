import { createContext, useCallback, useContext, useMemo, useState } from 'react';

const TOKEN_KEY = 'jwt_token';
const AuthContext = createContext(null);

// Decodifica el payload del JWT (base64url) para leer usuario, rol y expiración.
const parseJwt = (token) => {
  try {
    const base64 = token.split('.')[1].replace(/-/g, '+').replace(/_/g, '/');
    return JSON.parse(atob(base64));
  } catch {
    return null;
  }
};
const tokenVigente = (token) => {
  const p = parseJwt(token);
  return !!p && (!p.exp || p.exp * 1000 > Date.now());
};

export function AuthProvider({ children }) {
  const [token, setToken] = useState(() => {
    try {
      const guardado = localStorage.getItem(TOKEN_KEY);
      if (guardado && tokenVigente(guardado)) return guardado;
      localStorage.removeItem(TOKEN_KEY);
    } catch {
      /* sin almacenamiento */
    }
    return null;
  });

  const login = useCallback((nuevo) => {
    try { localStorage.setItem(TOKEN_KEY, nuevo); } catch { /* sin almacenamiento */ }
    setToken(nuevo);
  }, []);
  const logout = useCallback(() => {
    try { localStorage.removeItem(TOKEN_KEY); } catch { /* sin almacenamiento */ }
    setToken(null);
  }, []);

  const value = useMemo(() => {
    const payload = token ? parseJwt(token) : null;
    const role = payload?.rol || 'operador';
    return {
      token, login, logout, role,
      username: payload?.sub || 'usuario',
      isAdmin: role === 'admin' || role === 'superadmin',
      isSuperAdmin: role === 'superadmin',
    };
  }, [token, login, logout]);

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

// eslint-disable-next-line react-refresh/only-export-components
export const useAuth = () => useContext(AuthContext);
