from typing import Dict, Any, Optional
import requests
import json


class MCPClient:
    """Client for interacting with Tableau MCP server"""

    def __init__(self, mcp_server_url: str):
        self.mcp_server_url = mcp_server_url.rstrip('/')

    def query_datasource(self, datasource_luid: str, query: Dict[str, Any]) -> Dict[str, Any]:
        """
        Query a datasource using the MCP server

        Args:
            datasource_luid (str): The LUID of the datasource to query
            query (Dict[str, Any]): The VDS query payload

        Returns:
            Dict[str, Any]: The query response data
        """
        # MCP uses JSON-RPC format
        payload = {
            "jsonrpc": "2.0",
            "method": "tools/call",
            "params": {
                "name": "query-datasource",
                "arguments": {
                    "datasourceLuid": datasource_luid,
                    "query": query
                }
            },
            "id": 1
        }

        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json, text/event-stream'
        }

        try:
            response = requests.post(self.mcp_server_url, headers=headers, json=payload, timeout=30)
            response.raise_for_status()

            # Parse the Server-Sent Events response
            response_text = response.text
            if "event: message" in response_text and "data:" in response_text:
                # Extract JSON from SSE format
                lines = response_text.split('\n')
                for line in lines:
                    if line.startswith('data: '):
                        data_json = line[6:]  # Remove 'data: ' prefix
                        result = json.loads(data_json)
                        if 'result' in result:
                            return result['result']
                        elif 'error' in result:
                            raise RuntimeError(f"MCP server error: {result['error']}")
                        else:
                            return result

            # Fallback to direct JSON response
            return response.json()
        except requests.exceptions.RequestException as e:
            error_message = (
                f"Failed to query datasource via MCP server. "
                f"Status code: {getattr(e.response, 'status_code', 'Unknown')}. "
                f"Error: {str(e)}"
            )
            raise RuntimeError(error_message)

    def get_datasource_metadata(self, datasource_luid: str) -> Dict[str, Any]:
        """
        Get datasource metadata using the MCP server

        Args:
            datasource_luid (str): The LUID of the datasource

        Returns:
            Dict[str, Any]: The metadata response
        """
        # MCP uses JSON-RPC format
        payload = {
            "jsonrpc": "2.0",
            "method": "tools/call",
            "params": {
                "name": "read-metadata",
                "arguments": {
                    "datasourceLuid": datasource_luid
                }
            },
            "id": 1
        }

        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json, text/event-stream'
        }

        try:
            response = requests.post(self.mcp_server_url, headers=headers, json=payload, timeout=30)
            response.raise_for_status()

            # Parse the Server-Sent Events response
            response_text = response.text
            if "event: message" in response_text and "data:" in response_text:
                # Extract JSON from SSE format
                lines = response_text.split('\n')
                for line in lines:
                    if line.startswith('data: '):
                        data_json = line[6:]  # Remove 'data: ' prefix
                        result = json.loads(data_json)
                        if 'result' in result:
                            return result['result']
                        elif 'error' in result:
                            raise RuntimeError(f"MCP server error: {result['error']}")
                        else:
                            return result

            # Fallback to direct JSON response
            return response.json()
        except requests.exceptions.RequestException as e:
            error_message = (
                f"Failed to get datasource metadata from MCP server. "
                f"Status code: {getattr(e.response, 'status_code', 'Unknown')}. "
                f"Error: {str(e)}"
            )
            raise RuntimeError(error_message)

    def get_data_dictionary(self, datasource_luid: str) -> Dict[str, Any]:
        """
        Get data dictionary for a datasource using the MCP server

        Args:
            datasource_luid (str): The LUID of the datasource

        Returns:
            Dict[str, Any]: The data dictionary response
        """
        return self._call_mcp_tool("list-fields", {"datasourceLuid": datasource_luid})

    def list_datasources(self, site_id: str = None) -> Dict[str, Any]:
        """
        List all available data sources using the MCP server

        Args:
            site_id (str, optional): The site ID to list datasources from

        Returns:
            Dict[str, Any]: List of data sources
        """
        args = {}
        if site_id:
            args["siteId"] = site_id
        return self._call_mcp_tool("list-datasources", args)

    def list_workbooks(self, site_id: str = None) -> Dict[str, Any]:
        """
        List all available workbooks using the MCP server

        Args:
            site_id (str, optional): The site ID to list workbooks from

        Returns:
            Dict[str, Any]: List of workbooks
        """
        args = {}
        if site_id:
            args["siteId"] = site_id
        return self._call_mcp_tool("list-workbooks", args)

    def list_views(self, workbook_luid: str) -> Dict[str, Any]:
        """
        List views in a workbook using the MCP server

        Args:
            workbook_luid (str): The LUID of the workbook

        Returns:
            Dict[str, Any]: List of views
        """
        return self._call_mcp_tool("list-views", {"workbookLuid": workbook_luid})

    def list_dashboards(self, workbook_luid: str) -> Dict[str, Any]:
        """
        List dashboards in a workbook using the MCP server

        Args:
            workbook_luid (str): The LUID of the workbook

        Returns:
            Dict[str, Any]: List of dashboards
        """
        return self._call_mcp_tool("list-dashboards", {"workbookLuid": workbook_luid})

    def list_pulse_metrics(self, site_id: str = None) -> Dict[str, Any]:
        """
        List Pulse metrics using the MCP server

        Args:
            site_id (str, optional): The site ID to list metrics from

        Returns:
            Dict[str, Any]: List of Pulse metrics
        """
        args = {}
        if site_id:
            args["siteId"] = site_id
        return self._call_mcp_tool("list-pulse-metrics", args)

    def _call_mcp_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generic method to call any MCP tool

        Args:
            tool_name (str): The name of the MCP tool to call
            arguments (Dict[str, Any]): The arguments for the tool

        Returns:
            Dict[str, Any]: The tool response
        """
        # MCP uses JSON-RPC format
        payload = {
            "jsonrpc": "2.0",
            "method": "tools/call",
            "params": {
                "name": tool_name,
                "arguments": arguments
            },
            "id": 1
        }

        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json, text/event-stream'
        }

        try:
            response = requests.post(self.mcp_server_url, headers=headers, json=payload, timeout=30)
            response.raise_for_status()

            # Parse the Server-Sent Events response
            response_text = response.text
            if "event: message" in response_text and "data:" in response_text:
                # Extract JSON from SSE format
                lines = response_text.split('\n')
                for line in lines:
                    if line.startswith('data: '):
                        data_json = line[6:]  # Remove 'data: ' prefix
                        result = json.loads(data_json)
                        if 'result' in result:
                            return result['result']
                        elif 'error' in result:
                            raise RuntimeError(f"MCP server error: {result['error']}")
                        else:
                            return result

            # Fallback to direct JSON response
            return response.json()
        except requests.exceptions.RequestException as e:
            error_message = (
                f"Failed to call MCP tool '{tool_name}'. "
                f"Status code: {getattr(e.response, 'status_code', 'Unknown')}. "
                f"Error: {str(e)}"
            )
            raise RuntimeError(error_message)


# Convenience functions to maintain compatibility with existing code
def query_mcp_datasource(mcp_server_url: str, datasource_luid: str, query: Dict[str, Any]) -> Dict[str, Any]:
    """Query a datasource using MCP server - convenience function"""
    client = MCPClient(mcp_server_url)
    return client.query_datasource(datasource_luid, query)


def query_mcp_metadata(mcp_server_url: str, datasource_luid: str) -> Dict[str, Any]:
    """Get datasource metadata using MCP server - convenience function"""
    client = MCPClient(mcp_server_url)
    return client.get_datasource_metadata(datasource_luid)


def get_mcp_data_dictionary(mcp_server_url: str, datasource_luid: str) -> Dict[str, Any]:
    """Get data dictionary using MCP server - convenience function"""
    client = MCPClient(mcp_server_url)
    return client.get_data_dictionary(datasource_luid)


def list_mcp_datasources(mcp_server_url: str, site_id: str = None) -> Dict[str, Any]:
    """List all available data sources using MCP server - convenience function"""
    client = MCPClient(mcp_server_url)
    return client.list_datasources(site_id)


def list_mcp_workbooks(mcp_server_url: str, site_id: str = None) -> Dict[str, Any]:
    """List all available workbooks using MCP server - convenience function"""
    client = MCPClient(mcp_server_url)
    return client.list_workbooks(site_id)


def list_mcp_views(mcp_server_url: str, workbook_luid: str) -> Dict[str, Any]:
    """List views in a workbook using MCP server - convenience function"""
    client = MCPClient(mcp_server_url)
    return client.list_views(workbook_luid)


def list_mcp_dashboards(mcp_server_url: str, workbook_luid: str) -> Dict[str, Any]:
    """List dashboards in a workbook using MCP server - convenience function"""
    client = MCPClient(mcp_server_url)
    return client.list_dashboards(workbook_luid)
