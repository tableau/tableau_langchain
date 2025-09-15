from typing import Dict, Any
import os
from .mcp_client import query_mcp_datasource, query_mcp_metadata


def query_vds(api_key: str, datasource_luid: str, url: str, query: Dict[str, Any]) -> Dict[str, Any]:
    """
    Query a datasource using MCP server instead of direct VDS API.
    This function maintains compatibility with existing code while using MCP.
    """
    # Get MCP server URL from environment or use default
    mcp_server_url = os.environ.get('MCP_SERVER_URL', 'https://your-mcp-server.herokuapp.com/tableau-mcp')

    return query_mcp_datasource(mcp_server_url, datasource_luid, query)


def query_vds_metadata(api_key: str, datasource_luid: str, url: str) -> Dict[str, Any]:
    """
    Get datasource metadata using MCP server instead of direct VDS API.
    This function maintains compatibility with existing code while using MCP.
    """
    # Get MCP server URL from environment or use default
    mcp_server_url = os.environ.get('MCP_SERVER_URL', 'https://your-mcp-server.herokuapp.com/tableau-mcp')

    return query_mcp_metadata(mcp_server_url, datasource_luid)
