import os
import json
from dotenv import load_dotenv

from langchain_core.tools import tool
from typing import Optional, Dict, Any
from experimental.utilities.vizql_data_service import list_datasources, call_mcp_tool, list_mcp_tools

# Load environment variables before accessing them
load_dotenv()

# MCP-backed utility tool: list Tableau datasources on the current site
@tool("list_tableau_datasources")
def list_tableau_datasources(filter: Optional[str] = None) -> str:
    """Return JSON array of datasources with id, name, projectName. Optional filter string."""
    mcp_url = os.getenv('TABLEAU_MCP_URL', 'https://tableau-mcp-bierschenk-2df05b623f7a.herokuapp.com/tableau-mcp')
    try:
        results = list_datasources(url=mcp_url, filter=filter)
        if not isinstance(results, list) or not results:
            return json.dumps([])
        out = []
        for ds in results:
            if isinstance(ds, dict):
                out.append({
                    'id': ds.get('id') or '',
                    'name': ds.get('name') or ds.get('contentUrl') or 'Unnamed',
                    'projectName': (ds.get('project') or {}).get('name') if isinstance(ds.get('project'), dict) else None
                })
        return json.dumps(out)
    except Exception as e:
        return json.dumps({'error': str(e)})

# Generic MCP tool pass-through
@tool("mcp_call")
def mcp_call(tool_name: str, arguments_json: str) -> str:
    """Call any MCP tool by name with raw JSON arguments. Use list_mcp_tools to discover available tools."""
    mcp_url = os.getenv('TABLEAU_MCP_URL', 'https://tableau-mcp-bierschenk-2df05b623f7a.herokuapp.com/tableau-mcp')
    try:
        # Parse the arguments JSON string into a Python dict
        arguments = json.loads(arguments_json) if arguments_json else {}
        result = call_mcp_tool(mcp_url, tool_name, arguments)
        return json.dumps(result)
    except Exception as e:
        return json.dumps({'error': str(e)})

@tool("list_mcp_tools")
def get_mcp_tools() -> str:
    """List all available MCP tools with their descriptions and parameter schemas."""
    mcp_url = os.getenv('TABLEAU_MCP_URL', 'https://tableau-mcp-bierschenk-2df05b623f7a.herokuapp.com/tableau-mcp')
    try:
        result = list_mcp_tools(mcp_url)
        return json.dumps(result)
    except Exception as e:
        return json.dumps({'error': str(e)})

# MCP-only tools registered for this agent
tools = [ list_tableau_datasources, mcp_call, get_mcp_tools ]
