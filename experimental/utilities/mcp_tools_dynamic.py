"""
Dynamic MCP Tool Loader for LangGraph Agents

This module automatically discovers and wraps MCP server tools as LangChain tools,
making agents work like Claude Desktop with the Tableau MCP extension.
"""

import os
import json
import requests
import logging
from typing import Dict, Any, List, Optional
from langchain_core.tools import tool, StructuredTool
from pydantic import BaseModel, Field, create_model
from dotenv import load_dotenv

load_dotenv()
# Set up logging - only DEBUG level if DEBUG=1, otherwise WARNING
if os.getenv('DEBUG') == '1':
    logging.basicConfig(level=logging.DEBUG)
else:
    logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)

# Module-level session for connection pooling
_session = None

def _get_session():
    """Get or create a shared requests Session with connection pooling."""
    global _session
    if _session is None:
        _session = requests.Session()
        adapter = requests.adapters.HTTPAdapter(
            pool_connections=10,
            pool_maxsize=20,
            max_retries=0
        )
        _session.mount('http://', adapter)
        _session.mount('https://', adapter)
    return _session


class MCPToolDiscovery:
    """Discovers and wraps MCP tools as LangChain tools."""

    def __init__(self, mcp_url: Optional[str] = None):
        self.mcp_url = mcp_url or os.getenv('TABLEAU_MCP_URL')
        if not self.mcp_url:
            raise ValueError("TABLEAU_MCP_URL not set in environment")
        self.tools_cache = None

    def _call_mcp_jsonrpc(self, method: str, params: Dict[str, Any]) -> Any:
        """Make a JSON-RPC call to the MCP server."""
        endpoint = self.mcp_url.rstrip('/')
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json, text/event-stream'
        }
        payload = {
            "jsonrpc": "2.0",
            "id": "1",
            "method": method,
            "params": params
        }

        try:
            session = _get_session()
            response = session.post(endpoint, headers=headers, data=json.dumps(payload), timeout=30)
            if response.status_code != 200:
                raise RuntimeError(f"MCP call failed: {method}. Status: {response.status_code}")

            text = response.text

            # Parse SSE response
            for line in text.splitlines():
                if line.startswith('data: '):
                    try:
                        msg = json.loads(line[6:])
                        if 'result' in msg:
                            return msg['result']
                        elif 'error' in msg:
                            raise RuntimeError(f"MCP error: {msg['error']}")
                    except json.JSONDecodeError:
                        continue

            # Fallback: try parsing full body
            try:
                body = json.loads(text)
                if 'error' in body:
                    raise RuntimeError(f"MCP error: {body['error']}")
                return body.get('result', body)
            except:
                raise RuntimeError(f"Failed to parse MCP response for {method}")

        except requests.exceptions.Timeout:
            raise RuntimeError(f"MCP call timed out: {method}")
        except Exception as e:
            logger.error(f"MCP call failed: {method}, Error: {e}")
            raise

    def discover_tools(self) -> List[Dict[str, Any]]:
        """Discover all available tools from the MCP server."""
        if self.tools_cache is not None:
            return self.tools_cache

        logger.debug(f"Discovering MCP tools from {self.mcp_url}")
        result = self._call_mcp_jsonrpc("tools/list", {})

        if isinstance(result, dict) and 'tools' in result:
            self.tools_cache = result['tools']
        else:
            self.tools_cache = []

        logger.debug(f"Discovered {len(self.tools_cache)} MCP tools")
        return self.tools_cache

    def _format_result_for_agent(self, tool_name: str, result: Any) -> str:
        """Format tool results to be agent-friendly (concise and readable)."""
        # Handle list-datasources specially - summarize the list
        if tool_name == 'list-datasources' and isinstance(result, list):
            if len(result) == 0:
                return "No datasources found."

            # Create a concise summary
            summary = f"Found {len(result)} datasources:\n\n"
            for i, ds in enumerate(result[:10], 1):  # Limit to first 10
                ds_id = ds.get('id', 'unknown')
                ds_name = ds.get('name', 'Unnamed')
                project = ds.get('project', {})
                project_name = project.get('name', 'Unknown') if isinstance(project, dict) else 'Unknown'
                summary += f"{i}. {ds_name} (ID: {ds_id}, Project: {project_name})\n"

            if len(result) > 10:
                summary += f"\n... and {len(result) - 10} more datasources.\n"

            summary += "\nUse the datasource ID with get_datasource_metadata or query_datasource to work with a specific datasource."
            return summary

        # Handle get-datasource-metadata specially - format fields nicely
        elif tool_name == 'get-datasource-metadata' and isinstance(result, dict):
            fields = result.get('fields', [])
            if not isinstance(fields, list):
                # Fallback if fields is not a list
                return json.dumps(result, indent=2)

            description = result.get('description', 'No description available')

            summary = f"Datasource Metadata:\n"
            summary += f"Description: {description}\n\n"
            summary += f"Fields ({len(fields)} total):\n"

            # Group by role (dimensions vs measures)
            dimensions = [f for f in fields if isinstance(f, dict) and f.get('role') == 'dimension']
            measures = [f for f in fields if isinstance(f, dict) and f.get('role') == 'measure']
            other_fields = [f for f in fields if isinstance(f, dict) and f.get('role') not in ['dimension', 'measure']]

            if dimensions:
                summary += f"\nDimensions ({len(dimensions)}):\n"
                for f in dimensions[:10]:  # Show first 10 fields
                    name = f.get('name', f.get('caption', 'Unknown'))
                    data_type = f.get('dataType', 'unknown')
                    summary += f"  - {name} ({data_type})\n"
                if len(dimensions) > 10:
                    summary += f"  ... and {len(dimensions) - 10} more dimensions\n"

            if measures:
                summary += f"\nMeasures ({len(measures)}):\n"
                for f in measures[:10]:  # Show first 10 fields
                    name = f.get('name', f.get('caption', 'Unknown'))
                    data_type = f.get('dataType', 'unknown')
                    aggregation = f.get('aggregation', 'none')
                    summary += f"  - {name} ({data_type}, agg: {aggregation})\n"
                if len(measures) > 10:
                    summary += f"  ... and {len(measures) - 10} more measures\n"

            if other_fields:
                summary += f"\nOther Fields ({len(other_fields)}):\n"
                for f in other_fields[:10]:
                    name = f.get('name', f.get('caption', 'Unknown'))
                    data_type = f.get('dataType', 'unknown')
                    summary += f"  - {name} ({data_type})\n"
                if len(other_fields) > 10:
                    summary += f"  ... and {len(other_fields) - 10} more fields\n"

            summary += "\nUse these field names exactly as shown when calling query_datasource."
            return summary

        # Handle query-datasource specially - format data as a table
        elif tool_name == 'query-datasource' and isinstance(result, dict):
            data = result.get('data', [])

            if not data:
                return "Query returned no data."

            summary = f"Query Results ({len(data)} rows):\n\n"

            # Get column headers from first data row if not provided
            if isinstance(data[0], dict):
                headers = list(data[0].keys())

                # Header
                summary += " | ".join(headers) + "\n"
                summary += "-" * (len(" | ".join(headers))) + "\n"

                # Rows (limit to first 20 for better visibility)
                for row in data[:20]:
                    row_values = [str(row.get(h, '')) for h in headers]
                    summary += " | ".join(row_values) + "\n"

                if len(data) > 20:
                    summary += f"\n... and {len(data) - 20} more rows (showing first 20)\n"
            else:
                # Fallback: return raw JSON if structure is unexpected
                summary += json.dumps(data, indent=2)

            return summary

        # Default: return JSON for other tools
        if isinstance(result, str):
            return result
        else:
            return json.dumps(result, indent=2)

    def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Any:
        """Call an MCP tool by name with arguments."""
        logger.debug(f"Calling MCP tool: {tool_name} with args: {arguments}")
        result = self._call_mcp_jsonrpc("tools/call", {
            "name": tool_name,
            "arguments": arguments
        })

        # Extract content from result
        if isinstance(result, dict) and 'content' in result:
            content = result['content']
            if isinstance(content, list) and content:
                for item in content:
                    if isinstance(item, dict):
                        # Return JSON content if available
                        if item.get('type') == 'json' and 'json' in item:
                            return item['json']
                        # Try parsing text content as JSON
                        if item.get('type') in ['text', 'string'] and 'text' in item:
                            txt = item['text']
                            if isinstance(txt, str) and (txt.strip().startswith('{') or txt.strip().startswith('[')):
                                try:
                                    return json.loads(txt)
                                except:
                                    return txt
                            return txt
                return content

        return result

    def create_langchain_tools(self) -> List[StructuredTool]:
        """Create LangChain tools from discovered MCP tools."""
        mcp_tools = self.discover_tools()
        langchain_tools = []

        for mcp_tool in mcp_tools:
            tool_name = mcp_tool.get('name', '')
            description = mcp_tool.get('description', f"MCP tool: {tool_name}")
            input_schema = mcp_tool.get('inputSchema', {})

            # Create LangChain tool wrapper
            lc_tool = self._create_structured_tool(tool_name, description, input_schema)
            if lc_tool:
                langchain_tools.append(lc_tool)
                logger.info(f"Registered MCP tool: {tool_name}")

        return langchain_tools

    def _create_structured_tool(
        self,
        tool_name: str,
        description: str,
        input_schema: Dict[str, Any]
    ) -> Optional[StructuredTool]:
        """Create a StructuredTool from MCP tool schema."""
        try:
            # Build Pydantic model from input schema
            properties = input_schema.get('properties', {})
            required = input_schema.get('required', [])

            # Create field definitions for Pydantic model
            field_definitions = {}
            for prop_name, prop_schema in properties.items():
                prop_type = prop_schema.get('type', 'string')
                prop_desc = prop_schema.get('description', '')

                # Map JSON schema types to Python types
                python_type = str  # default
                if prop_type == 'string':
                    python_type = str
                elif prop_type == 'number':
                    python_type = float
                elif prop_type == 'integer':
                    python_type = int
                elif prop_type == 'boolean':
                    python_type = bool
                elif prop_type == 'array':
                    python_type = List[Any]
                elif prop_type == 'object':
                    python_type = Dict[str, Any]

                # Make field optional if not required
                if prop_name not in required:
                    python_type = Optional[python_type]
                    field_definitions[prop_name] = (python_type, Field(None, description=prop_desc))
                else:
                    field_definitions[prop_name] = (python_type, Field(..., description=prop_desc))

            # Handle tools with no parameters
            if not field_definitions:
                field_definitions['dummy_param'] = (Optional[str], Field(None, description="No parameters required"))

            # Create dynamic Pydantic model
            InputModel = create_model(
                f"{tool_name.replace('-', '_').title()}Input",
                **field_definitions
            )

            # Create the tool function
            def tool_func(**kwargs) -> str:
                # Remove dummy field if present
                kwargs.pop('dummy_param', None)
                # Remove None/null values - MCP server expects parameters to be omitted, not null
                cleaned_kwargs = {k: v for k, v in kwargs.items() if v is not None}
                try:
                    result = self.call_tool(tool_name, cleaned_kwargs)
                    # Format result to be agent-friendly
                    formatted = self._format_result_for_agent(tool_name, result)
                    return formatted
                except Exception as e:
                    error_msg = f"Error invoking tool '{tool_name}' with kwargs {cleaned_kwargs} with error: {str(e)}\nPlease fix the error and try again."
                    logger.error(error_msg)
                    return error_msg

            # Create StructuredTool
            return StructuredTool(
                name=tool_name.replace('-', '_'),  # LangChain prefers underscores
                description=description.strip() or f"MCP tool: {tool_name}",
                func=tool_func,
                args_schema=InputModel
            )

        except Exception as e:
            logger.error(f"Failed to create tool {tool_name}: {e}")
            return None


def get_mcp_tools(mcp_url: Optional[str] = None) -> List[StructuredTool]:
    """
    Main entry point: Get all MCP tools as LangChain StructuredTool instances.

    Usage:
        from experimental.utilities.mcp_tools_dynamic import get_mcp_tools
        tools = get_mcp_tools()
    """
    discovery = MCPToolDiscovery(mcp_url)
    return discovery.create_langchain_tools()


# Also provide a simple pass-through tool for backwards compatibility
@tool("list_tableau_datasources")
def list_tableau_datasources(filter: Optional[str] = None) -> str:
    """List all Tableau datasources. Deprecated - use list_datasources instead."""
    discovery = MCPToolDiscovery()
    try:
        args = {}
        if filter:
            args['filter'] = filter
        result = discovery.call_tool('list-datasources', args)

        # Format result
        if isinstance(result, list):
            out = []
            for ds in result:
                if isinstance(ds, dict):
                    out.append({
                        'id': ds.get('id', ''),
                        'name': ds.get('name', ds.get('contentUrl', 'Unnamed')),
                        'projectName': (ds.get('project') or {}).get('name') if isinstance(ds.get('project'), dict) else None
                    })
            return json.dumps(out)
        return json.dumps(result)
    except Exception as e:
        return json.dumps({'error': str(e)})
