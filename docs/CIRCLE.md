# IVE RADAR — Circle Chart feasibility

As of 2026-10-27 KST, **Circle Chart is not an automated source** for this fan website. The published Circle pages include an explicit restriction on unauthorized text/data mining (TDM). Our read-only GitHub Actions check received **HTTP 404 for robots.txt** on both circlechart.co.kr and circlechart.kr, which **does not grant chart collection permission**. We did not fetch or scrape ranking pages from the runner, and no Circle ranking has been ingested or invented.

Official chart references:
- Digital (weekly): https://circlechart.co.kr/page_chart/onoff.circle?serviceGbn=ALL
- Streaming (weekly): https://circlechart.co.kr/page_chart/onoff.circle?serviceGbn=S1040
- Album (weekly): https://circlechart.co.kr/page_chart/album.circle
- Chart definitions: https://circlechart.co.kr/page_community/faq.circle

**Never confuse categories.** Digital combines weighted streaming/downloads/BGM/V-coloring, Streaming uses streaming totals, and Album is based on physical-format wholesale distribution adjusted for returns. These rankings are **not hourly**. A title released October 26, 2026 cannot already have a verified 2026 week-44 Circle rank until Circle publishes the corresponding chart.

Next supported pathways:
1. Obtain explicit permission/partnership access from Circle for its chart data, API, or publisher feed; retain terms and verify permissible caching and redistribution.
2. Alternatively add individually sourced official weekly rankings by explicit human verification when published, documenting chart category, period identifier and source URL. Do **not** transform absence of a checked rank into "uncharted".
3. Keep Circle figures blank and link to the original weekly chart until one of the above is true.

The website keeps Circle's official source registry in data.json, with collection_status=permission-unconfirmed. This is **metadata only**, not an automated collector or a ranking claim.

## Official Apple Music KR Top 100 Albums feed

A separate, permitted public marketing RSS source is available:
https://rss.applemarketingtools.com/api/v2/kr/music/most-played/100/albums.json

That list measures *most-played albums*, **not album purchases, physical sales, or Circle Album shipments**. The "Looks Can Kill" EP has a confirmed Apple KR album ID of 6820421860, taken from its official Apple Music KR song page. A GitHub-hosted probe at 2026-10-27 01:39 KST returned a complete 100-entry album chart but **no exact matching EP**. This is a single feed capture, not proof that the EP never ranked.

The monitoring script checks 100 unique IDs, Korean country, artist/title/album-ID match, and the official source link. It stores only relevant exact EP positions when present in album_chart_observations[] with source, capture time and feed metadata; it does not store the full Top 100 or infer empty periods.

The dashboard's Album section separates Hanteo album **sales**, Circle weekly **wholesale shipments**, and Apple Music KR **most-played album ranking** in different tabs. Every unsupported rank remains an em dash. Existing YouTube and Apple Music KR song automation is unchanged.
