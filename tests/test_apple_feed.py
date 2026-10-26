#!/usr/bin/env python3
"""Offline validation of the RSS parser; fixtures are NEVER production stats."""
from datetime import datetime, timezone
from email.utils import format_datetime
import unittest

from scripts.collect_apple_kr import parse_feed, Unavailable

NOW = datetime(2026,10,26,16,17,tzinfo=timezone.utc)
SONG_ID = "6820422075"


def fixture():
    rows = [
        {
            "id": str(6000000000+i),
            "name": "Placeholder chart song",
            "artistName": "Other Artist",
            "url": f"https://music.apple.com/kr/album/example/100000?i={6000000000+i}",
        } for i in range(100)
    ]
    rows[1] = {
        "id": SONG_ID,
        "name": "Looks Can Kill",
        "artistName": "아이브",
        "url": "https://music.apple.com/kr/album/looks-can-kill/6820421860?i=6820422075",
    }
    return {"feed": {
        "country": "kr",
        "updated": format_datetime(NOW),
        "results": rows,
    }}


class FeedParserTests(unittest.TestCase):
    def test_exact_ive_song_rank_and_capture_time(self):
        result = parse_feed(fixture(), song_id=SONG_ID, collected_at=NOW)
        self.assertEqual(result["rank"], 2)
        self.assertEqual(result["verification"], "official-apple-rss")
        self.assertIsNone(result["movement"])
        self.assertNotIn("observed_at", result, "Capture time must not masquerade as a published chart hour")
        self.assertEqual(result["collected_at"], "2026-10-27T01:17:00+09:00")

    def test_reject_wrong_country(self):
        payload=fixture()
        payload["feed"]["country"]="us"
        with self.assertRaises(Unavailable):
            parse_feed(payload, song_id=SONG_ID, collected_at=NOW)

    def test_reject_duplicate_chart_ids(self):
        payload=fixture()
        payload["feed"]["results"][20]["id"]=payload["feed"]["results"][19]["id"]
        with self.assertRaises(Unavailable):
            parse_feed(payload, song_id=SONG_ID, collected_at=NOW)

    def test_reject_artist_mismatch(self):
        payload=fixture()
        payload["feed"]["results"][1]["artistName"]="Not IVE"
        with self.assertRaises(Unavailable):
            parse_feed(payload, song_id=SONG_ID, collected_at=NOW)

    def test_reject_url_mismatch(self):
        payload=fixture()
        payload["feed"]["results"][1]["url"]="https://music.apple.com/kr/album/test/123?i=1"
        with self.assertRaises(Unavailable):
            parse_feed(payload, song_id=SONG_ID, collected_at=NOW)

    def test_reject_missing_track(self):
        payload=fixture()
        payload["feed"]["results"][1]["id"]="6000000101"
        with self.assertRaises(Unavailable):
            parse_feed(payload, song_id=SONG_ID, collected_at=NOW)

    def test_reject_empty_feed(self):
        payload=fixture()
        payload["feed"]["results"]=[]
        with self.assertRaises(Unavailable):
            parse_feed(payload, song_id=SONG_ID, collected_at=NOW)


if __name__=="__main__":
    unittest.main()
