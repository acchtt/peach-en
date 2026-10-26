#!/usr/bin/env python3
"""Strict schema and provenance checks; no synthetic numbers or silently duplicated periods."""
import json
from pathlib import Path
from urllib.parse import urlparse
from datetime import datetime

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
    iso=o['observed_at']
    instant=datetime.fromisoformat(iso)
    assert instant.tzinfo is not None, 'Time must include timezone'
    url=urlparse(o['source_url'])
    expected=urlparse(charts[o['chart_id']]['source_url'])
    assert url.scheme=='https' and url.hostname==expected.hostname, 'Source domain mismatch'
    assert o['verification']=='official-chart-snapshot', 'Not a verified snapshot'
    key=(o['track_id'],o['chart_id'],iso)
    assert key not in seen, 'Duplicate chart observation'
    seen.add(key)
print(f'PASS: {len(tracks)} tracks, {len(charts)} chart series, {len(seen)} timestamped observations')

# Official MV cumulative counters are separate from chart positions and times.
from urllib.parse import parse_qs
from datetime import timezone
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
