import unittest
from datetime import datetime,timezone
from scripts.melon_mcp_adapter import decode_mcp_chart,inspect_ive,InvalidMelonChart

NOW=datetime(2026,10,26,17,0,tzinfo=timezone.utc)
def sample():
    return "{'pageable':{'index':1,'has_more':false},'songs':[" \
        "{'song_id':123,'song_name':'Looks Can Kill','artists':[{'artist_name':'아이브'}]," \
        "'rank':{'current_rank':'6','past_rank':'6','rank_type':'NONE'}}," \
        "{'song_id':124,'song_name':'Other','artists':[{'artist_name':'Someone'}]," \
        "'rank':{'current_rank':'7','past_rank':'7','rank_type':'NONE'}}]}"

class MelonMcpTests(unittest.TestCase):
    def test_literal_parse_is_safe(self):
        self.assertEqual(len(decode_mcp_chart(sample())['songs']),2)
        self.assertFalse(decode_mcp_chart(sample())['pageable']['has_more'])
    def test_exact_match_has_no_published_chart_time(self):
        result=inspect_ive(sample(),chart_type="TOP_100",captured_at=NOW)
        self.assertEqual((result['ive_rank_in_page'],result['ive_song_id']),(6,123))
        self.assertIsNone(result['official_reporting_period'])
        self.assertFalse(result['publishable'])
    def test_absent_song_does_not_mean_unranked(self):
        text=sample().replace("'Looks Can Kill'","'Something Else'")
        self.assertIsNone(inspect_ive(text,chart_type="TOP_100",captured_at=NOW)['ive_rank_in_page'])
    def test_rejects_duplicate_rank(self):
        text=sample().replace("'current_rank':'7'","'current_rank':'6'")
        with self.assertRaises(InvalidMelonChart):
            inspect_ive(text,chart_type="TOP_100",captured_at=NOW)
    def test_rejects_duplicate_song(self):
        text=sample().replace("'song_id':124","'song_id':123")
        with self.assertRaises(InvalidMelonChart):
            inspect_ive(text,chart_type="TOP_100",captured_at=NOW)
    def test_rejects_arbitrary_code(self):
        with self.assertRaises(InvalidMelonChart):
            decode_mcp_chart("__import__('os').system('echo no')")
    def test_requires_chart_and_timezone(self):
        with self.assertRaises(InvalidMelonChart):
            inspect_ive(sample(),chart_type="UNKNOWN",captured_at=NOW)
        with self.assertRaises(InvalidMelonChart):
            inspect_ive(sample(),chart_type="TOP_100",captured_at=datetime(2026,10,26))
    def test_refuses_empty_rank_page(self):
        with self.assertRaises(InvalidMelonChart):
            inspect_ive("{'songs':[]}",chart_type="TOP_100",captured_at=NOW)

if __name__=="__main__":
    unittest.main()
