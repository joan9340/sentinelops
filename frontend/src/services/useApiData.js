import { useCallback, useEffect, useState } from 'react';
import { apiFetch } from './api';

// Carga datos de la API al montar (y cuando cambian token o idioma). reload() vuelve a pedirlos.
export function useApiData(path, { token, lang } = {}) {
  const [state, setState] = useState({ data: null, loading: true });
  const [version, setVersion] = useState(0);

  useEffect(() => {
    let activo = true;
    apiFetch(path, { token, lang })
      .then((data) => activo && setState({ data, loading: false }))
      .catch((err) => {
        console.error(`Error cargando ${path}:`, err);
        if (activo) setState((s) => ({ ...s, loading: false }));
      });
    return () => {
      activo = false;
    };
  }, [path, token, lang, version]);

  const reload = useCallback(() => {
    setState((s) => ({ ...s, loading: true }));
    setVersion((v) => v + 1);
  }, []);

  return { data: state.data, loading: state.loading, reload };
}
