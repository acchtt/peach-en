# IVE RADAR — Verified statistics contract (v2)

The source of truth is `data.json`. This is a single-comeback fan tracker, **not** an official real-time service.

## Observation schema

Append-only list `observations[]`:

```json
{
  "track_id": "looks-can-kill",
  "chart_id": "melon-top100",
  "rank": 6,
  "movement": 1,
  "observed_at": "2026-10-26T20:00:00+09:00",
  "source_url": "https://www.melon.com/chart/index.htm",
  "verification": "official-chart-snapshot"
}
```

Rank `6` means position #6 in the exact named chart and reporting period, not a popularity score. Positive `movement` means **rose** by that many places, negative means fell. Each observation must map to a listed track and chart. `observed_at` is the **chart's published time**, not when a worker downloaded it. Verify the official source independently before recording. Do not extrapolate unobserved periods.

`charts[]` keeps the platform, market, actual chart label, cadence and source URL. Ranking graphs never combine different chart types (e.g., Melon TOP100 vs HOT100, or Spotify Global vs Korea). All times are rendered KST to prevent date drift.

## Metric rules

- Latest observed rank: latest **verified timestamp** in the selected series. May be stale.
- Observed peak: minimum rank among recorded observations only; never call this the full-career or full-era peak without complete historical coverage.
- Movement: use the chart's published delta when provided; do not infer from sparse snapshots across different periods.
- Hour counts (Top 10/20/50) and consecutive hours: **unavailable** until hourly coverage is complete and frequency verified.
- Charted days: count unique dates **observed** only, not the provider's full discography statistics.
- Uncharted vs missing: an absent observation is **unknown**, not proof the track missed the chart. Explicitly record out-of-chart only when the full source chart was checked.
- Music-show predictions are not verified results. Never show invented scores, forecasts, or wins as facts.

## Collection plan at $0/mo

| Priority | Source | Realistic method | Status |
|---|---|---|---|
| 1 | Melon TOP100 | Official chart page, timestamped observations; verify access and reuse terms before scheduled automation | One manually verified snapshot |
| 2 | YouTube MV views | Official YouTube Data API `videos.list?part=statistics` with a free API key (video ID confirmed first) | Not connected |
| 3 | Melon Daily/HOT100, Genie, Bugs, FLO | Source-specific collectors **only if** allowed and reliably accessible; fail closed and log blocked attempts | Not connected |
| 4 | Hanteo / Circle | Authorized publicly accessible releases/official reported counts; label periods and avoid guessing sales | Not connected |
| 5 | Spotify | Chart rankings only from an authorized accessible chart feed; Spotify Web API track popularity is NOT stream count | Not connected |
| 6 | Music shows | Official published winner/nominee results and score breakdowns, manual verification initially | Not connected |

GitHub Actions can run collection jobs for a public repository within free limits once an allowed/reliable source has been tested. Store credentials in GitHub secrets only, never in browser JS or committed JSON. Do not imply that `charts.spotify.com` can be scraped anonymously (it may require login). Treat platform page design, API availability, and redistribution rights as separate constraints.

## Validation and publication

Run `python3 scripts/validate_data.py` before commit. A future collector workflow should validate, append, deduplicate by `(track_id, chart_id, observed_at)`, then publish a single small JSON diff. Do not backfill fabricated history. Preserve Git commit provenance per snapshot.

## Source references

- Official Melon TOP100: https://www.melon.com/chart/index.htm
- Melon FAQ chart method: https://help.melon.com/web/faq/content.htm?faqId=QUES20160825000007
- YouTube Data API videos: https://developers.google.com/youtube/data/reference/rest/v3/videos/list
- Spotify Web API track details (no stream-count field): https://developer.spotify.com/documentation/web-api/reference/get-track
- IVE official artist page: https://www.starship-ent.com/musician/ive

## YouTube MV counter: official API, separate metric

The collector calls the YouTube Data API videos.list endpoint with the confirmed Starship MV video ID and fetches the public viewCount from statistics. It verifies title, channel and ID before appending a sample. The schema for streaming[] is:

- track_id: looks-can-kill
- platform: YouTube
- metric: view_count
- video_id: rsNhWkC4neE
- value: official nonnegative integer public view count
- collected_at: timezone-aware ISO 8601 timestamp when the API request completed
- source_url: official YouTube watch URL
- verification: youtube-data-api-v3

The view count is cumulative, not a song-chart rank or the number of views gained in the last hour. The API supplies no chart reporting timestamp for that counter; never label collected_at as a published reporting period. YouTube may adjust the counter, so later readings are not required to increase monotonically. One sample per UTC hour is allowed.

Enable by adding the YOUTUBE_DATA_API_KEY Actions secret. The web client never receives that key. GitHub Actions runs hourly and commits validated changes before performing the Pages deployment in the same run.

Melon's robots.txt prohibits our chart collector in its GitHub-hosted test. Do not bypass access restrictions. Continue storing manually verified published Melon chart snapshots with exact KST time until an authorized reliable feed is available.
