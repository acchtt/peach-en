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
| 1 | Melon TOP100 | Official published chart observations; automation blocked by chart robots rules | Two timestamped historical snapshots |
| 2 | YouTube MV views | Official YouTube Data API `videos.list?part=statistics` | Connected, hourly collection |
| 3 | Apple Music KR Top Songs | Official Apple marketing RSS Top Songs (KR); captured snapshots, no chart-hour claims | Tested; automated capture |\n| 4 | Melon Daily/HOT100, Genie, Bugs, FLO | Only authorized reliable chart feeds; do not bypass robots restrictions | Not connected |
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


## Automatic Apple Music KR chart snapshots

The chart ID \`apple-music-kr-top-songs\` uses Apple's official RSS Builder:
https://rss.marketingtools.apple.com/ — feed
https://rss.applemarketingtools.com/api/v2/kr/music/most-played/100/songs.json

A live GitHub-runner test at 2026-10-27 01:12 KST returned 100 ranked songs and IVE's "Looks Can Kill" at position #2. **This test result is not a hardcoded website rank.** Production uses the collector to retrieve the feed again.

Apple Music most-played is a **separate chart**, not Melon/Genie/Bugs/FLO, Spotify, or Apple Music stream count. Its RSS response reports a dynamic \`updated\` field that appears to follow request time, so we do not use it as an official chart period. We record when the full feed was fetched, retain the RSS update metadata, and label rank values as **captured**. Never derive "hours in Top 10" from this collection.

Example schema (the position below is *illustrative*, not a claim about a chart period):

\`\`\`json
{
  "track_id": "looks-can-kill",
  "chart_id": "apple-music-kr-top-songs",
  "rank": 2,
  "movement": null,
  "collected_at": "2026-10-27T01:16:20+09:00",
  "feed_updated_at": "2026-10-27T01:16:19+09:00",
  "source_url": "https://rss.applemarketingtools.com/api/v2/kr/music/most-played/100/songs.json",
  "song_url": "https://music.apple.com/kr/album/looks-can-kill/6820421860?i=6820422075",
  "song_id": "6820422075",
  "verification": "official-apple-rss"
}
\`\`\`

The collector verifies country code, 100 unique ranked song IDs, exact Apple song ID and IVE artist/title, and Apple's song link. Source/identity checks fail closed. The collection time is KST. Rank movement stays null because the RSS does not publish movement. If the exact track is missing, status remains **unavailable**, not falsely reported out of the chart.

Official RSS website-use guidance: https://performance-partners.apple.com/tools

All four service-specific chart robots checks disallowed the experimental bot:
- https://www.melon.com/robots.txt
- https://www.genie.co.kr/robots.txt
- https://music.bugs.co.kr/robots.txt
- https://www.music-flo.com/robots.txt

These results are for the examined chart URLs and our bot, not a determination of license rights for every kind of data reuse.


## Additional Apple Music KR most-played album tracking

The album chart is **not album sales**. The public Apple marketing RSS feed is https://rss.applemarketingtools.com/api/v2/kr/music/most-played/100/albums.json, chart ID apple-music-kr-top-albums. The linked IVE EP has Apple KR album ID 6820421860. Collect only a complete 100-entry feed with 100 unique IDs, matching KR country, exact title/artist/album ID and a music.apple.com source URL. Missing target ID means **no observed rank**; never backfill rank 101 or uncharted.

The record belongs to album_chart_observations[] (not songs' observations[] or numeric album_sales[]) and contains track_id, chart_id, album_id, rank, movement:null, collected_at, feed_updated_at, source_url, album_url, verification:official-apple-rss. Duplicate UTC sample-hours are prohibited. Capture times are KST; updated is RSS metadata and **not** a provider-declared chart reporting period.

### Circle Chart

See [CIRCLE.md](CIRCLE.md). Its Digital, Streaming and Album chart categories have distinct meanings, largely weekly reporting periods. Site data holds source links only and **no scraped Circle observations** because authorized collection has not been established. Charts remain unavailable until licensed or manually verified, separately from this Apple Music KR album-ranking feed.
