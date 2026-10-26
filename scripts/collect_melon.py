#!/usr/bin/env python3
"""Conservative, read-only Melon TOP100 collector for the IVE RADAR fan project.

- Fetches a public chart only if robots.txt permits it.
- Never guesses a chart timestamp, rank, movement, or out-of-chart status.
- Accepts only a complete chart and exact IVE/title match.
- Deduplicates by (track_id, chart_id, observed_at).
- Fails closed if blocked, stale, uncertain or structurally changed.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timedelta, timezone
import json
import re
import sys
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urljoin, urlparse
from urllib.request import Request, urlopen
from zoneinfo import ZoneInfo

try:
    from bs4 import BeautifulSoup
except ImportError:
    sys.exit("Missing dependency: pip install beautifulsoup4")

PROJECT = Path(__file__).resolve().parents[1]
CHART_URL = "https://www.melon.com/chart/index.htm"
ROBOTS_URL = "https://www.melon.com/robots.txt"
AGENT = "IVERadarChartMonitor/0.1 (+https://github.com/acchtt/peach-en; hourly public-chart check)"
KST = ZoneInfo("Asia/Seoul")
DATE_TIME = re.compile(r"(20\d{2})\s*[.\-/]\s*(\d{1,2})\s*[.\-/]\s*(\d{1,2})\s+(\d{1,2}):(\d{2})")
TITLE = "Looks Can Kill"


class CollectionUnavailable(Exception):
    """No trustworthy observation was obtained; never modify data.json."""


def fetch(url: str) -> tuple[int, str]:
    request = Request(url, headers={"User-Agent": AGENT, "Accept": "text/html,application/xhtml+xml;q=0.9"})
    try:
        with urlopen(request, timeout=18) as response:
            status = response.status
            raw = response.read(800_000)
            charset = response.headers.get_content_charset() or "utf-8"
            return status, raw.decode(charset, errors="replace")
    except HTTPError as exc:
        if exc.code == 404:
            return 404, ""
        raise CollectionUnavailable(f"{urlparse(url).path}: HTTP {exc.code}") from exc
    except (URLError, TimeoutError, OSError) as exc:
        raise CollectionUnavailable(f"{urlparse(url).path}: network error ({type(exc).__name__})") from exc


def permitted() -> None:
    status, robots = fetch(ROBOTS_URL)
    if status == 404:  # A missing robots.txt means no published crawl restrictions.
        return
    if status != 200 or not robots.strip():
        raise CollectionUnavailable("Could not read robots.txt; stopping rather than assuming permission")
    from urllib.robotparser import RobotFileParser
    parser = RobotFileParser()
    parser.parse(robots.splitlines())
    if not parser.can_fetch(AGENT, CHART_URL):
        raise CollectionUnavailable("robots.txt does not permit chart collection")
    # Only one GET to the chart in each collection run.


def read_timestamp(soup: BeautifulSoup, now: datetime) -> datetime:
    containers = soup.select(
        ".calendar_prid, .calendar_prid_wrap, .calendar, .calendar_wrap, .year, .yyyymmdd"
    )
    candidates = []
    for container in containers:
        text = container.get_text(" ", strip=True)
        if len(text) > 120:
            text = text[:120]
        candidates.extend(DATE_TIME.findall(text))
    if not candidates:
        # The chart title/heading may contain an inline publication timestamp.
        for el in soup.find_all(["h1", "h2", "h3", "time"], limit=30):
            candidates.extend(DATE_TIME.findall(el.get_text(" ", strip=True)))
    if not candidates:
        raise CollectionUnavailable("Explicit official TOP100 reporting timestamp not found")
    parsed = set()
    for y, m, d, hh, mm in candidates:
        try:
            parsed.add(datetime(int(y), int(m), int(d), int(hh), int(mm), tzinfo=KST))
        except ValueError:
            pass
    if len(parsed) != 1:
        raise CollectionUnavailable("Ambiguous chart reporting time")
    observed = next(iter(parsed))
    # Don't take an ancient cached page or a future clock as a fresh hourly observation.
    if observed - now > timedelta(minutes=10):
        raise CollectionUnavailable("Chart timestamp is in the future")
    if now - observed > timedelta(hours=5):
        raise CollectionUnavailable("Chart page is stale; no new observation")
    return observed


def parse_movement(row: BeautifulSoup):
    # Melon HTML uses up/down markers; only use a delta if clearly labeled.
    marker = row.select_one(".rank_wrap")
    if not marker:
        return None
    kind = marker.select_one(".up, .down")
    if kind is None:
        if marker.select_one(".none, .same"):
            return 0
        return None
    text = kind.get_text(" ", strip=True)
    numbers = re.findall(r"\d+", text)
    if len(numbers) != 1:
        return None
    delta = int(numbers[0])
    if delta > 100:
        return None
    return delta if "up" in kind.get("class", []) else -delta


def parse_chart(html: str, now: datetime) -> dict:
    soup = BeautifulSoup(html, "html.parser")
    title = soup.title.get_text(" ", strip=True) if soup.title else ""
    if "멜론" not in title and "Melon" not in title:
        raise CollectionUnavailable("Page is not recognizable as an official Melon page")
    if "TOP100" not in soup.get_text(" ", strip=True)[:3500]:
        raise CollectionUnavailable("Page is not recognizable as the Melon TOP100 chart")
    timestamp = read_timestamp(soup, now)
    rows = soup.select("tr.lst50, tr.lst100")
    if len(rows) < 90 or len(rows) > 110:
        raise CollectionUnavailable(f"Chart integrity check failed: found {len(rows)} ranked rows")
    matches = []
    ranks = []
    for row in rows:
        title_element = row.select_one(".ellipsis.rank01 a")
        artist_element = row.select_one(".ellipsis.rank02")
        rank_element = row.select_one("span.rank")
        if not title_element or not artist_element or not rank_element:
            raise CollectionUnavailable("Chart row structure changed")
        song = title_element.get_text(" ", strip=True)
        artist = artist_element.get_text(" ", strip=True)
        rank_match = re.fullmatch(r"\s*(\d{1,3})\s*", rank_element.get_text(" ", strip=True))
        if not rank_match:
            raise CollectionUnavailable("Could not parse rank safely")
        position = int(rank_match.group(1))
        ranks.append(position)
        if song.casefold() == TITLE.casefold() and re.search(r"\bIVE\b|아이브", artist, re.I):
            matches.append({"rank": position, "movement": parse_movement(row)})
    if len(set(ranks)) != len(ranks) or min(ranks) != 1 or max(ranks) != len(ranks):
        raise CollectionUnavailable("Rank sequence is incomplete or duplicated")
    if len(matches) != 1:
        raise CollectionUnavailable(f"Found {len(matches)} exact IVE Looks Can Kill matches in chart")
    return {
        "track_id": "looks-can-kill",
        "chart_id": "melon-top100",
        "rank": matches[0]["rank"],
        "movement": matches[0]["movement"],
        "observed_at": timestamp.isoformat(timespec="seconds"),
        "source_url": CHART_URL,
        "verification": "official-chart-snapshot",
        "note": f"Automated public Melon TOP100 snapshot, timestamp shown on source page; checked at {now.isoformat(timespec='seconds')}."
    }


def update_dataset(observation: dict, *, dry_run: bool) -> str:
    data_file = PROJECT / "data.json"
    data = json.loads(data_file.read_text(encoding="utf-8"))
    existing = data["observations"]
    key = (observation["track_id"], observation["chart_id"], observation["observed_at"])
    for item in existing:
        same = (item["track_id"], item["chart_id"], item["observed_at"]) == key
        if same:
            if item["rank"] != observation["rank"]:
                raise CollectionUnavailable("Official chart rank conflicts with existing timestamp; requires review")
            return "ALREADY_RECORDED"
    existing.append(observation)
    existing.sort(key=lambda item: datetime.fromisoformat(item["observed_at"]).astimezone(timezone.utc))
    if not dry_run:
        data_file.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return "WOULD_APPEND" if dry_run else "APPENDED"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true", help="Validate access and parse without modifying JSON")
    parser.add_argument("--strict", action="store_true", help="Exit nonzero if collection is unavailable")
    args = parser.parse_args()
    try:
        permitted()
        status, html = fetch(CHART_URL)
        if status != 200:
            raise CollectionUnavailable(f"Melon TOP100 returned HTTP {status}")
        now = datetime.now(KST)
        observation = parse_chart(html, now)
        outcome = update_dataset(observation, dry_run=args.dry_run)
        print(json.dumps({
            "status": outcome,
            "rank": observation["rank"],
            "chart_time_kst": observation["observed_at"],
            "rows_validated": "90-100",
            "source": CHART_URL
        }, ensure_ascii=False))
    except CollectionUnavailable as exc:
        print(json.dumps({"status": "SOURCE_UNAVAILABLE", "reason": str(exc)}, ensure_ascii=False))
        return 1 if args.strict else 0
    return 0


if __name__ == "__main__":
    sys.exit(main())
