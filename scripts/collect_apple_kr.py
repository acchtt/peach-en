#!/usr/bin/env python3
"""Official Apple Music KR Top Songs marketing RSS snapshot collector.

Apple's public RSS feed is explicitly intended for incorporation in websites.
Capture-time observations are NOT Apple Music chart publication periods.
Fail closed on malformed/blocked responses, exact-ID ambiguity and timestamps.
"""
from __future__ import annotations
import argparse
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime
import json
from pathlib import Path
import re
import sys
import time
import unicodedata
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse, parse_qs
from urllib.request import Request, urlopen
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
URL = "https://rss.applemarketingtools.com/api/v2/kr/music/most-played/100/songs.json"
CHART_ID = "apple-music-kr-top-songs"
TRACK_ID = "looks-can-kill"
KST = ZoneInfo("Asia/Seoul")
USER_AGENT = "IVERadarChartMonitor/0.2 (+https://github.com/acchtt/peach-en)"


class Unavailable(Exception):
    """No trustworthy new chart observation was obtained."""


def normalize(value: str) -> str:
    return unicodedata.normalize("NFKC", value).strip().casefold()


def retrieve() -> dict:
    last_error = None
    for attempt in range(2):
        if attempt:
            time.sleep(2)
        try:
            request = Request(URL, headers={
                "User-Agent": USER_AGENT,
                "Accept": "application/json",
                "Cache-Control": "no-cache",
            })
            with urlopen(request, timeout=23) as response:
                if response.status != 200:
                    raise Unavailable(f"RSS HTTP {response.status}")
                body = response.read(1_000_000)
                if "json" not in response.headers.get("Content-Type", "").lower():
                    raise Unavailable("RSS did not return JSON")
                return json.loads(body)
        except (URLError, HTTPError, TimeoutError, OSError, json.JSONDecodeError, Unavailable) as exc:
            last_error = exc
    raise Unavailable(f"RSS request unavailable ({type(last_error).__name__})")


def parse_feed(payload: dict, *, song_id: str, collected_at: datetime) -> dict:
    if not isinstance(payload, dict):
        raise Unavailable("RSS result not an object")
    feed = payload.get("feed")
    if not isinstance(feed, dict) or feed.get("country", "").lower() != "kr":
        raise Unavailable("Not a Korea Apple Music feed")
    results = feed.get("results")
    if not isinstance(results, list) or len(results) != 100:
        raise Unavailable("RSS chart must contain exactly 100 ranked songs")
    ids = [str(item.get("id", "")) for item in results if isinstance(item, dict)]
    if len(ids) != 100 or any(not re.fullmatch(r"\d{4,}", item) for item in ids) or len(set(ids)) != 100:
        raise Unavailable("Duplicate or malformed chart song IDs")
    updated = feed.get("updated")
    if not isinstance(updated, str):
        raise Unavailable("Feed missing update metadata")
    try:
        updated_dt = parsedate_to_datetime(updated)
    except (ValueError, TypeError, IndexError) as exc:
        raise Unavailable("Unparseable RSS update metadata") from exc
    if updated_dt.tzinfo is None:
        raise Unavailable("RSS update metadata missing timezone")
    if updated_dt.astimezone(timezone.utc) - collected_at.astimezone(timezone.utc) > timedelta(minutes=10):
        raise Unavailable("RSS update metadata timestamp in future")
    found = [(i + 1, x) for i, x in enumerate(results) if str(x["id"]) == song_id]
    if len(found) != 1:
        raise Unavailable(f"Expected official song ID found {len(found)} times")
    rank, item = found[0]
    if normalize(item.get("name", "")) != normalize("Looks Can Kill"):
        raise Unavailable("Song ID title mismatch")
    if normalize(item.get("artistName", "")) not in {"ive", "아이브"}:
        raise Unavailable("Song ID artist mismatch")
    song_url = item.get("url", "")
    parsed = urlparse(song_url)
    if parsed.scheme != "https" or parsed.hostname != "music.apple.com":
        raise Unavailable("Song URL not on Apple Music")
    if parse_qs(parsed.query).get("i") != [song_id]:
        raise Unavailable("Song URL ID differs from chart song ID")
    return {
        "track_id": TRACK_ID,
        "chart_id": CHART_ID,
        "rank": rank,
        "movement": None,  # Apple marketing RSS does not supply rank movement.
        "collected_at": collected_at.astimezone(KST).replace(microsecond=0).isoformat(),
        "feed_updated_at": updated_dt.astimezone(KST).replace(microsecond=0).isoformat(),
        "source_url": URL,
        "song_url": song_url,
        "song_id": song_id,
        "verification": "official-apple-rss",
        "note": "Apple Music KR Top Songs RSS feed rank, captured during collection. Timestamp is NOT an hourly chart publication period.",
    }


def append_new(observation: dict, *, dry_run: bool = False) -> str:
    path = ROOT / "data.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    if data.get("schema_version") != 2:
        raise Unavailable("Unexpected data schema")
    if not any(chart["id"] == CHART_ID and chart["source_url"] == URL for chart in data["charts"]):
        raise Unavailable("Apple Music KR chart is not registered")
    points = [o for o in data["observations"] if o.get("chart_id") == CHART_ID and o.get("track_id") == TRACK_ID]
    points.sort(key=lambda o: datetime.fromisoformat(o["collected_at"]).astimezone(timezone.utc))
    if points:
        last = points[-1]
        last_time = datetime.fromisoformat(last["collected_at"])
        now_time = datetime.fromisoformat(observation["collected_at"])
        if now_time <= last_time:
            raise Unavailable("Capture time not later than existing sample")
        if last["rank"] == observation["rank"] and (now_time - last_time) < timedelta(hours=3):
            return "UNCHANGED_RANK_RECENTLY_SAMPLED"
    if not dry_run:
        data["observations"].append(observation)
        data["observations"].sort(
            key=lambda o: datetime.fromisoformat(o.get("collected_at") or o["observed_at"]).astimezone(timezone.utc)
        )
        path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return "WOULD_APPEND" if dry_run else "APPENDED"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    try:
        data = json.loads((ROOT / "data.json").read_text(encoding="utf-8"))
        track = next(t for t in data["tracks"] if t["id"] == TRACK_ID)
        song_id = track["apple_music_kr_song_id"]
        if not isinstance(song_id, str) or not re.fullmatch(r"\d{4,}", song_id):
            raise Unavailable("Official Apple Music song ID not configured")
        payload = retrieve()
        collected_at = datetime.now(KST)
        obs = parse_feed(payload, song_id=song_id, collected_at=collected_at)
        result = append_new(obs, dry_run=args.dry_run)
        print(json.dumps({
            "status": result,
            "chart": CHART_ID,
            "rank": obs["rank"],
            "captured_at": obs["collected_at"],
            "feed_update_metadata": obs["feed_updated_at"],
            "source": URL,
        }, ensure_ascii=False))
    except (Unavailable, KeyError, ValueError, TypeError) as exc:
        print(json.dumps({
            "status": "SOURCE_UNAVAILABLE",
            "reason": str(exc)[:180],
            "chart": CHART_ID,
        }, ensure_ascii=False))
        return 0  # Source outages must not block valid YouTube samples/deployment.
    return 0


if __name__ == "__main__":
    sys.exit(main())
