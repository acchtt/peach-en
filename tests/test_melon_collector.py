"""All chart data here is synthetic test input, never published as a real rank."""
from datetime import datetime, timedelta
from unittest import TestCase
from unittest.mock import patch
from zoneinfo import ZoneInfo

from scripts.collect_melon_mcp import (
    Unavailable, find_ive, make_observation, parse_chart_text,
    should_capture, mcp_chart_page, CHARTS
)

KST = ZoneInfo("Asia/Seoul")
NOW = datetime(2026, 10, 27, 3, 13, tzinfo=KST)


def songs(start, length, ive=None):
    rows = []
    for i in range(length):
        rank = start + i
        sid = 100_000_000 + rank
        name, artist = "Placeholder", "Unknown"
        if ive == rank:
            sid, name, artist = 603448999, "Looks Can Kill", "아이브"
        rows.append({
            "song_id": sid, "song_name": name,
            "artists": [{"artist_name": artist}],
            "rank": {"current_rank": str(rank), "past_rank": str(rank), "rank_type": "NONE"},
        })
    return rows


class MelonCollectorTests(TestCase):
    def test_safe_pythonish_response(self):
        source = "{'songs':[{'rank':{'current_rank':'1'},'flag':false,'empty':null}]}"
        parsed = parse_chart_text(source)
        self.assertEqual(parsed["songs"][0]["rank"]["current_rank"], "1")
        self.assertIs(parsed["songs"][0]["flag"], False)
        self.assertIsNone(parsed["songs"][0]["empty"])

    def test_reject_arbitrary_execution(self):
        with self.assertRaises(Unavailable):
            parse_chart_text("__import__('os').system('false')")

    def test_ive_found_with_exact_id(self):
        def fake(chart, start, size):
            return songs(start, size, ive=12)
        with patch("scripts.collect_melon_mcp.mcp_chart_page", side_effect=fake) as read:
            position = find_ive("TOP_100", expected_id=603448999, target_title="Looks Can Kill")
        self.assertEqual(position, 12)
        self.assertEqual(read.call_count, 1)

    def test_secondary_page(self):
        def fake(chart, start, size):
            return songs(start, size, ive=45)
        with patch("scripts.collect_melon_mcp.mcp_chart_page", side_effect=fake), patch("scripts.collect_melon_mcp.time.sleep"):
            position = find_ive("TOP_100", expected_id=603448999, target_title="Looks Can Kill")
        self.assertEqual(position,45)

    def test_known_song_id_wrong_title_fails_closed(self):
        def fake(chart, start, size):
            rows = songs(start, size, ive=12)
            for item in rows:
                if item["song_id"] == 603448999:
                    item["song_name"] = "Different"
            return rows
        with patch("scripts.collect_melon_mcp.mcp_chart_page", side_effect=fake):
            with self.assertRaises(Unavailable):
                find_ive("TOP_100", expected_id=603448999, target_title="Looks Can Kill")

    def test_not_found_is_unknown(self):
        with patch("scripts.collect_melon_mcp.mcp_chart_page", side_effect=lambda c,s,n:songs(s,n)), patch("scripts.collect_melon_mcp.time.sleep"):
            self.assertIsNone(find_ive("TOP_100",expected_id=603448999,target_title="Looks Can Kill"))

    def test_mcp_observation_does_not_invent_published_time(self):
        o = make_observation("TOP_100", rank=12, song_id=603448999, now=NOW)
        self.assertEqual(o["rank"],12)
        self.assertEqual(o["verification"],"official-melon-mcp-capture")
        self.assertIsNone(o["movement"])
        self.assertNotIn("observed_at",o)
        self.assertEqual(o["collected_at"],"2026-10-27T03:13:00+09:00")

    def test_cadence_per_chart(self):
        row = make_observation("TOP_100", rank=12, song_id=603448999, now=NOW)
        self.assertFalse(should_capture([row],"melon-top100",NOW+timedelta(minutes=10)))
        self.assertTrue(should_capture([row],"melon-top100",NOW+timedelta(hours=1)))
        daily = make_observation("DAILY",rank=12,song_id=603448999,now=NOW)
        self.assertFalse(should_capture([daily],"melon-daily",NOW+timedelta(minutes=50)))
        self.assertTrue(should_capture([daily],"melon-daily",NOW+timedelta(days=1)))
        weekly = make_observation("WEEKLY",rank=12,song_id=603448999,now=NOW)
        self.assertFalse(should_capture([weekly],"melon-weekly",NOW+timedelta(days=6)))
        self.assertTrue(should_capture([weekly],"melon-weekly",NOW+timedelta(days=7)))

    def test_chart_map_is_separate(self):
        self.assertEqual({x[0] for x in CHARTS.values()}, {"melon-top100","melon-daily","melon-weekly"})

    def test_reject_rank_outside_top100(self):
        with self.assertRaises(Unavailable):
            make_observation("TOP_100",rank=101,song_id=603448999,now=NOW)
