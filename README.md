# IVE RADAR — The Chart Lab

A free and unofficial IVE-only comeback tracking website. Design approved from the Hero Office-inspired Chart Lab prototype, published as a GitHub Pages static site.

**Website:** https://acchtt.github.io/peach-en/

## What it shows

- Melon TOP100 and source-specific Korean chart snapshots for IVE's *Looks Can Kill* comeback.
- Ranking movement and history **only from verifiable observations**.
- Additional sections for streaming, album sales, and music shows; unavailable values stay `—` until a qualified source is integrated.
- Captured timestamps are in Korean Standard Time (KST; UTC+09:00).

**Important:** This is not a live chart API. Charts may be stale; the site explicitly labels their observation times. A rank like #6 represents a historical snapshot and is not automatically a lifetime peak or a current rank.

## Updating statistics

Edit `data.json` by appending a new `observations[]` entry with exact `track_id`, `chart_id`, `rank`, `observed_at` (with timezone), and an official `source_url`. Supported source definitions appear in `charts[]`. The site reads the data file at each page load; GitHub Pages deploys after a push to `master`.

See [docs/STATS.md](docs/STATS.md) for the data contract and collection roadmap. `python3 scripts/validate_data.py` checks validity and rejects untraceable or duplicate observations.

## Deployment

The existing `.github/workflows/pages.yml` deploys to Pages from `master`. No paid services, API calls from visitors, or bundler are required.

## Image provenance

The hero image was cropped from a video of [IVE Hero Office](https://ive-herooffice.com/) supplied by the user for this fan-site design. Rights in that promotional artwork belong to the original rightsholders. This project is unofficial, noncommercial and not affiliated with Starship Entertainment or IVE Hero Office. The image is not AI-generated.

## Recovery

The previous IVE RADAR version is preserved on branch `archive/ive-radar-pre-chart-lab-20261026`, and the earlier Peach EN project on `archive/peach-en-before-ive-radar-20261026`.