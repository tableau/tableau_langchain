"""
Cumulus Agent Tooling - Dynamic MCP Tool Integration

This module uses dynamic MCP tool discovery to automatically register all available
Tableau MCP tools, making the agent work like Claude Desktop with the Tableau MCP extension.
"""

from dotenv import load_dotenv
from experimental.utilities.mcp_tools_dynamic import get_mcp_tools

# Load environment variables before accessing them
load_dotenv()

# Dynamically load all MCP tools from the Tableau MCP server
tools = get_mcp_tools()
