"""
Makana Agent Tooling - Filtered MCP Tools

This module loads MCP tools and filters datasource results to show ONLY healthcare-related datasources.
"""

from dotenv import load_dotenv
from experimental.utilities.mcp_tools_dynamic import get_mcp_tools
from langchain_core.tools import StructuredTool

load_dotenv()

# Get all MCP tools
all_tools = get_mcp_tools()

def create_filtered_list_datasources(original_tool, filter_keywords):
    """Create a filtered version of list_datasources that only shows relevant datasources"""

    # Get the MCPToolDiscovery instance to access raw data
    from experimental.utilities.mcp_tools_dynamic import MCPToolDiscovery
    import os

    def filtered_list_datasources(**kwargs):
        # Call MCP directly to get RAW unformatted data (not truncated!)
        mcp = MCPToolDiscovery(os.getenv('TABLEAU_MCP_URL'))
        raw_result = mcp.call_tool('list-datasources', kwargs)

        # Filter the raw list
        if isinstance(raw_result, list):
            filtered_ds = []
            for ds in raw_result:
                ds_name = ds.get('name', '').lower()
                project_name = ds.get('project', {}).get('name', '').lower()

                # ALWAYS exclude Admin Insights
                if 'admin insights' in project_name:
                    continue

                # Check if matches our keywords
                if any(keyword.lower() in ds_name for keyword in filter_keywords):
                    filtered_ds.append(ds)

            # Format the filtered results
            if len(filtered_ds) == 0:
                return f"No datasources found matching: {', '.join(filter_keywords)}"

            summary = f"Found {len(filtered_ds)} datasource{'s' if len(filtered_ds) != 1 else ''}:\n\n"
            for i, ds in enumerate(filtered_ds, 1):
                ds_id = ds.get('id', 'unknown')
                ds_name = ds.get('name', 'Unnamed')
                project = ds.get('project', {})
                project_name = project.get('name', 'Unknown') if isinstance(project, dict) else 'Unknown'
                summary += f"{i}. {ds_name} (ID: {ds_id}, Project: {project_name})\n"

            summary += "\nUse the datasource ID with get_datasource_metadata or query_datasource to work with a specific datasource."
            return summary

        # Fallback
        return f"No datasources found matching: {', '.join(filter_keywords)}"

    # Create new tool with same signature
    return StructuredTool(
        name=original_tool.name,
        description=original_tool.description,
        func=filtered_list_datasources,
        args_schema=original_tool.args_schema
    )

# Filter keywords for Makana agent
MAKANA_KEYWORDS = ['Makana', 'Health', 'Healthcare', 'Claims', 'Pharma', 'Clinical', 'Medical', 'HLS', 'Payer', 'Denial']

# Find and replace list_datasources with filtered version
tools = []
for tool in all_tools:
    if 'list' in tool.name.lower() and 'datasource' in tool.name.lower():
        # Replace with filtered version
        filtered_tool = create_filtered_list_datasources(tool, MAKANA_KEYWORDS)
        tools.append(filtered_tool)
    else:
        tools.append(tool)
