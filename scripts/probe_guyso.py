#!/usr/bin/env python3
"""Read-only Guyso.com source review; does not ingest music rankings.

Check robots metadata before fetching content, inspect one public page
only if allowed. No API probing, no automated repeated collection.
"""
import html
import json
import re
from urllib.error import HTTPError,URLError
from urllib.request import Request,urlopen
from urllib.robotparser import RobotFileParser
from urllib.parse import urlparse
from datetime import datetime,timezone

HOST="https://xn--o39an51b2re.com"
UA="IVERadarResearchReview/0.1 (+https://github.com/acchtt/peach-en)"
URLS=[
    HOST+"/",
    HOST+"/chart/melon/top100/20261027/02",
    HOST+"/chart/genie/realtime/20261027/01"
]

def get(url, method="GET"):
    req=Request(url,headers={"User-Agent":UA,"Accept":"text/html, text/plain;q=0.9,*/*;q=0.5"},method=method)
    try:
        with urlopen(req,timeout=16) as response:
            return response.status,dict(response.headers.items()),response.read(180000)
    except HTTPError as err:
        return err.code,dict(err.headers.items()),b""
    except (URLError,TimeoutError,OSError) as err:
        return "NETWORK_"+type(err).__name__,{},b""

status,headers,body=get(HOST+"/robots.txt")
result={"stage":"robots","status":status,"bytes":len(body)}
allowed=False
if status==200:
    parser=RobotFileParser()
    parser.parse(body.decode("utf-8","replace").splitlines())
    allowed=all(parser.can_fetch(UA,url) for url in URLS)
    result["url_permissions"]={urlparse(url).path:parser.can_fetch(UA,url) for url in URLS}
else:
    result["access_decision"]="unknown; do not automatically collect"
print(json.dumps(result,ensure_ascii=False))

if not allowed:
    print(json.dumps({"status":"NO_AUTOMATED_CHART_FETCH","reason":"No confirmed robots permission for every tested URL"}))
else:
    for url in URLS:
        code,head,body=get(url)
        content=body.decode("utf-8","replace")
        titles=re.findall(r"<title[^>]*>(.*?)</title>",content,re.I|re.S)
        title=html.unescape(re.sub(r"<[^>]*>","",titles[0]).strip())[:180] if titles else ""
        dates=re.findall(r"2026[.\-/]10[.\-/]27.{0,15}(?:0?[0-9]|1[0-9]|2[0-3]):00",content)
        print(json.dumps({
            "stage":"one-off-page-health","path":urlparse(url).path,"status":code,
            "content_type":head.get("Content-Type", ""),
            "title":title,"visible_ive_title_match":"Looks Can Kill" in content,
            "date_match_count":len(dates),"size":len(body)
        },ensure_ascii=False))
