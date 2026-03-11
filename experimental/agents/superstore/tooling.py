"""
Superstore Agent Tooling - Dynamic MCP Tool Integration

This module uses dynamic MCP tool discovery to automatically register all available
Tableau MCP tools, making the agent work like Claude Desktop with the Tableau MCP extension.
"""

from dotenv import load_dotenv
from experimental.utilities.mcp_tools_dynamic import get_mcp_tools

# Load environment variables before accessing them
load_dotenv()

# Dynamically load all MCP tools from the Tableau MCP server
# This automatically discovers and registers tools like:
# - list_datasources
# - get_datasource_metadata
# - query_datasource
# - get_workbook
# - list_workbooks
# - list_views
# - get_view_data
# - get_view_image
# - search_content
# - generate_pulse_insight_brief
# - list_pulse_metric_definitions
# - etc.
tools = get_mcp_tools()
