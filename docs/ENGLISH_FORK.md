# Peach English fork — first localization pass

This fork preserves Peach's original Chinese source copy and media handling. The user interface
defaults to **English (en-US)**; **简体中文 (zh-CN)** remains available through the language
selector in the top toolbar.

## Implementation
- `frontend/src/i18n.ts`: typed language state and localized configuration copy.
- `web/peach-locale.js`: a dependency-free, exact-match translation dictionary for
  288 reviewed Chinese interface labels, including navigation, search, playback,
  settings, filtering, actions and accessibility attributes.
- `web/index.html`: persistent language selector, loaded before application bundles.
- `src/peach/routes_pages.py`: explicitly serves the static locale adapter, including
  before sign-in.
- `frontend/test/peach-locale.test.ts`: checks language selection, async content
  translation and preservation of work titles.

## Boundaries
**This is a first-pass UI translation, not yet complete English coverage.**
Unrecognized strings, longer descriptions, complex messages, server-originated
error messages and some onboarding labels may still be Chinese. New UI strings
should be localized directly at source via `t()` rather than expanding the
compatibility adapter indefinitely.

The adapter only translates exact reviewed labels in DOM text and common control
attributes. It does not translate arbitrary text, video titles, performer names,
file names, private library data or API responses. It leaves content in media
cards untouched except recognized action controls. React may replace translated
DOM text during rendering; a throttled observer reapplies those labels. Avoid
relying on modified text content as application state.

Changing language persists `peach-ui-locale` in browser localStorage and
**reloads the page** to avoid stale imported strings. It does not alter Peach
server settings or the user's library.

## Use and validation
1. Check out this branch; do not use upstream release executables, which
   do not include this fork's new files.
2. Build and run using the upstream instructions in `README.en.md`.
3. Open the web UI and select **English** or **中文** at the top.
4. Run `npm --prefix frontend ci`, then `npm --prefix frontend run typecheck`,
   `npm --prefix frontend test`, and `npm --prefix frontend run build`.
5. Run Python/web tests using the repository's documented testing instructions.

## Next pass
Extract a complete English/Chinese dictionary for the React and server-rendered
views; replace DOM-time translations with source-level `t()` calls and reactive
subscriptions. Audit remaining untranslated UI, especially the first-run wizard,
diagnostics and long notifications. Do not label this fork 'fully localized' until
those tests and visual reviews pass.
