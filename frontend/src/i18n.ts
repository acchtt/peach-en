/** Peach English fork: lightweight, dependency-free interface localization. */
export type Locale = 'en-US' | 'zh-CN';
const STORAGE_KEY = 'peach-ui-locale';
const messages = {
  'entryLinks.help': {
    'en-US': 'If JavDB or MISSAV is unavailable, enter an accessible mirror domain.',
    'zh-CN': 'JavDB 或 MISSAV 打不开时，填一个能打开的镜像域名。',
  },
  'entryLinks.hint': {
    'en-US': 'Enter a domain only; leave blank to use the default address',
    'zh-CN': '只填域名，留空用默认地址',
  },
} as const;
export type MessageKey = keyof typeof messages;
let currentLocale: Locale = 'en-US';
try {
  const saved = globalThis.localStorage?.getItem(STORAGE_KEY);
  if (saved === 'en-US' || saved === 'zh-CN') currentLocale = saved;
} catch { /* Private browsing or restricted storage: use English. */ }
export function getLocale(): Locale { return currentLocale; }
export function setLocale(locale: Locale): void {
  currentLocale = locale;
  try { globalThis.localStorage?.setItem(STORAGE_KEY, locale); } catch { /* nonpersistent */ }
  if (typeof document !== 'undefined') {
    document.documentElement.lang = locale;
    document.dispatchEvent(new CustomEvent('peach:locale-changed', { detail: locale }));
  }
}
export function t(key: MessageKey, locale: Locale = currentLocale): string {
  return messages[key][locale];
}
