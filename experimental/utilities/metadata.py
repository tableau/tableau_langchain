import json
import requests
import os
from typing import Dict
from langchain_tableau.utilities.utils import http_post
from .mcp_client import get_mcp_data_dictionary


def get_datasource_query(luid):
    query = f"""
    query Datasources {{
      publishedDatasources(filter: {{ luid: "{luid}" }}) {{
        name
        description
        owner {{
          name
        }}
        fields {{
          name
          description
          isHidden
        }}
      }}
    }}
    """

    print('query', query)

    return query


async def get_data_dictionary_async(api_key: str, domain: str, datasource_luid: str) -> Dict:
    full_url = f"{domain}/api/metadata/graphql"

    query = get_datasource_query(datasource_luid)

    payload = json.dumps({
        "query": query,
        "variables": {}
    })

    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'X-Tableau-Auth': api_key
    }

    response = await http_post(endpoint=full_url, headers=headers, payload=payload)

    # Check if the request was successful (status code 200)
    if response['status'] == 200:
        return response['data']
    else:
        error_message = (
            f"Failed to query Tableau's Metadata API"
            f"Status code: {response['status']}. Response: {response['data']}"
        )
        raise RuntimeError(error_message)


def get_data_dictionary(api_key: str, domain: str, datasource_luid: str) -> Dict:
    """
    Get data dictionary using MCP server instead of direct Metadata API.
    This function maintains compatibility with existing code while using MCP.
    """
    # Get MCP server URL from environment or use default
    mcp_server_url = os.environ.get('MCP_SERVER_URL', 'https://your-mcp-server.herokuapp.com/tableau-mcp')

    try:
        return get_mcp_data_dictionary(mcp_server_url, datasource_luid)
    except Exception as e:
        # Fallback to original implementation if MCP fails
        print(f"MCP data dictionary failed, falling back to direct API: {e}")
        return get_data_dictionary_fallback(api_key, domain, datasource_luid)


def get_data_dictionary_fallback(api_key: str, domain: str, datasource_luid: str) -> Dict:
    """Fallback method using direct Metadata API if MCP fails"""
    full_url = f"{domain}/api/metadata/graphql"
    query = get_datasource_query(datasource_luid)

    payload = json.dumps({"query": query, "variables": {}})

    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'X-Tableau-Auth': api_key
    }

    response = requests.post(full_url, headers=headers, data=payload)
    response.raise_for_status() # Raise an exception for bad status codes

    data_sources = response.json().get('data', {}).get('publishedDatasources', [])

    if not data_sources:  # Check for empty list
        return {
            'datasource_name': 'data source metadata such as names not available',
            'datasource_description': 'data source metadata such as descriptions not available',
            'datasource_owner': 'data source metadata such as data source owner not available',
            'datasource_fields': 'data source metadata such as field descriptions and comments not available'
        }

    json_data = data_sources[0]  # Safely access first element

    return {
        'datasource_name': json_data.get('name'),
        'datasource_description': json_data.get('description'),
        'datasource_owner': json_data.get('owner').get('name'),
        'datasource_fields': [ field for field in json_data.get('fields', []) if not field.get('isHidden') ]
    }
