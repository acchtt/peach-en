#!/usr/bin/env python3
"""Read-only discovery of public Korean chart feed access.
No chart scraping and no writes. robots.txt checks are indicative, not licenses.
"""
from urllib.request import Request, urlopen
from urllib.parse import urlparse
from urllib.robotparser import RobotFileParser
from urllib.error import HTTPError, URLError
import json
import re
import socket

AGENT="IVERadarFanStats/0.1 (+https://github.com/acchtt/peach-en)"
RSS=[
"https://rss.applemarketingtools.com/api/v2/kr/music/most-played/100/songs.json",
"https://rss.marketingtools.apple.com/api/v2/kr/music/most-played/100/songs.json",
"https://rss.itunes.apple.com/api/v1/kr/apple-music/top-songs/all/100/json",
]
CHARTS=[
"https://www.genie.co.kr/chart/top200",
"https://music.bugs.co.kr/chart",
"https://www.music-flo.com/",
"https://www.melon.com/chart/index.htm",
]
def get(url):
    try:
        req=Request(url,headers={"User-Agent":AGENT,"Accept":"application/json,text/plain,*/*"})
        with urlopen(req,timeout=12) as r:
            body=r.read(800_000)
            return r.status,body, r.headers.get("Content-Type","")
    except HTTPError as e:
        return e.code,b"",str(e.headers.get("Content-Type",""))
    except (URLError,TimeoutError,OSError,socket.timeout) as e:
        return "ERROR_"+type(e).__name__,b"",""
for url in CHARTS:
    p=urlparse(url)
    robots=f"{p.scheme}://{p.netloc}/robots.txt"
    status,body,_=get(robots)
    if status==200 and body:
        rp=RobotFileParser()
        rp.parse(body.decode("utf-8","replace").splitlines())
        allowed=rp.can_fetch(AGENT,url)
        verdict="allowed-by-robots" if allowed else "disallowed-by-robots"
    else:
        verdict="robots-unavailable-or-missing"
    print(json.dumps({"site":p.netloc,"robots_http":status,"robots_verdict":verdict}))
for url in RSS:
    status,body,content_type=get(url)
    record={"endpoint":urlparse(url).netloc+urlparse(url).path,"status":status,"bytes":len(body),"content_type":content_type}
    if status==200:
        try:
            payload=json.loads(body)
            feed=payload.get("feed",{})
            results=feed.get("results",[])
            record["count"]=len(results)
            record["feed_title"]=feed.get("title")
            record["keys"]=list(feed.keys())
            matched=[{"index":i+1,"name":x.get("name"),"artist":x.get("artistName"),"id":x.get("id"),"url":x.get("url")} for i,x in enumerate(results) if re.search(r"looks can kill",x.get("name",""),re.I) and re.search(r"IVE|아이브",x.get("artistName",""),re.I)]
            record["matches"]=matched[:3]
            record["first_names"]=[(x.get("name","")[:35],x.get("artistName","")[:35]) for x in results[:2]]
        except Exception as exc: record["parse_error"]=type(exc).__name__
    print(json.dumps(record,ensure_ascii=False))
