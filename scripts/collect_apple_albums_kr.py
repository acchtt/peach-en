#!/usr/bin/env python3
"""Official Apple Music KR Top 100 Albums RSS monitor for IVE RADAR.

The feed is a *most-played album ranking*, not album sales or Circle Album.
Empty/no exact match => no rank observation, not proof that the album is uncharted.
Keep provider capture times distinct from published weekly/monthly chart periods.
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
from urllib.parse import urlparse
from urllib.request import Request, urlopen
from zoneinfo import ZoneInfo

ROOT=Path(__file__).resolve().parents[1]
RSS_URL="https://rss.applemarketingtools.com/api/v2/kr/music/most-played/100/albums.json"
CHART_ID="apple-music-kr-top-albums"
TRACK_ID="looks-can-kill"
KST=ZoneInfo("Asia/Seoul")
AGENT="IVERadarChartMonitor/0.2 (+https://github.com/acchtt/peach-en)"


class SourceUnavailable(Exception):
    pass


def normalize(value: str) -> str:
    return unicodedata.normalize("NFKC",value).strip().casefold()


def get_feed() -> dict:
    error=None
    for attempt in range(2):
        if attempt:
            time.sleep(2)
        try:
            request=Request(RSS_URL,headers={"User-Agent":AGENT,"Accept":"application/json","Cache-Control":"no-cache"})
            with urlopen(request,timeout=22) as response:
                if response.status!=200 or "json" not in response.headers.get("Content-Type","").lower():
                    raise SourceUnavailable("Apple album feed returned invalid response")
                return json.loads(response.read(1_000_000))
        except (HTTPError,URLError,TimeoutError,OSError,ValueError,SourceUnavailable) as exc:
            error=exc
    raise SourceUnavailable("Official album RSS unavailable: "+type(error).__name__)


def parse_album_feed(payload:dict, *, album_id:str, captured_at:datetime) -> dict | None:
    if not isinstance(payload,dict) or not isinstance(payload.get("feed"),dict):
        raise SourceUnavailable("No recognizable official feed")
    feed=payload["feed"]
    if feed.get("country","").lower()!="kr":
        raise SourceUnavailable("Wrong country in album feed")
    albums=feed.get("results")
    if not isinstance(albums,list) or len(albums)!=100 or any(not isinstance(x,dict) for x in albums):
        raise SourceUnavailable("Top 100 albums feed missing complete ranking")
    ids=[str(x.get("id","")) for x in albums]
    if len(set(ids))!=100 or any(not re.fullmatch(r"\d{4,}",x) for x in ids):
        raise SourceUnavailable("Album ID list is incomplete or duplicated")
    try:
        published=parsedate_to_datetime(feed["updated"])
    except (KeyError,ValueError,TypeError,IndexError) as exc:
        raise SourceUnavailable("Apple feed metadata lacks timestamp") from exc
    if published.tzinfo is None or published.astimezone(timezone.utc)>captured_at.astimezone(timezone.utc)+timedelta(minutes=10):
        raise SourceUnavailable("Apple album feed timestamp is invalid")
    found=[(i+1,entry) for i,entry in enumerate(albums) if str(entry["id"])==album_id]
    if not found:
        return None
    if len(found)!=1:
        raise SourceUnavailable("Duplicate target album IDs in chart")
    rank,item=found[0]
    title=normalize(item.get("name",""))
    valid_titles={"looks can kill","looks can kill - ep","looks can kill (ep)"}
    if title not in valid_titles:
        raise SourceUnavailable("Matched album ID with unexpected title: review before publishing")
    artist=normalize(item.get("artistName",""))
    if artist not in {"ive","아이브"}:
        raise SourceUnavailable("Matched album ID with unexpected artist")
    song_url=item.get("url","")
    parsed=urlparse(song_url)
    if parsed.scheme!="https" or parsed.hostname!="music.apple.com" or not parsed.path.rstrip("/").endswith("/"+album_id):
        raise SourceUnavailable("Apple Music album link ID or host mismatch")
    return {
        "track_id":TRACK_ID,"chart_id":CHART_ID,"album_id":album_id,
        "rank":rank,
        "movement":None,
        "collected_at":captured_at.astimezone(KST).replace(microsecond=0).isoformat(),
        "feed_updated_at":published.astimezone(KST).replace(microsecond=0).isoformat(),
        "source_url":RSS_URL,
        "album_url":song_url,
        "verification":"official-apple-rss",
        "note":"Apple Music KR Top 100 most-played album ranking captured from official RSS; not album sales or a published hourly period."
    }


def append_album(observation:dict, *, dry_run:bool) -> str:
    path=ROOT/"data.json"
    data=json.loads(path.read_text(encoding="utf-8"))
    if data.get("schema_version")!=2:
        raise SourceUnavailable("Data schema mismatch")
    album_charts=data.get("album_charts",[])
    if not any(x["id"]==CHART_ID and x["source_url"]==RSS_URL for x in album_charts):
        raise SourceUnavailable("Album chart source not registered")
    series=data.setdefault("album_chart_observations",[])
    latest=[x for x in series if x.get("chart_id")==CHART_ID and x.get("album_id")==observation["album_id"]]
    latest.sort(key=lambda x:datetime.fromisoformat(x["collected_at"]).astimezone(timezone.utc))
    if latest:
        prior=latest[-1]
        before=datetime.fromisoformat(prior["collected_at"])
        now=datetime.fromisoformat(observation["collected_at"])
        if now<=before:
            raise SourceUnavailable("Album observation timestamp is not increasing")
        if observation["rank"]==prior["rank"] and now-before<timedelta(hours=3):
            return "UNCHANGED_RANK_RECENTLY_SAMPLED"
    if dry_run:
        return "WOULD_APPEND"
    series.append(observation)
    series.sort(key=lambda x:datetime.fromisoformat(x["collected_at"]).astimezone(timezone.utc))
    path.write_text(json.dumps(data,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    return "APPENDED"


def main():
    cli=argparse.ArgumentParser()
    cli.add_argument("--dry-run",action="store_true")
    args=cli.parse_args()
    try:
        data=json.loads((ROOT/"data.json").read_text(encoding="utf-8"))
        track=next(x for x in data["tracks"] if x["id"]==TRACK_ID)
        album_id=track["apple_music_kr_album_id"]
        if not isinstance(album_id,str) or not re.fullmatch(r"\d{4,}",album_id):
            raise SourceUnavailable("Album ID missing or invalid")
        payload=get_feed()
        captured=datetime.now(KST)
        observation=parse_album_feed(payload,album_id=album_id,captured_at=captured)
        if not observation:
            print(json.dumps({"status":"NO_VERIFIED_TOP100_OBSERVATION","chart":CHART_ID,"checked_at":captured.isoformat(timespec="seconds"),
            "note":"Target EP absent from latest returned 100 entries; no out-of-chart history is inferred."}))
            return 0
        status=append_album(observation,dry_run=args.dry_run)
        print(json.dumps({"status":status,"chart":CHART_ID,"rank":observation["rank"],
                          "captured_at":observation["collected_at"],"source":RSS_URL},ensure_ascii=False))
    except (SourceUnavailable,KeyError,TypeError,ValueError) as exc:
        print(json.dumps({"status":"SOURCE_UNAVAILABLE","chart":CHART_ID,"reason":str(exc)[:150]}))
    return 0  # Independent sources should not block verified YouTube or song-RSS updates.


if __name__=="__main__":
    sys.exit(main())
