# Official Melon MCP feasibility — IVE RADAR

Status (2026-10-27 KST): **tested successfully as a research prototype; not integrated into production chart publication.**

## Confirmed live on GitHub Actions

- First-party Kakao Entertainment service: https://mcp.melon.com/mcp/
- Public MCP discovery through JSON-RPC tools/list returned 18 named tools over SSE.
- The chart tool is get_music_chart. Its chart_type values include TOP_100, DAILY, WEEKLY, HOT_100 and specialized HOT_TRACK types.
- Optional parameters: start 1..100, size 1..30, hot_100_filter D30/D100 for HOT_100.
- A one-off tools/call for TOP_100, start=1, size=10 returned HTTP 200, result isError=false, with Melon song IDs, ranks, artist credits and titles without authentication.
- Follow-up TOP_100, start=11, size=10 at 2026-10-27 02:14 KST returned an exact match for IVE Looks Can Kill, rank #12 and Melon song ID 603448999. This is a *retrieval-time* observation, not a provider-verified chart-hour snapshot, and is deliberately NOT included in production data.json.
- The returned tool-content string was Python-like dictionary syntax rather than strict JSON. The test adapter uses tokenize + ast.literal_eval, never arbitrary eval.
- The inspected payload did not include an identifiable official chart reporting timestamp. Retrieval time must not be misrepresented as the chart's published hour.
- This test downloaded no personal account data, registered no OAuth app and made no modifications to data.json.

Workflow: https://github.com/acchtt/peach-en/actions/workflows/qa-melon-mcp.yml

## OAuth and access

The public official metadata https://cola.melon.com/.well-known/oauth-authorization-server reports:
- Authorization: https://cola.melon.com/auth/v3/oauth/authorize
- Tokens: https://cola.melon.com/auth/v3/oauth/token
- Registration: https://cola.melon.com/auth/v3/oauth/register
- Supported grants: authorization_code and refresh_token (no client_credentials advertised).

Published Melon MCP integration information discusses per-partner redirect-URI allowlisting. Our anonymous chart call succeeding does not prove user-library tools can run without OAuth, nor that a scheduled public redistribution service is permitted.

Sources:
- https://tech.kakaoent.com/ai/using-melon-mcp-server-en/
- https://claude.com/marketplace/connectors/melon
- https://newsroom.kakaoent.com/terms-of-use/

Melon's terms restrict copying or distributing information obtained from Melon services without prior consent. The ability to call an endpoint is not a blanket redistribution license.

## To activate official rankings on IVE RADAR

Obtain a confirmation from Kakao Entertainment permitting a public fan website to retrieve ONLY IVE chart rankings (TOP100, Daily, Weekly, HOT100), poll at most hourly, store timestamped rank history and display it with links/attribution. Ask for any required partner approval or OAuth setup, accepted rate limits, and official KST chart-period fields. Support email published in the Melon connector listing: melon_info@kakaoent.com.

A proposed inquiry:

Hello Melon MCP team,

We operate IVE RADAR (https://acchtt.github.io/peach-en/), a free, noncommercial fan dashboard tracking IVE music-chart rankings. We discovered your first-party Melon MCP service and get_music_chart tool. Can you confirm whether automated retrieval of only IVE ranks once per hour, retaining dated rank history and displaying it on a public noncommercial website with prominent Melon attribution and source links, is permitted? If so, do we need OAuth/partner enrollment, and what rate limits, reporting-time fields, retention restrictions or attribution conditions apply?

Thank you.

Do not send account credentials, login cookies or OAuth tokens by email.

## Project guardrails

Before production use:
1. Permission or published use terms supporting our precise reuse.
2. Chart timestamp handling: distinguish captured_at from provider-published observed_at; no fabricated elapsed-hour records.
3. Exact IVE artist and song IDs; pagination across chart ranks when necessary; mark missing results unknown, not uncharted.
4. Source failures preserve historical verified data, never claim current rank from an old result.
5. Never put access tokens in GitHub Pages/browser source.

The demo parser in scripts/melon_mcp_adapter.py deliberately sets publishable=false, does no network fetching itself and cannot append data.json. No scheduled Melon MCP polling has been enabled on master.
