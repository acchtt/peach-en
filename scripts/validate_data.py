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