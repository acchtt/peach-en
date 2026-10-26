#!/usr/bin/env python3
"""Research-only Melon MCP chart response parser. No network or publishing."""
import ast
from datetime import datetime
import io
import json
import tokenize
import unicodedata

class InvalidMelonChart(Exception):
    pass

def normalized(value):
    return unicodedata.normalize("NFKC",value).strip().casefold()

def decode_mcp_chart(text):
    if not isinstance(text,str) or not text or len(text)>120_000:
        raise InvalidMelonChart("Missing or oversized chart payload")
    try:
        value=json.loads(text)
    except ValueError:
        try:
            tokens=[]
            for token in tokenize.generate_tokens(io.StringIO(text).readline):
                if token.type==tokenize.NAME and token.string in ("true","false","null"):
                    replacement={"true":"True","false":"False","null":"None"}[token.string]
                    token=tokenize.TokenInfo(token.type,replacement,token.start,token.end,token.line)
                tokens.append(token)
            value=ast.literal_eval(tokenize.untokenize(tokens))
        except (ValueError,SyntaxError,TypeError,tokenize.TokenError,RecursionError,MemoryError) as exc:
            raise InvalidMelonChart("Cannot safely decode chart") from exc
    if not isinstance(value,dict) or not isinstance(value.get("songs"),list):
        raise InvalidMelonChart("No chart song list")
    return value

def inspect_ive(text, *, chart_type, captured_at):
    if chart_type not in ("TOP_100","DAILY","WEEKLY","HOT_100"):
        raise InvalidMelonChart("Unsupported chart type")
    if not isinstance(captured_at,datetime) or captured_at.tzinfo is None:
        raise InvalidMelonChart("Missing capture timezone")
    items=decode_mcp_chart(text)["songs"]
    if not 1<=len(items)<=30:
        raise InvalidMelonChart("Unexpected chart page length")
    ranks=set()
    ids=set()
    matches=[]
    for item in items:
        if not isinstance(item,dict) or not isinstance(item.get("rank"),dict) or not isinstance(item.get("song_id"),int):
            raise InvalidMelonChart("Song/rank structure changed")
        try:
            rank=int(item["rank"]["current_rank"])
        except (KeyError,TypeError,ValueError) as exc:
            raise InvalidMelonChart("Invalid rank") from exc
        if rank<1 or rank>100 or rank in ranks or item["song_id"] in ids:
            raise InvalidMelonChart("Duplicate or invalid chart entry")
        ranks.add(rank);ids.add(item["song_id"])
        artists=item.get("artists")
        if not isinstance(artists,list):
            raise InvalidMelonChart("No artist list")
        names={normalized(a.get("artist_name","")) for a in artists if isinstance(a,dict)}
        if normalized(item.get("song_name",""))=="looks can kill" and any(n in {"ive","아이브","ive (아이브)","아이브 (ive)"} for n in names):
            matches.append((rank,item["song_id"]))
    if len(matches)>1:
        raise InvalidMelonChart("Multiple exact IVE matches")
    match=matches[0] if matches else None
    return {
        "chart_type":chart_type,
        "captured_at":captured_at.isoformat(timespec="seconds"),
        "ive_rank_in_page":match[0] if match else None,
        "ive_song_id":match[1] if match else None,
        "official_reporting_period":None,
        "publishable":False,
    }
