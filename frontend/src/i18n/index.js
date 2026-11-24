import es from './es';
import en from './en';

export const DICTIONARIES = { es, en };
export const LANGUAGES = ['es', 'en'];

// translate('es', 'auth.login.title', { x: 1 }) -> texto; reemplaza {x} por el valor.
// Si falta la clave en el idioma elegido, usa español; si tampoco existe, devuelve la clave.
export function translate(lang, key, vars) {
  const walk = (dict) => key.split('.').reduce((node, part) => (node == null ? undefined : node[part]), dict);
  let value = walk(DICTIONARIES[lang]);
  if (value === undefined) value = walk(DICTIONARIES.es);
  if (value === undefined) return key;
  if (typeof value === 'string' && vars) {
    return value.replace(/\{(\w+)\}/g, (_, name) => (vars[name] !== undefined ? vars[name] : `{${name}}`));
  }
  return value;
}
