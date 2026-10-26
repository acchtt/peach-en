#!/usr/bin/env python3
"""IVE-only first-party Melon MCP chart capture.

Reads small portions of TOP100 / Daily / Weekly via Melon's official public
get_music_chart MCP tool. Never requests Guyso or Melon's robots-disallowed
HTML charts, account data, cookies, private APIs or OAuth tokens.

Captures are timestamped when obtained; they are NOT falsely presented as
provider-published hourly/daily/weekly chart periods. Only exact known IVE song
IDs are recorded. Source failures and missing matches do not imply 'uncharted'.
"""
from __future__ import annotations

import argparse
import ast
from datetime import datetime, timedelta, timezone
import io
import json
from pathlib import Path
import re
import sys
import time
import tokenize
import unicodedata
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
KST = ZoneInfo("Asia/Seoul")
MCP = "https://mcp.melon.com/mcp/"
AGENT = "IVERadarFanChartTracker/0.1 (+https://github.com/acchtt/peach-en)"
CHARTS = {
    "TOP_100": ("melon-top100", "https://www.melon.com/chart/index.htm"),
    "DAILY": ("melon-daily", "https://www.melon.com/chart/day/index.htm"),
    "WEEKLY": ("melon-weekly", "https://www.melon.com/chart/week/index.htm"),
}
MAX_RESPONSE_BYTES = 150_000
CHUNK = 30


class Unavailable(Exception):
    """No source-validated rank to publish."""


def normalize(value: str) -> str:
    return unicodedata.normalize("NFKC", value).strip().casefold()


def parse_chart_text(raw: str) -> dict:
    """Handle the MCP's Python-ish payload safely, without executing code."""
    if not isinstance(raw, str) or not 10 <= len(raw) <= 120_000:
        raise Unavailable("Missing or oversized MCP chart text")
    try:
        parsed = json.loads(raw)
    except ValueError:
        try:
            tokens = []
            for token in tokenize.generate_tokens(io.StringIO(raw).readline):
                if token.type == tokenize.NAME and token.string in ("true", "false", "null"):
                    rename = {"true": "True", "false": "False", "null": "None"}[token.string]
                    token = tokenize.TokenInfo(token.type, rename, token.start, token.end, token.line)
                tokens.append(token)
            parsed = ast.literal_eval(tokenize.untokenize(tokens))
        except (SyntaxError, ValueError, TypeError, tokenize.TokenError, RecursionError, MemoryError) as exc:
            raise Unavailable("Invalid MCP chart text") from exc
    if not isinstance(parsed, dict) or not isinstance(parsed.get("songs"), list):
        raise Unavailable("Chart result does not contain a song list")
    return parsed


def mcp_chart_page(chart_type: str, start: int, size: int) -> list:
    if chart_type not in CHARTS or not 1 <= start <= 100 or not 1 <= size <= 30:
        raise Unavailable("MCP chart arguments invalid")
    query = {
        "jsonrpc": "2.0", "id": 1, "method": "tools/call",
        "params": {"name": "get_music_chart", "arguments": {
            "chart_type": chart_type, "start": start, "size": size
        }},
    }
    request = Request(
        MCP, data=json.dumps(query).encode("utf-8"), method="POST",
        headers={
            "Content-Type": "application/json",
            "Accept": "application/json, text/event-stream",
            "User-Agent": AGENT,
        },
    )
    try:
        with urlopen(request, timeout=24) as response:
            if response.status != 200:
                raise Unavailable("Melon MCP returned unexpected HTTP status")
            media = response.headers.get("Content-Type", "").lower()
            payload = response.read(MAX_RESPONSE_BYTES + 1)
    except HTTPError as exc:
        raise Unavailable(f"Melon MCP HTTP {exc.code}") from exc
    except (URLError, TimeoutError, OSError) as exc:
        raise Unavailable("Melon MCP network unavailable") from exc
    if len(payload) > MAX_RESPONSE_BYTES:
        raise Unavailable("MCP response size exceeded limit")
    try:
        wire = payload.decode("utf-8")
        if "text/event-stream" in media:
            events = []
            for line in wire.splitlines():
                if line.startswith("data:"):
                    text = line[5:].strip()
                    if text.startswith("{"):
                        events.append(json.loads(text))
            if not events:
                raise Unavailable("MCP SSE result missing")
            rpc = events[-1]
        elif "json" in media:
            rpc = json.loads(wire)
        else:
            raise Unavailable("MCP content-type unexpected")
    except (ValueError, UnicodeDecodeError) as exc:
        raise Unavailable("MCP response could not be decoded") from exc
    if not isinstance(rpc, dict) or "error" in rpc or not isinstance(rpc.get("result"), dict):
        raise Unavailable("Melon returned an MCP tool error")
    result = rpc["result"]
    if result.get("isError"):
        raise Unavailable("Melon tool refused chart request")
    chunks = result.get("content", [])
    if not isinstance(chunks, list) or len(chunks) != 1 or chunks[0].get("type") != "text":
        raise Unavailable("Melon chart content missing")
    data = parse_chart_text(chunks[0].get("text", ""))
    songs = data["songs"]
    if len(songs) != size:
        raise Unavailable("Incomplete chart page, do not publish")
    seen_ids = set()
    actual_ranks = set()
    for item in songs:
        if not isinstance(item, dict) or not isinstance(item.get("rank"), dict):
            raise Unavailable("Invalid song row")
        song_id = item.get("song_id")
        if isinstance(song_id, bool) or not isinstance(song_id, int) or song_id <= 0:
            raise Unavailable("Song ID invalid")
        try:
            rank = int(item["rank"]["current_rank"])
        except (KeyError, ValueError, TypeError) as exc:
            raise Unavailable("Chart rank malformed") from exc
        if not start <= rank < start + size:
            raise Unavailable("Rank differs from requested chart page")
        if song_id in seen_ids or rank in actual_ranks:
            raise Unavailable("Duplicate song ID or rank")
        seen_ids.add(song_id)
        actual_ranks.add(rank)
    if len(actual_ranks) != size:
        raise Unavailable("Chart page incomplete")
    return songs


def find_ive(chart_type: str, *, expected_id: int, target_title: str):
    """Read at most four chart slices; never mistake a missing page for absence."""
    if chart_type not in CHARTS:
        raise Unavailable("Unsupported chart type")
    for start in (1, 31, 61, 91):
        size = min(CHUNK, 101-start)
        songs = mcp_chart_page(chart_type, start, size)
        matches = []
        for item in songs:
            if item["song_id"] != expected_id:
                continue
            title = normalize(item.get("song_name", ""))
            credits = item.get("artists", [])
            if not isinstance(credits, list):
                raise Unavailable("Artist credits missing")
            artists = {normalize(c.get("artist_name", "")) for c in credits if isinstance(c, dict)}
            if title != normalize(target_title) or not artists.intersection({
                "ive", "아이브", "ive (아이브)", "아이브 (ive)"
            }):
                raise Unavailable("Melon song ID exists but credits/title do not match IVE")
            matches.append(int(item["rank"]["current_rank"]))
        if len(matches) != 0:
            if len(matches) != 1:
                raise Unavailable("Ambiguous Melon song rank")
            return matches[0]
        if start < 91:
            time.sleep(0.25)
    return None


def should_capture(rows: list, chart_id: str, now: datetime) -> bool:
    history = [x for x in rows if x.get("chart_id") == chart_id and x.get("verification") == "official-melon-mcp-capture"]
    if not history:
        return True
    recent = max(datetime.fromisoformat(x["collected_at"]).astimezone(KST) for x in history)
    if now <= recent:
        return False
    if chart_id == "melon-top100":
        return now.strftime("%Y-%m-%dT%H") != recent.strftime("%Y-%m-%dT%H")
    if chart_id == "melon-daily":
        return now.date() != recent.date()
    return now - recent >= timedelta(days=7)


def make_observation(chart_type: str, *, rank: int, song_id: int, now: datetime) -> dict:
    chart_id, source = CHARTS[chart_type]
    if not 1 <= rank <= 100:
        raise Unavailable("Invalid rank outside chart")
    return {
        "track_id": "looks-can-kill",
        "chart_id": chart_id,
        "rank": rank,
        "movement": None,
        "collected_at": now.astimezone(KST).replace(microsecond=0).isoformat(),
        "source_url": source,
        "mcp_endpoint": MCP,
        "melon_song_id": song_id,
        "verification": "official-melon-mcp-capture",
        "note": "Rank captured via official Melon MCP at collection time, not verified as a published chart hour.",
    }


def collect(*, dry_run: bool = False, chart_types=None):
    path = ROOT / "data.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    tracks = [x for x in data["tracks"] if x["id"] == "looks-can-kill"]
    if len(tracks) != 1 or tracks[0].get("artist") != "IVE":
        raise Unavailable("Default IVE title track not found")
    track = tracks[0]
    song_id = track.get("melon_song_id")
    if isinstance(song_id, bool) or not isinstance(song_id, int) or song_id <= 0:
        raise Unavailable("Expected Melon song ID unavailable")
    rows = data["observations"]
    captures = []
    for chart_type in (chart_types or list(CHARTS)):
        if chart_type not in CHARTS:
            raise Unavailable("Unsupported chart type")
        now = datetime.now(KST)
        chart_id = CHARTS[chart_type][0]
        if not should_capture(rows, chart_id, now):
            captures.append({"chart": chart_id, "status": "ALREADY_CAPTURED_INTERVAL"})
            continue
        try:
            rank = find_ive(chart_type, expected_id=song_id, target_title=track["title"])
            if rank is None:
                captures.append({"chart": chart_id, "status": "NOT_IN_VERIFIED_PAGE_SET", "stored": False})
                continue
            obs = make_observation(chart_type, rank=rank, song_id=song_id, now=datetime.now(KST))
            rows.append(obs)
            captures.append({
                "chart": chart_id, "status": "WOULD_APPEND" if dry_run else "CAPTURED",
                "rank": rank, "collected_at": obs["collected_at"], "stored": not dry_run
            })
        except Unavailable as exc:
            captures.append({"chart": chart_id, "status": "SOURCE_UNAVAILABLE", "reason": str(exc)[:150]})
    if not dry_run and any(x.get("status") == "CAPTURED" for x in captures):
        rows.sort(key=lambda x: datetime.fromisoformat(x.get("collected_at") or x["observed_at"]).astimezone(timezone.utc))
        path.write_text(json.dumps(data, indent=2, ensure_ascii=False)+"\n", encoding="utf-8")
    print(json.dumps({"source": "first-party Melon MCP (not Guyso)", "results": captures}, ensure_ascii=False))
    return captures


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--chart", choices=list(CHARTS), action="append")
    args = parser.parse_args()
    try:
        collect(dry_run=args.dry_run, chart_types=args.chart)
    except (Unavailable, KeyError, ValueError, TypeError) as exc:
        print(json.dumps({"status": "COLLECTION_UNAVAILABLE", "reason": str(exc)[:150]}))
    return 0  # Preserve independent Apple and YouTube uploads on Melon outages.


if __name__ == "__main__":
    sys.exit(main())
