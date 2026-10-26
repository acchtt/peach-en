#!/usr/bin/env python3
"""Record public official IVE MV view-count samples from YouTube Data API v3.

No unofficial scraping, no guesswork, no credentials committed to GitHub.
Missing YOUTUBE_DATA_API_KEY => skip. Other collection failures => nonzero.
"""
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import re
import sys
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
API_URL = "https://www.googleapis.com/youtube/v3/videos"
TRACK = "looks-can-kill"
KST = ZoneInfo("Asia/Seoul")


def fail(message):
    print(f"COLLECTION_UNAVAILABLE: {message}", file=sys.stderr)
    return 1


def main():
    key = os.environ.get("YOUTUBE_DATA_API_KEY", "").strip()
    if not key:
        print("SKIPPED: Set the YOUTUBE_DATA_API_KEY Actions secret to enable automatic YouTube views.")
        return 0

    path = ROOT / "data.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    track = next((item for item in data.get("tracks", []) if item["id"] == TRACK), None)
    if not track:
        return fail("Unknown IVE track.")
    video_id = track.get("mv_video_id")
    if not isinstance(video_id, str) or not re.fullmatch(r"[\w-]{11}", video_id):
        return fail("Official MV video ID is missing or invalid.")

    query = urlencode({
        "part": "snippet,statistics", "id": video_id,
        "fields": "items(id,snippet(title,channelTitle),statistics(viewCount))",
        "key": key
    })
    request = Request(API_URL + "?" + query, headers={
        "User-Agent": "IVE-RADAR/0.1", "Accept": "application/json"
    })
    try:
        with urlopen(request, timeout=20) as response:
            payload = json.load(response)
    except HTTPError as error:
        # Never print the request URL, which contains the secret.
        return fail(f"YouTube Data API returned HTTP {error.code}.")
    except (URLError, TimeoutError, OSError, ValueError) as error:
        return fail(f"YouTube API request failed ({type(error).__name__}).")

    items = payload.get("items", [])
    if len(items) != 1 or items[0].get("id") != video_id:
        return fail("Official video ID mismatch or missing YouTube response.")
    item = items[0]
    snippet = item.get("snippet", {})
    title = snippet.get("title", "")
    channel = snippet.get("channelTitle", "")
    if "looks can kill" not in title.casefold() or "ive" not in title.casefold():
        return fail("Video title does not match IVE Looks Can Kill.")
    if "starship" not in channel.casefold():
        return fail("YouTube video is not on Starship's official channel.")

    try:
        views = int(item["statistics"]["viewCount"])
    except (KeyError, TypeError, ValueError):
        return fail("API response contains no valid public view count.")
    if views < 0 or views > 100_000_000_000:
        return fail("View count outside supported range.")

    captured = datetime.now(KST).replace(microsecond=0)
    series = data.setdefault("streaming", [])
    for existing in series:
        if existing.get("platform") != "YouTube" or existing.get("video_id") != video_id:
            continue
        previous = datetime.fromisoformat(existing["collected_at"]).astimezone(KST)
        if previous.strftime("%Y-%m-%dT%H") == captured.strftime("%Y-%m-%dT%H"):
            print("UNCHANGED: YouTube MV has already been sampled this KST hour.")
            return 0

    series.append({
        "track_id": TRACK,
        "platform": "YouTube",
        "metric": "view_count",
        "video_id": video_id,
        "value": views,
        "collected_at": captured.isoformat(),
        "source_url": "https://www.youtube.com/watch?v=" + video_id,
        "verification": "youtube-data-api-v3"
    })
    series.sort(key=lambda item: datetime.fromisoformat(item["collected_at"]).astimezone(timezone.utc))
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"APPENDED: Official MV {views:,} public views, collected {captured.isoformat()} KST.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
