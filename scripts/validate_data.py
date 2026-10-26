#!/usr/bin/env python3
"""Strict schema and provenance checks; no synthetic numbers or silently duplicated periods."""
import json
from pathlib import Path
from urllib.parse import urlparse, parse_qs
from datetime import datetime, timedelta

root=Path(__file__).resolve().parents[1]
data=json.loads((root/'data.json').read_text())
assert data.get('schema_version')==2, 'Unexpected stats schema'
assert isinstance(data.get('observations'),list), 'observations must be a list'
charts={s['id']:s for s in data['charts']}
tracks={t['id']:t for t in data['tracks']}
seen=set()
for o in data['observations']:
    assert o['chart_id'] in charts, 'Unknown chart ID'
    assert o['track_id'] in tracks, 'Unknown track ID'
    assert type(o['rank']) is int and 1<=o['rank']<=200, 'Invalid rank'
    apple = o['chart_id']=='apple-music-kr-top-songs'
    melon_capture = o.get('verification')=='official-melon-mcp-capture'
    iso = o['collected_at'] if (apple or melon_capture) else o['observed_at']
    instant = datetime.fromisoformat(iso)
    assert instant.tzinfo is not None, 'Time must include timezone'
    url = urlparse(o['source_url'])
    expected = urlparse(charts[o['chart_id']]['source_url'])
    assert url.scheme=='https' and url.hostname==expected.hostname, 'Source domain mismatch'
    if apple:
        assert o['verification']=='official-apple-rss', 'Apple RSS verification mismatch'
        assert 1<=o['rank']<=100, 'Apple RSS rank outside Top 100'
        assert o.get('song_id')==tracks[o['track_id']].get('apple_music_kr_song_id'), 'Wrong Apple song ID'
        assert o.get('movement') is None, 'Apple feed cannot assert movement'
        song_url=urlparse(o.get('song_url', ''))
        assert song_url.scheme=='https' and song_url.hostname=='music.apple.com', 'Invalid official Apple song link'
        assert parse_qs(song_url.query).get('i')==[o['song_id']], 'Apple track link mismatch'
        feed_updated=datetime.fromisoformat(o['feed_updated_at'])
        assert feed_updated.tzinfo is not None, 'Apple feed metadata time needs timezone'
        assert feed_updated<=instant + timedelta(minutes=10), 'RSS feed metadata cannot be in the future'
    elif melon_capture:
        assert o['chart_id'] in {'melon-top100','melon-daily','melon-weekly'}, 'Unexpected Melon MCP series'
        assert o['melon_song_id']==tracks[o['track_id']].get('melon_song_id'), 'Wrong first-party Melon song ID'
        assert type(o['melon_song_id']) is int and o['melon_song_id'] > 0, 'Melon ID invalid'
        assert o['mcp_endpoint']=='https://mcp.melon.com/mcp/', 'Must use first-party Melon MCP'
        assert 1<=o['rank']<=100 and o.get('movement') is None, 'MCP capture has no confirmed movement'
        assert 'observed_at' not in o, 'Capture time is not a provider-published chart time'
        assert instant.utcoffset()==timedelta(hours=9), 'Melon captures must be timestamped in KST'
        assert o['source_url']==charts[o['chart_id']]['source_url'], 'Wrong chart permalink'
    else:
        assert o['verification']=='official-chart-snapshot', 'Not a verified official chart snapshot'
    key=(o['track_id'],o['chart_id'],iso)
    assert key not in seen, 'Duplicate chart observation'
    seen.add(key)
# Melon capture cadence: one sample per KST hour per chart. Daily/weekly are
# sampled at lower frequency by the collector but still require unique hours.
melon_capture_hours=set()
for o in data['observations']:
    if o.get('verification')!='official-melon-mcp-capture':
        continue
    stamp=datetime.fromisoformat(o['collected_at'])
    key=(o['track_id'],o['chart_id'],stamp.strftime('%Y-%m-%dT%H'))
    assert key not in melon_capture_hours, 'Duplicate official Melon MCP capture hour'
    melon_capture_hours.add(key)
print(f'PASS: {len(tracks)} tracks, {len(charts)} chart series, {len(seen)} timestamped observations')

# Official MV cumulative counters are separate from chart positions and times.
from urllib.parse import parse_qs
from datetime import timezone, timedelta
streaming = data.get('streaming', [])
assert isinstance(streaming, list), 'streaming must be a list'
video_ids = {t['id']: t.get('mv_video_id') for t in data['tracks']}
samples = set()
for item in streaming:
    assert item.get('track_id') in tracks, 'Unknown streaming track'
    assert item.get('platform') == 'YouTube', 'Unsupported streaming platform'
    assert item.get('metric') == 'view_count', 'Unsupported metric'
    assert item.get('video_id') == video_ids[item['track_id']], 'Video ID mismatch'
    assert type(item.get('value')) is int and 0 <= item['value'] <= 100_000_000_000, 'Invalid views'
    captured = datetime.fromisoformat(item['collected_at'])
    assert captured.tzinfo is not None, 'Missing timezone'
    assert item.get('verification') == 'youtube-data-api-v3', 'Unsupported verification'
    url = urlparse(item.get('source_url', ''))
    assert url.scheme == 'https' and url.hostname in ('www.youtube.com','youtube.com'), 'Wrong MV hostname'
    assert parse_qs(url.query).get('v') == [item['video_id']], 'MV URL does not match'
    key = (item['track_id'], item['video_id'], captured.astimezone(timezone.utc).strftime('%Y-%m-%dT%H'))
    assert key not in samples, 'Duplicate hourly MV counter sample'
    samples.add(key)
print(f'PASS: {len(samples)} YouTube MV counter samples')


# Official Apple Music KR most-played albums are NOT physical sales.
album_sources={x['id']:x for x in data.get('album_charts',[])}
assert 'apple-music-kr-top-albums' in album_sources, 'Missing Apple KR album chart registration'
album_rows=data.get('album_chart_observations',[])
assert isinstance(album_rows,list), 'Album chart captures must be a list'
album_ids={x['id']:x.get('apple_music_kr_album_id') for x in data['tracks']}
album_seen=set()
for item in album_rows:
    assert item.get('track_id') in tracks, 'Unknown album track'
    assert item.get('chart_id')=='apple-music-kr-top-albums', 'Unsupported album chart'
    assert item.get('album_id')==album_ids[item['track_id']], 'Official Apple KR EP ID mismatch'
    assert type(item.get('rank')) is int and 1<=item['rank']<=100, 'Invalid KR album chart rank'
    assert item.get('movement') is None, 'Apple album feed has no movement metadata'
    assert item.get('verification')=='official-apple-rss', 'Album RSS source unverified'
    collected=datetime.fromisoformat(item['collected_at'])
    feed_updated=datetime.fromisoformat(item['feed_updated_at'])
    assert collected.tzinfo is not None and feed_updated.tzinfo is not None, 'Album capture missing timezone'
    assert collected.utcoffset()==timedelta(hours=9), 'Album captured_at must be KST'
    assert feed_updated<=collected+timedelta(minutes=10), 'Invalid RSS update metadata timestamp'
    feed_url=urlparse(item.get('source_url',''))
    assert feed_url.scheme=='https' and feed_url.hostname=='rss.applemarketingtools.com', 'Album feed hostname mismatch'
    assert item['source_url']==album_sources[item['chart_id']]['source_url'], 'Wrong official album RSS endpoint'
    album_url=urlparse(item.get('album_url',''))
    assert album_url.scheme=='https' and album_url.hostname=='music.apple.com', 'Album link must be official'
    assert album_url.path.rstrip('/').endswith('/'+item['album_id']), 'Album link ID mismatch'
    key=(item['track_id'],item['album_id'],collected.astimezone(timezone.utc).strftime('%Y-%m-%dT%H'))
    assert key not in album_seen, 'Duplicate Apple KR album chart hour'
    album_seen.add(key)
print(f'PASS: {len(album_seen)} Apple Music KR album rank captures')

# These are source links, not a license to scrape or redistribute Circle charts.
circle_sources=data.get('circle_chart_sources',[])
assert len(circle_sources)==3 and len(set(x['id'] for x in circle_sources))==3, 'Circle weekly source registry invalid'
for x in circle_sources:
    assert x['collection_status']=='permission-unconfirmed', 'No Circle automated access authorization'
    uri=urlparse(x['source_url'])
    assert uri.scheme=='https' and uri.hostname in ('circlechart.co.kr','circlechart.kr'), 'Wrong Circle official URL'
