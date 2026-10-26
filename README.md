# IVE RADAR ★ Current Comeback Headquarters

An unofficial, free, single-comeback fan chart tracker, inspired by the pop-art visual language of IVE Hero Office. No connection to IVE, Starship, or the reference site's owners.

## Status
**Public design preview.** No chart API, collector, or authorized source feed has been integrated yet. Ranking cards intentionally display “—” rather than invented data. Only publish verified observations with correct reporting timestamps.

## Deployment
The site is built without a bundler. GitHub Pages is deployed from the `master` branch by `.github/workflows/pages.yml`; automatic enablement is requested in the workflow.

## Data
Edit `data.json` to provide verified data. Each observation should be traceable to a source. Sources use IDs `melon-top100`, `melon-daily`, `melon-hot100`, `genie-realtime`, `bugs-realtime`, and `flo-realtime`. History entries require `source`, `timestamp`, and numeric `rank`. Null means unavailable, not zero. Track streaming and music-show results only when verification is available.

## Scope
IVE’s current comeback only: Melon, Genie, Bugs, FLO, album track data, YouTube/Spotify/Hanteo, and music shows.

## Previous project recovery
The prior Peach EN repository contents are preserved on branch `archive/peach-en-before-ive-radar-20261026`, pointing to original commit `de22796c04919aaa057d77930c33c81313765569`.

## Disclaimer
This site is not an official IVE, Starship, ChartRadar, or IVE Hero Office property.
