# Peach English localization fork

Peach's core functionality is preserved. This fork defaults to **English (`en-US`)**
and retains **Simplified Chinese (`zh-CN`)** as a user-selectable alternative.

## Current implementation

- `web/peach-ui-en.json` — canonical catalog of 390 reviewed Chinese-to-English
  interface labels. Strings used as content IDs or file names are left untouched.
- `frontend/src/i18n.ts` — source-level `uiText()`, `t()`, persistent locale choice.
- Source-level translation is wired into the primary sidebar, settings groups, login,
  setup, setup completion, and standalone error screens.
- Both the normal application toolbar and standalone login/setup/error pages expose
  a visible English / 简体中文 switcher.
- `web/peach-locale.js` — a transitional exact-match DOM adapter for remaining
  Chinese labels. It handles dynamic React text using a bounded MutationObserver;
  it does **not** translate arbitrary media metadata, filenames, names, or API data.
- `scripts/sync_peach_ui_labels.mjs` deterministically syncs that browser adapter
  with the canonical catalog; `--check` verifies byte-for-byte consistency.
- `src/peach/routes_pages.py` serves the adapter as an explicit public static
  asset so the login screen can use it before authentication.
- `src/peach/web_entry.py` includes the script in standalone page shells.

Language preference lives in localStorage under `peach-ui-locale`. Switching language
reloads the current view to avoid stale module-level labels. It does not change
Peach account settings, metadata, files, or the local library.

## Tests and verification

Use the **Peach English localization** GitHub Actions workflow, or locally:

```sh
node scripts/sync_peach_ui_labels.mjs --check
node --check web/peach-locale.js
npm --prefix frontend ci
npm --prefix frontend run typecheck
npm --prefix frontend test
npm --prefix frontend run build
```

The source-level English tests are `frontend/test/i18n.test.ts` and
`frontend/test/peach-locale.test.ts`. The inherited upstream tests run under
`zh-CN`, preserving their original Chinese string assertions, while dedicated
tests explicitly check the English default and translations.

## Windows builds

Windows packaging already invokes the frontend build and bundles the entire `web/`
folder, including the language assets. **Upstream Peach installers will not contain
this fork's English translations.**

To build a candidate from GitHub when checks pass, enable GitHub Actions for
`acchtt/peach-en`, choose **Actions → Release → Run workflow**, select the tested
fork branch, and retrieve the `desktop-candidate` artifact after the Windows build
and smoke tests complete. The project creates unsigned test packages.

Do not publish or promote a release before the Windows installer, installed
application, and portable package have been smoke-tested. A workflow artifact is
not, by itself, proof that all localization screens are complete.

## Outstanding work

**The app is not fully translated.** Some longer help text, API error messages,
complex notifications, and specialized screens may still display Chinese.
The DOM adapter is a compatibility bridge, not the final architecture. The durable
design is to migrate every remaining interface string into source-level `uiText()`
and contextual translation keys with locale-aware rendering, then remove the
observer once coverage and cross-platform testing are complete.
