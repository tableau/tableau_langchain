"""
Enhanced Tableau MCP Tool that can handle various types of questions about Tableau resources.
This tool provides access to all available MCP tools for comprehensive Tableau integration.
"""

from typing import Dict, Any, Optional, List
from langchain.tools import BaseTool
from pydantic import BaseModel, Field
from experimental.utilities.mcp_client import MCPClient
import os


class TableauMCPToolInput(BaseModel):
    """Input for the Tableau MCP Tool."""
    question: str = Field(description="The question about Tableau resources (e.g., 'What data sources are available?', 'List workbooks', 'Show me views in workbook X')")
    site_id: Optional[str] = Field(default=None, description="Optional site ID to filter results")


class TableauMCPTool(BaseTool):
    """Enhanced tool for interacting with Tableau resources via MCP server."""

    name: str = "tableau_mcp_tool"
    description: str = """
    A comprehensive tool for interacting with Tableau resources through the MCP server.
    Can answer questions about:
    - Available data sources
    - Available workbooks
    - Views and dashboards in workbooks
    - Pulse metrics and definitions
    - Data source metadata and fields
    - And much more!

    Examples:
    - "What data sources are available?"
    - "List all workbooks"
    - "Show me views in workbook abc123"
    - "What dashboards are in workbook xyz789?"
    - "List pulse metrics"
    """
    args_schema = TableauMCPToolInput

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Get MCP server URL from environment or use default
        self._mcp_server_url = os.environ.get('MCP_SERVER_URL', 'https://your-mcp-server.herokuapp.com/tableau-mcp')
        self._client = MCPClient(self._mcp_server_url)

    def _run(self, question: str, site_id: Optional[str] = None) -> str:
        """Execute the tool based on the question asked."""
        try:
            question_lower = question.lower()

            # Handle data source related questions
            if any(keyword in question_lower for keyword in ['data source', 'datasource', 'data sources', 'datasources']):
                if 'list' in question_lower or 'show' in question_lower or 'available' in question_lower:
                    result = self._client.list_datasources(site_id)
                    return self._format_datasources_response(result)
                elif 'metadata' in question_lower or 'fields' in question_lower:
                    # This would need a specific datasource LUID
                    return "To get data source metadata, please specify the data source LUID. Use 'list data sources' first to see available options."

            # Handle workbook related questions
            elif any(keyword in question_lower for keyword in ['workbook', 'workbooks']):
                if 'list' in question_lower or 'show' in question_lower or 'available' in question_lower:
                    result = self._client.list_workbooks(site_id)
                    return self._format_workbooks_response(result)
                elif 'view' in question_lower and 'in' in question_lower:
                    # Extract workbook LUID from question
                    workbook_luid = self._extract_workbook_luid(question)
                    if workbook_luid:
                        result = self._client.list_views(workbook_luid)
                        return self._format_views_response(result)
                elif 'dashboard' in question_lower and 'in' in question_lower:
                    # Extract workbook LUID from question
                    workbook_luid = self._extract_workbook_luid(question)
                    if workbook_luid:
                        return "Dashboard listing is not available through the MCP server. You can use 'list views' to see available views in a workbook."

            # Handle view related questions
            elif any(keyword in question_lower for keyword in ['view', 'views']):
                if 'list' in question_lower or 'show' in question_lower:
                    # This would need a specific workbook LUID
                    return "To list views, please specify the workbook LUID. Use 'list workbooks' first to see available options."

            # Handle dashboard related questions
            elif any(keyword in question_lower for keyword in ['dashboard', 'dashboards']):
                if 'list' in question_lower or 'show' in question_lower:
                    # This would need a specific workbook LUID
                    return "To list dashboards, please specify the workbook LUID. Use 'list workbooks' first to see available options."

            # Handle pulse metrics questions
            elif any(keyword in question_lower for keyword in ['pulse', 'metric', 'metrics']):
                if 'list' in question_lower or 'show' in question_lower or 'available' in question_lower:
                    result = self._client.list_pulse_metrics(site_id)
                    return self._format_pulse_metrics_response(result)

            # Default response for unrecognized questions
            else:
                return f"""
I can help you with various Tableau resource questions. Here are some examples:

**Data Sources:**
- "What data sources are available?"
- "List all data sources"

**Workbooks:**
- "What workbooks are available?"
- "List all workbooks"
- "Show me views in workbook [workbook_luid]"
- "Show me dashboards in workbook [workbook_luid]"

**Pulse Metrics:**
- "List pulse metrics"
- "What pulse metrics are available?"

**General:**
- "What can you help me with?"

Please ask a specific question about Tableau resources, and I'll do my best to help!
                """

        except Exception as e:
            return f"Error accessing Tableau MCP server: {str(e)}"

    def _extract_workbook_luid(self, question: str) -> Optional[str]:
        """Extract workbook LUID from question text."""
        # This is a simple extraction - in practice, you might want more sophisticated parsing
        words = question.split()
        for i, word in enumerate(words):
            if word.lower() in ['workbook', 'in'] and i + 1 < len(words):
                return words[i + 1]
        return None

    def _format_datasources_response(self, result: Dict[str, Any]) -> str:
        """Format data sources response."""
        if not result:
            return "No data sources found or error retrieving data sources."

        # Check if this is a notification message
        if 'method' in result and 'params' in result:
            # This is a notification, not the actual result
            return "No data sources found or error retrieving data sources."

        # Check if this is the actual result
        if 'content' not in result:
            return "No data sources found or error retrieving data sources."

        # Parse the content which is a JSON string
        try:
            import json
            content = result['content'][0]['text']
            datasources = json.loads(content)
        except (KeyError, IndexError, json.JSONDecodeError) as e:
            return "Error parsing data sources response."

        if not datasources:
            return "No data sources available."

        response = "**Available Data Sources:**\n\n"
        for i, ds in enumerate(datasources[:10], 1):  # Limit to first 10
            name = ds.get('name', 'Unknown')
            luid = ds.get('id', 'Unknown')
            description = ds.get('description', 'No description')
            project = ds.get('project', {}).get('name', 'Unknown')
            response += f"{i}. **{name}**\n"
            response += f"   - LUID: `{luid}`\n"
            response += f"   - Project: {project}\n"
            response += f"   - Description: {description}\n\n"

        if len(datasources) > 10:
            response += f"... and {len(datasources) - 10} more data sources.\n"

        return response

    def _format_workbooks_response(self, result: Dict[str, Any]) -> str:
        """Format workbooks response."""
        if not result:
            return "No workbooks found or error retrieving workbooks."

        # Check if this is a notification message
        if 'method' in result and 'params' in result:
            # This is a notification, not the actual result
            return "No workbooks found or error retrieving workbooks."

        # Check if this is the actual result
        if 'content' not in result:
            return "No workbooks found or error retrieving workbooks."

        # Parse the content which is a JSON string
        try:
            import json
            content = result['content'][0]['text']
            workbooks = json.loads(content)
        except (KeyError, IndexError, json.JSONDecodeError) as e:
            return "Error parsing workbooks response."

        if not workbooks:
            return "No workbooks available."

        response = "**Available Workbooks:**\n\n"
        for i, wb in enumerate(workbooks[:10], 1):  # Limit to first 10
            name = wb.get('name', 'Unknown')
            luid = wb.get('id', 'Unknown')
            description = wb.get('description', 'No description')
            project = wb.get('project', {}).get('name', 'Unknown')
            response += f"{i}. **{name}**\n"
            response += f"   - LUID: `{luid}`\n"
            response += f"   - Project: {project}\n"
            response += f"   - Description: {description}\n\n"

        if len(workbooks) > 10:
            response += f"... and {len(workbooks) - 10} more workbooks.\n"

        return response

    def _format_views_response(self, result: Dict[str, Any]) -> str:
        """Format views response."""
        if not result or 'views' not in result:
            return "No views found or error retrieving views."

        views = result['views']
        if not views:
            return "No views available in this workbook."

        response = "**Views in Workbook:**\n\n"
        for i, view in enumerate(views[:10], 1):  # Limit to first 10
            name = view.get('name', 'Unknown')
            luid = view.get('luid', 'Unknown')
            view_type = view.get('viewType', 'Unknown')
            response += f"{i}. **{name}**\n"
            response += f"   - LUID: `{luid}`\n"
            response += f"   - Type: {view_type}\n\n"

        if len(views) > 10:
            response += f"... and {len(views) - 10} more views.\n"

        return response

    def _format_dashboards_response(self, result: Dict[str, Any]) -> str:
        """Format dashboards response."""
        if not result or 'dashboards' not in result:
            return "No dashboards found or error retrieving dashboards."

        dashboards = result['dashboards']
        if not dashboards:
            return "No dashboards available in this workbook."

        response = "**Dashboards in Workbook:**\n\n"
        for i, dashboard in enumerate(dashboards[:10], 1):  # Limit to first 10
            name = dashboard.get('name', 'Unknown')
            luid = dashboard.get('luid', 'Unknown')
            response += f"{i}. **{name}**\n"
            response += f"   - LUID: `{luid}`\n\n"

        if len(dashboards) > 10:
            response += f"... and {len(dashboards) - 10} more dashboards.\n"

        return response

    def _format_pulse_metrics_response(self, result: Dict[str, Any]) -> str:
        """Format pulse metrics response."""
        if not result or 'metrics' not in result:
            return "No pulse metrics found or error retrieving pulse metrics."

        metrics = result['metrics']
        if not metrics:
            return "No pulse metrics available."

        response = "**Available Pulse Metrics:**\n\n"
        for i, metric in enumerate(metrics[:10], 1):  # Limit to first 10
            name = metric.get('name', 'Unknown')
            luid = metric.get('luid', 'Unknown')
            description = metric.get('description', 'No description')
            response += f"{i}. **{name}**\n"
            response += f"   - LUID: `{luid}`\n"
            response += f"   - Description: {description}\n\n"

        if len(metrics) > 10:
            response += f"... and {len(metrics) - 10} more pulse metrics.\n"

        return response


def initialize_tableau_mcp_tool() -> TableauMCPTool:
    """Initialize the Tableau MCP Tool."""
    return TableauMCPTool()
