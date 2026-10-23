/* Sync the no-import browser locale adapter with its canonical JSON dictionary.
 * Usage: node scripts/sync_peach_ui_labels.mjs [--check]
 * The adapter must stay self-contained for the unauthenticated login/setup shell.
 */
import { readFileSync, writeFileSync } from 'node:fs';
import { resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const root = fileURLToPath(new URL('..', import.meta.url));
const catalogPath = resolve(root, 'web/peach-ui-en.json');
const adapterPath = resolve(root, 'web/peach-locale.js');
const catalog = JSON.parse(readFileSync(catalogPath, 'utf8'));
if (typeof catalog !== 'object' || catalog === null || Array.isArray(catalog)) {
  throw new Error('Expected a dictionary of translated UI strings');
}
for (const [key, value] of Object.entries(catalog)) {
  if (!key || typeof value !== 'string' || !value) throw new Error(`Bad UI translation key: ${key}`);
}
const current = readFileSync(adapterPath, 'utf8');
const start = '  const translations = ';
const end = ';\n  const locale = (() => {';
const from = current.indexOf(start);
const to = current.indexOf(end, from + start.length);
if (from < 0 || to < 0 || current.indexOf(start, from + start.length) !== -1) {
  throw new Error('Localization adapter dictionary boundaries changed');
}
const expected = current.slice(0, from) + start + JSON.stringify(catalog, null, 2) + current.slice(to);
if (process.argv.includes('--check')) {
  if (expected !== current) {
    console.error('Locale adapter is out of sync. Run: node scripts/sync_peach_ui_labels.mjs');
    process.exitCode = 1;
  } else {
    console.log(`Verified ${Object.keys(catalog).length} translated interface strings`);
  }
} else {
  writeFileSync(adapterPath, expected);
  console.log(`Synced ${Object.keys(catalog).length} translated interface strings`);
}
