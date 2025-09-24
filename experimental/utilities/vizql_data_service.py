from typing import Dict, Any
import json
import requests


def _invoke_mcp_tool(mcp_url: str, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
    endpoint = mcp_url.rstrip('/')
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json, text/event-stream'
    }
    payload = {
        "jsonrpc": "2.0",
        "id": "1",
        "method": "tools/call",
        "params": {
            "name": tool_name,
            "arguments": arguments
        }
    }
    response = requests.post(endpoint, headers=headers, data=json.dumps(payload))
    if response.status_code != 200:
        raise RuntimeError(
            f"MCP tool invocation failed: {tool_name}. Status code: {response.status_code}. Response: {response.text}"
        )
    text = response.text
    result_obj = None
    for line in text.splitlines():
        if line.startswith('data: '):
            try:
                msg = json.loads(line[6:])
                if 'result' in msg:
                    result_obj = msg['result']
            except Exception:
                continue
    if result_obj is None:
        try:
            body = json.loads(text)
            return body.get('result', body)
        except Exception:
            raise RuntimeError("MCP response parsing failed; no result found.")
    content = result_obj.get('content')
    if isinstance(content, list) and content:
        for item in content:
            if isinstance(item, dict):
                if item.get('type') == 'json' and 'json' in item:
                    return item['json']
                if item.get('type') in ['text', 'string'] and 'text' in item:
                    txt = item['text']
                    if isinstance(txt, str) and (txt.strip().startswith('{') or txt.strip().startswith('[')):
                        try:
                            return json.loads(txt)
                        except Exception:
                            pass
        return content
    return result_obj




def list_datasources(url: str, filter: str | None = None) -> Any:
    arguments: Dict[str, Any] = {}
    if isinstance(filter, str) and filter:
        arguments["filter"] = filter
    result = _invoke_mcp_tool(url, "list-datasources", arguments)
    # Ensure we always return a list
    if isinstance(result, dict) and 'data' in result:
        return result.get('data', [])
    return result if isinstance(result, list) else []




def call_mcp_tool(url: str, tool_name: str, arguments: Dict[str, Any]) -> Any:
    """Generic MCP tool caller using JSON-RPC tools/call. Arguments must be a dict serializable to JSON."""
    return _invoke_mcp_tool(url, tool_name, arguments)


def list_mcp_tools(url: str) -> Any:
    """Return the list of MCP tools by invoking JSON-RPC method tools/list over HTTP SSE."""
    endpoint = url.rstrip('/')
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json, text/event-stream'
    }
    payload = {
        "jsonrpc": "2.0",
        "id": "1",
        "method": "tools/list",
        "params": {}
    }
    response = requests.post(endpoint, headers=headers, data=json.dumps(payload))
    if response.status_code != 200:
        raise RuntimeError(f"MCP tools/list failed. Status code: {response.status_code}. Response: {response.text}")
    text = response.text
    for line in text.splitlines():
        if line.startswith('data: '):
            try:
                msg = json.loads(line[6:])
                if 'result' in msg:
                    return msg['result']
            except Exception:
                continue
    return {}
