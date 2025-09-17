import os
import json
from dotenv import load_dotenv

from experimental.tools.simple_datasource_qa import initialize_simple_datasource_qa
from langchain_core.tools import tool
from typing import Optional, Dict, Any
from experimental.utilities.vizql_data_service import list_datasources, call_mcp_tool, list_mcp_tools

# Load environment variables before accessing them
load_dotenv()
tableau_domain = os.environ['TABLEAU_DOMAIN']
tableau_site = os.environ['TABLEAU_SITE']
tableau_jwt_client_id = os.environ['TABLEAU_JWT_CLIENT_ID']
tableau_jwt_secret_id = os.environ['TABLEAU_JWT_SECRET_ID']
tableau_jwt_secret = os.environ['TABLEAU_JWT_SECRET']
tableau_api_version = os.environ['TABLEAU_API_VERSION']
tableau_user = os.environ['TABLEAU_USER']
datasource_luid = os.environ['DATASOURCE_LUID']
model_provider = os.environ['MODEL_PROVIDER']
tooling_llm_model = os.environ['TOOLING_MODEL']

# Direct MCP tools only - no intermediate layers
mcp_url = os.getenv('TABLEAU_MCP_URL', 'https://tableau-mcp-bierschenk-2df05b623f7a.herokuapp.com/tableau-mcp')

# Build tools list with MCP-backed tools only
tools = []

# MCP-backed utility tool: list Tableau datasources on the current site
@tool("list-datasources")
def list_datasources_tool(filter: Optional[str] = None) -> str:
    """List all available Tableau datasources. Optional filter parameter to search by name."""
    try:
        arguments = {}
        if filter:
            arguments["filter"] = filter
        result = call_mcp_tool(mcp_url, "list-datasources", arguments)
        return json.dumps(result)
    except Exception as e:
        return f"Error: {str(e)}"

@tool("list-fields")
def list_fields_tool(datasourceLuid: str) -> str:
    """List all fields in a Tableau datasource. Requires datasourceLuid parameter."""
    try:
        arguments = {"datasourceLuid": datasourceLuid}
        result = call_mcp_tool(mcp_url, "list-fields", arguments)
        return json.dumps(result)
    except Exception as e:
        return f"Error: {str(e)}"

@tool("query-datasource")
def query_datasource_tool(datasourceLuid: str, query: Dict[str, Any]) -> str:
    """Query a Tableau datasource with a structured query. Requires datasourceLuid and query parameters."""
    try:
        arguments = {
            "datasourceLuid": datasourceLuid,
            "query": query
        }
        result = call_mcp_tool(mcp_url, "query-datasource", arguments)
        return json.dumps(result)
    except Exception as e:
        return f"Error: {str(e)}"

@tool("read-metadata")
def read_metadata_tool(datasourceLuid: str) -> str:
    """Read metadata for a Tableau datasource. Requires datasourceLuid parameter."""
    try:
        arguments = {"datasourceLuid": datasourceLuid}
        result = call_mcp_tool(mcp_url, "read-metadata", arguments)
        return json.dumps(result)
    except Exception as e:
        return f"Error: {str(e)}"

@tool("tools-list")
def list_tools_tool() -> str:
    """List all available MCP tools with their descriptions and parameter schemas."""
    try:
        result = list_mcp_tools(mcp_url)
        return json.dumps(result)
    except Exception as e:
        return f"Error: {str(e)}"

tools.extend([list_datasources_tool, list_fields_tool, query_datasource_tool, read_metadata_tool, list_tools_tool])
