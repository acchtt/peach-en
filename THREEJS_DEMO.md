# IVE RADAR — Three.js Hero Demo

**Branch:** `demo/threejs-hero` — not merged to production.

This demo enhances the existing comic-style homepage with a decorative 3D scene: stars, record tokens, bolts, and rings.

## Implementation

- Existing text, CTA, charts, ranks, and navigation remain semantic HTML/SVG.
- Rendered only on WebGL2-capable browsers with no reduced-motion preference.
- Pinned Three.js 0.180.0 dynamically imported from jsDelivr; no paid APIs or build tools.
- Mouse parallax; 30fps render limit; pixel ratio capped to 1.5.
- Pause/play toggle; stops offscreen and on hidden tabs.
- Static fallback: CDN failure, WebGL2 unsupported, or prefers-reduced-motion.
- Demo QA workflow captures desktop/mobile previews (when headless Chrome is available).

## Run locally

Run `python -m http.server 8000`, then visit `http://localhost:8000`.

## Review before merge

Check rendering on mobile, reduced motion, keyboard focus and toggle, fallback when CDN blocked, and that chart data stays unavailable until verified.

**Do not merge or publish to production without approval.**

Three.js (MIT): https://threejs.org/
