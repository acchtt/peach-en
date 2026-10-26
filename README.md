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

## Automatic website updates

Visitors' browsers now refresh the published static data file every **5 minutes** while the tab is visible. A GitHub Actions workflow is scheduled hourly at minute 13 (UTC). It collects only supported official API data, validates it, commits new records and deploys the static site in the *same* workflow run. GitHub scheduled jobs may be delayed; this is not guaranteed live to the minute.

**Supported automatic source:** The official IVE "Looks Can Kill" music video cumulative public view count from **YouTube Data API v3**, confirmed Starship MV video ID: https://youtu.be/rsNhWkC4neE. This is not a YouTube Music chart position, unique stream count or hour-by-hour official reporting period. The captured time is the collector retrieval time.

**One-time activation:** In Google Cloud, enable the YouTube Data API v3 and create an API key with that API restricted. In the GitHub repository open **Settings → Secrets and variables → Actions → New repository secret**. Set the name to YOUTUBE_DATA_API_KEY and paste the key. Never put the key in repository files or chat. Test with **Actions → Deploy IVE RADAR to GitHub Pages → Run workflow**. Without the key the scheduled collector safely skips and the site shows no unverified view count.

**Melon is NOT automatically polled.** A direct Melon TOP100 collector was tested from GitHub Actions and rejected by Melon's robots rules. It remains solely on the experimental branch demo/automatic-chart-collection; it is not merged or scheduled. The current Melon snapshots on the website remain historical until a permitted, verified new observation is available.

Hourly runs with no new observations do not unnecessarily redeploy Pages. Changes made by the default GITHUB_TOKEN don't trigger a second push workflow, so the scheduled job deploys after its own commit.


## Apple Music Korea Top Songs (official RSS)

The first fully tested, public **Korea-market ranking feed** is Apple's marketing RSS generator. It is separate from Melon TOP100, Genie, Bugs, and FLO. Apple offers this feed specifically for putting top-music lists on websites:

- RSS URL: https://rss.applemarketingtools.com/api/v2/kr/music/most-played/100/songs.json
- Official chart: **Apple Music KR Top Songs / most-played**.
- IVE title track has Apple song ID \`6820422075\`.
- The app displays **captured rank snapshots** and an observed peak. It does not call these "realtime", "daily", or Apple-published hourly ranks.
- Feed \`updated\` appears to refresh per request and is saved as metadata, **not** treated as a chart reporting period. \`collected_at\` is the actual source capture timestamp.
- The collector runs on the existing hourly GitHub Actions schedule. It records rank changes immediately, and otherwise records a stable rank at most once every 3 hours, avoiding fake hourly rank continuity.
- If the RSS is blocked, malformed, missing the exact track, or inconsistent, no rank is created. No out-of-chart claim is made.
- Every card links to Apple Music; only metadata about the tracked IVE track is retained, not the full Top 100 feed.

**Access investigation (26 Oct 2026):** The current public chart URLs for Melon, Genie, Bugs, and FLO were each disallowed by their robots.txt for the chart bot. We did not bypass those rules. Apple RSS was accessible in live GitHub Actions probes, though intermittent timeouts can occur. The historical Melon source data and YouTube API continue independently.
