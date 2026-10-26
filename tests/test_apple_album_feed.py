#!/usr/bin/env python3
"""Deterministic offline tests. Placeholder rows are NOT persisted in data.json."""
import unittest
from datetime import datetime,timezone,timedelta
from email.utils import format_datetime
from scripts.collect_apple_albums_kr import parse_album_feed, SourceUnavailable

NOW=datetime(2026,10,26,16,44,tzinfo=timezone.utc)
ALBUM_ID="6820421860"

def fixture():
    entries=[{
        "id":str(8000000000+i),
        "name":"Other Record",
        "artistName":"Other Artist",
        "url":f"https://music.apple.com/kr/album/other/{8000000000+i}"
    } for i in range(100)]
    entries[15]={
        "id":ALBUM_ID,
        "name":"Looks Can Kill - EP",
        "artistName":"아이브",
        "url":f"https://music.apple.com/kr/album/looks-can-kill-ep/{ALBUM_ID}",
    }
    return {"feed":{"country":"kr","updated":format_datetime(NOW),"results":entries}}

class AlbumSourceTests(unittest.TestCase):
    def test_exact_album_rank(self):
        result=parse_album_feed(fixture(),album_id=ALBUM_ID,captured_at=NOW)
        self.assertEqual(result["rank"],16)
        self.assertEqual(result["album_id"],ALBUM_ID)
        self.assertEqual(result["collected_at"],"2026-10-27T01:44:00+09:00")
        self.assertEqual(result["verification"],"official-apple-rss")
        self.assertIsNone(result["movement"])
        self.assertNotIn("observed_at",result,"No invented official hourly reporting period")

    def test_not_in_top100_is_unknown_not_zero(self):
        p=fixture()
        p["feed"]["results"][15]["id"]="9000000001"
        self.assertIsNone(parse_album_feed(p,album_id=ALBUM_ID,captured_at=NOW))

    def test_wrong_country_rejected(self):
        p=fixture()
        p["feed"]["country"]="jp"
        with self.assertRaises(SourceUnavailable):
            parse_album_feed(p,album_id=ALBUM_ID,captured_at=NOW)

    def test_short_feed_rejected(self):
        p=fixture()
        p["feed"]["results"]=p["feed"]["results"][:12]
        with self.assertRaises(SourceUnavailable):
            parse_album_feed(p,album_id=ALBUM_ID,captured_at=NOW)

    def test_duplicate_ids_rejected(self):
        p=fixture()
        p["feed"]["results"][35]["id"]=p["feed"]["results"][34]["id"]
        with self.assertRaises(SourceUnavailable):
            parse_album_feed(p,album_id=ALBUM_ID,captured_at=NOW)

    def test_artist_mismatch(self):
        p=fixture()
        p["feed"]["results"][15]["artistName"]="Other Act"
        with self.assertRaises(SourceUnavailable):
            parse_album_feed(p,album_id=ALBUM_ID,captured_at=NOW)

    def test_title_mismatch(self):
        p=fixture()
        p["feed"]["results"][15]["name"]="Other EP"
        with self.assertRaises(SourceUnavailable):
            parse_album_feed(p,album_id=ALBUM_ID,captured_at=NOW)

    def test_album_link_mismatch(self):
        p=fixture()
        p["feed"]["results"][15]["url"]="https://music.apple.com/kr/album/test/123"
        with self.assertRaises(SourceUnavailable):
            parse_album_feed(p,album_id=ALBUM_ID,captured_at=NOW)

    def test_future_metadata_rejected(self):
        p=fixture()
        p["feed"]["updated"]=format_datetime(NOW+timedelta(hours=6))
        with self.assertRaises(SourceUnavailable):
            parse_album_feed(p,album_id=ALBUM_ID,captured_at=NOW)

if __name__=="__main__":
    unittest.main()
