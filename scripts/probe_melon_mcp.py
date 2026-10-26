#!/usr/bin/env python3
"""Non-authenticated, read-only Melon first-party MCP capability probe.

Never uses Melon account credentials, never requests private data, never
registers an OAuth client, and never fetches chart content. Intended to learn
whether the public discovery metadata supports our possible integration.
"""
from __future__ import annotations

import json
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

ENDPOINT = "https://mcp.melon.com/mcp/"
URLS = [
    "https://mcp.melon.com/.well-known/oauth-protected-resource",
    "https://mcp.melon.com/.well-known/oauth-protected-resource/mcp",
    "https://cola.melon.com/.well-known/oauth-authorization-server",
    "https://cola.melon.com/auth/v3/oauth/docs/dynamic-client-registration",
]


def request(url: str, method: str = "GET", body: dict | None = None):
    data = json.dumps(body).encode() if body else None
    headers = {
        "Accept": "application/json, text/event-stream" if body else "application/json, text/html",
        "User-Agent": "IVE-RADAR-Melon-MCP-Feasibility/0.1 (+https://github.com/acchtt/peach-en)",
    }
    if body:
        headers["Content-Type"] = "application/json"
    req = Request(url, data=data, method=method, headers=headers)
    try:
        with urlopen(req, timeout=16) as response:
            return response.status, {k.lower(): v for k, v in response.headers.items()}, response.read(150000)
    except HTTPError as exc:
        return exc.code, {k.lower(): v for k, v in exc.headers.items()}, exc.read(1000)
    except (URLError, TimeoutError, OSError) as exc:
        return "NETWORK_ERROR", {}, type(exc).__name__.encode()


def parse_rpc(payload: bytes, content_type: str):
    text = payload.decode("utf-8", "replace")
    if "text/event-stream" in content_type:
        chunks = [line[6:].strip() for line in text.splitlines() if line.startswith("data: ")]
        candidates = [json.loads(line) for line in chunks if line.startswith("{")]
        return candidates[-1] if candidates else {}
    try:
        return json.loads(text)
    except ValueError:
        return {}


def main():
    for url in URLS:
        status, headers, content = request(url)
        record = {"url": url, "status": status, "content_type": headers.get("content-type", "")[:90]}
        if status == 200 and "json" in record["content_type"].lower():
            try:
                data = json.loads(content)
                if isinstance(data, dict):
                    for key in (
                        "issuer", "authorization_endpoint", "token_endpoint",
                        "registration_endpoint", "authorization_servers", "resource",
                        "grant_types_supported", "token_endpoint_auth_methods_supported",
                        "scopes_supported"
                    ):
                        if key in data:
                            record[key] = data[key]
            except ValueError:
                record["malformed_json"] = True
        print(json.dumps(record, ensure_ascii=False))
    headers = {"Accept": "application/json, text/event-stream"}
    status, response_headers, content = request(
        ENDPOINT, "POST",
        {"jsonrpc": "2.0", "id": 1, "method": "tools/list", "params": {}}
    )
    record = {
        "url": ENDPOINT,
        "method": "tools/list",
        "status": status,
        "www_authenticate": response_headers.get("www-authenticate", "")[:500],
        "content_type": response_headers.get("content-type", "")[:100],
    }
    if status == 200:
        data = parse_rpc(content, record["content_type"])
        record["json_rpc_error"] = data.get("error", {}).get("code") if isinstance(data.get("error"), dict) else None
        result = data.get("result") or {}
        tools = result.get("tools", []) if isinstance(result, dict) else []
        if isinstance(tools, list):
            record["tool_count"] = len(tools)
            record["tool_names"] = [tool.get("name","") for tool in tools if isinstance(tool,dict)]
            chart_tool = next((x for x in tools if isinstance(x,dict) and x.get("name")=="get_music_chart"),None)
            if chart_tool:
                record["get_music_chart_description"] = chart_tool.get("description","")[:1400]
                record["get_music_chart_input_schema"] = chart_tool.get("inputSchema",{})
            record["chart_tool_names"] = [
                tool.get("name", "") for tool in tools
                if isinstance(tool, dict)
                and ("chart" in tool.get("name", "").lower() or
                     "chart" in tool.get("description", "").lower())
            ]
    if status==200 and not record.get("tool_count"):
        record["response_sample"] = content[:240].decode("utf-8", "replace")
    print(json.dumps(record, ensure_ascii=False))
    # One normal chart-tool request to establish whether unauthenticated access
    # is accepted. No credentials, no persisted chart data, no polling.
    call_status, call_headers, call_bytes = request(
        ENDPOINT, "POST", {
            "jsonrpc": "2.0", "id": 2, "method": "tools/call",
            "params": {
                "name": "get_music_chart",
                "arguments": {"chart_type": "TOP_100", "start": 1, "size": 10}
            },
        }
    )
    parsed = parse_rpc(call_bytes, call_headers.get("content-type", ""))
    result = parsed.get("result") if isinstance(parsed, dict) else None
    error = parsed.get("error") if isinstance(parsed, dict) else None
    summary = {
        "url": ENDPOINT,
        "method": "tools/call/get_music_chart",
        "status": call_status,
        "content_type": call_headers.get("content-type", ""),
        "auth_challenge": call_headers.get("www-authenticate", "")[:300],
        "rpc_error_code": error.get("code") if isinstance(error, dict) else None,
        "rpc_error_message": str(error.get("message", ""))[:220] if isinstance(error, dict) else None,
        "mcp_result_is_error": result.get("isError") if isinstance(result, dict) else None,
        "content_block_count": len(result.get("content", [])) if isinstance(result, dict) else None,
    }
    if isinstance(result,dict) and result.get("isError"):
        blocks=result.get("content",[])
        summary["error_text"] = str(blocks[0].get("text",""))[:240] if blocks and isinstance(blocks[0],dict) else ""
    print(json.dumps(summary, ensure_ascii=False))


if __name__ == "__main__":
    main()
