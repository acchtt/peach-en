#!/usr/bin/env python3
"""Read-only source feasibility: Circle robots policies and official Apple KR album RSS.

Do not retrieve Circle chart pages if permission is uncertain or disallowed.
Do not modify the website data.
"""
import json
from urllib.parse import urlparse
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError
from urllib.robotparser import RobotFileParser

USER_AGENT="IVERadarChartMonitor/0.2 (+https://github.com/acchtt/peach-en)"
CIRCLE_SITES=[
    ("https://circlechart.co.kr", "/page_chart/onoff.circle?serviceGbn=ALL"),
    ("https://circlechart.kr", "/page_chart/onoff.circle?serviceGbn=ALL"),
]
APPLE_ALBUMS=[
    "https://rss.applemarketingtools.com/api/v2/kr/music/most-played/100/albums.json",
    "https://rss.applemarketingtools.com/api/v2/kr/music/top-albums/100/albums.json",
]
def load(url,accept="text/plain,*/*"):
    try:
        req=Request(url,headers={"User-Agent":USER_AGENT,"Accept":accept})
        with urlopen(req,timeout=18) as response:
            return response.status,response.read(900_000),response.headers.get("Content-Type","")
    except HTTPError as error:
        return error.code,b"",""
    except (URLError,TimeoutError,OSError) as error:
        return "UNAVAILABLE_"+type(error).__name__,b"",""
def main():
    for root,chart_path in CIRCLE_SITES:
        status,body,kind=load(root+"/robots.txt")
        record={"source":"Circle Chart","host":urlparse(root).hostname,
                "robots_status":status,"chart_path":chart_path}
        if status==200 and body:
            parser=RobotFileParser()
            parser.parse(body.decode("utf-8","replace").splitlines())
            record["chart_access_by_robots"]="allowed" if parser.can_fetch(USER_AGENT,root+chart_path) else "disallowed"
        else:
            record["chart_access_by_robots"]="not_established"
        print(json.dumps(record,ensure_ascii=False))
    for url in APPLE_ALBUMS:
        status,body,kind=load(url,accept="application/json")
        record={"source":"Apple official marketing RSS (album discovery)",
                "path":urlparse(url).path,"status":status,"content_type":kind}
        if status==200 and "json" in kind.lower():
            try:
                payload=json.loads(body)
                feed=payload["feed"]
                results=feed["results"]
                record["country"]=feed.get("country")
                record["count"]=len(results)
                record["updated"]=feed.get("updated")
                record["matches"]=[{"rank":i+1,"title":r.get("name"),"artist":r.get("artistName"),
                     "id":r.get("id"),"url":r.get("url")} for i,r in enumerate(results)
                     if r.get("name","").strip().casefold()=="looks can kill" and
                     r.get("artistName","").strip().casefold() in ("ive","아이브")]
            except (KeyError,TypeError,ValueError) as err:
                record["parse_error"]=str(err)[:80]
        print(json.dumps(record,ensure_ascii=False))
if __name__=="__main__":
    main()
