from typing import Dict, Any
import json
import requests
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


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

    logger.info(f"MCP Tool Call - Tool: {tool_name}, Arguments: {json.dumps(arguments, indent=2)}")

    try:
        response = requests.post(endpoint, headers=headers, data=json.dumps(payload), timeout=30)
        logger.info(f"MCP Response Status: {response.status_code}")
        logger.info(f"MCP Response Headers: {dict(response.headers)}")

        if response.status_code != 200:
            error_msg = f"MCP tool invocation failed: {tool_name}. Status code: {response.status_code}. Response: {response.text}"
            logger.error(error_msg)
            raise RuntimeError(error_msg)

        text = response.text
        logger.info(f"MCP Raw Response Text: {text[:500]}...")  # Log first 500 chars

        result_obj = None
        error_obj = None
        for line in text.splitlines():
            if line.startswith('data: '):
                try:
                    msg = json.loads(line[6:])
                    logger.info(f"MCP Data Line: {msg}")
                    if 'result' in msg:
                        result_obj = msg['result']
                        logger.info(f"MCP Result Object: {result_obj}")
                    elif 'error' in msg:
                        error_obj = msg['error']
                        logger.error(f"MCP Error Object: {error_obj}")
                except Exception as e:
                    logger.warning(f"Failed to parse data line: {line}, Error: {e}")
                    continue

        if error_obj is not None:
            error_msg = f"MCP tool error: {error_obj.get('message', 'Unknown error')}"
            logger.error(error_msg)
            raise RuntimeError(error_msg)

        if result_obj is None:
            logger.warning("No result found in data lines, trying to parse full body as JSON")
            try:
                body = json.loads(text)
                logger.info(f"MCP Full Body Result: {body}")
                if 'error' in body:
                    error_msg = f"MCP tool error: {body['error'].get('message', 'Unknown error')}"
                    logger.error(error_msg)
                    raise RuntimeError(error_msg)
                return body.get('result', body)
            except Exception as e:
                error_msg = f"MCP response parsing failed; no result found. Raw response: {text}"
                logger.error(error_msg)
                raise RuntimeError(error_msg)

        content = result_obj.get('content')
        logger.info(f"MCP Content: {content}")

        if isinstance(content, list) and content:
            for item in content:
                if isinstance(item, dict):
                    if item.get('type') == 'json' and 'json' in item:
                        logger.info(f"Returning JSON content: {item['json']}")
                        return item['json']
                    if item.get('type') in ['text', 'string'] and 'text' in item:
                        txt = item['text']
                        if isinstance(txt, str) and (txt.strip().startswith('{') or txt.strip().startswith('[')):
                            try:
                                parsed = json.loads(txt)
                                logger.info(f"Returning parsed text content: {parsed}")
                                return parsed
                            except Exception as e:
                                logger.warning(f"Failed to parse text content: {txt}, Error: {e}")
                                pass
            logger.info(f"Returning raw content: {content}")
            return content

        logger.info(f"Returning result object: {result_obj}")
        return result_obj

    except requests.exceptions.Timeout:
        error_msg = f"MCP tool call timed out: {tool_name}"
        logger.error(error_msg)
        raise RuntimeError(error_msg)
    except requests.exceptions.RequestException as e:
        error_msg = f"MCP tool call failed with request error: {tool_name}, Error: {str(e)}"
        logger.error(error_msg)
        raise RuntimeError(error_msg)
    except Exception as e:
        error_msg = f"Unexpected error in MCP tool call: {tool_name}, Error: {str(e)}"
        logger.error(error_msg)
        raise RuntimeError(error_msg)




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
