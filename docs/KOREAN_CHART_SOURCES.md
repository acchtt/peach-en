# Korean chart sources and provenance

The project uses these independently identified data feeds:
- First-party Melon MCP (https://mcp.melon.com/mcp/): only IVE song rank captures, with collected_at KST and exact song ID 603448999; NOT an authenticated provider reporting-hour timestamp.
- Apple Music KR official marketing RSS: song and most-played album capture data. Album ranking is NOT sales.
- YouTube Data API v3: cumulative official MV views; provider API key held in GitHub Actions secrets.

The project DOES NOT scrape Guyso (https://xn--o39an51b2re.com/), whose robots rules disallowed the research bot. It is linked as an external historical reference. Genie, Bugs, FLO and Circle chart rankings remain unavailable without a permitted feed. Do not fabricate values.

## Melon collector controls

The workflow runs at UTC minute 13 hourly, subject to GitHub scheduling delays. The collector records at most one TOP100 capture per KST hour, one Daily capture per day, and one Weekly capture per seven days. No authentication or account data is used. Other chart services continue if Melon fails.

Old source-verified records use observed_at for published periods; automatic MCP samples use collected_at for retrieval. Both have a time label in the interface. Do not treat sparse captures as complete charted-hour totals.

Provider rights to automated public redistribution are not confirmed by endpoint access alone; attribution and reviewing source terms remain important. To disable this source without disrupting the others, remove or disable the Melon capture step from .github/workflows/pages.yml.
