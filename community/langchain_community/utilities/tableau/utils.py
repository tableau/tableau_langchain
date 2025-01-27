import os
from typing import Dict, Any, Optional
import aiohttp
import json
from dotenv import load_dotenv


async def http_get(endpoint: str, headers: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
    """
    Reusable asynchronous HTTP GET requests.

    Args:
        endpoint (str): The URL to send the GET request to.
        headers (Optional[Dict[str, str]]): Optional headers to include in the request.

    Returns:
        Dict[str, Any]: A dictionary containing the status code and either the JSON response or response text.
    """
    async with aiohttp.ClientSession() as session:
        async with session.get(endpoint, headers=headers) as response:
            response_data = await response.json() if response.status == 200 else await response.text()
            return {
                'status': response.status,
                'data': response_data
            }


async def http_post(endpoint: str, headers: Optional[Dict[str, str]] = None, payload: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Reusable asynchronous HTTP POST requests.

    Args:
        endpoint (str): The URL to send the POST request to.
        headers (Optional[Dict[str, str]]): Optional headers to include in the request.
        payload (Optional[Dict[str, Any]]): The data to send in the body of the request.

    Returns:
        Dict[str, Any]: A dictionary containing the status code and either the JSON response or response text.
    """
    async with aiohttp.ClientSession() as session:
        async with session.post(endpoint, headers=headers, json=payload) as response:
            response_data = await response.json() if response.status == 200 else await response.text()
            return {
                'status': response.status,
                'data': response_data
            }


def env_vars_simple_datasource_qa(
    domain=None,
    site=None,
    jwt_client_id=None,
    jwt_secret_id=None,
    jwt_secret=None,
    tableau_api_version=None,
    tableau_user=None,
    datasource_luid=None,
    tooling_llm_model=None
):
    """
    Retrieves Tableau configuration from environment variables if not provided as arguments.

    Args:
        domain (str, optional): Tableau domain
        site (str, optional): Tableau site
        jwt_client_id (str, optional): JWT client ID
        jwt_secret_id (str, optional): JWT secret ID
        jwt_secret (str, optional): JWT secret
        tableau_api_version (str, optional): Tableau API version
        tableau_user (str, optional): Tableau user
        datasource_luid (str, optional): Datasource LUID
        tooling_llm_model (str, optional): Tooling LLM model

    Returns:
        dict: A dictionary containing all the configuration values
    """
    # Load environment variables before accessing them
    load_dotenv()

    config = {
        'domain': domain or os.environ.get('TABLEAU_DOMAIN'),
        'site': site or os.environ.get('TABLEAU_SITE'),
        'jwt_client_id': jwt_client_id or os.environ.get('TABLEAU_JWT_CLIENT_ID'),
        'jwt_secret_id': jwt_secret_id or os.environ.get('TABLEAU_JWT_SECRET_ID'),
        'jwt_secret': jwt_secret or os.environ.get('TABLEAU_JWT_SECRET'),
        'tableau_api_version': tableau_api_version or os.environ.get('TABLEAU_API_VERSION'),
        'tableau_user': tableau_user or os.environ.get('TABLEAU_USER'),
        'datasource_luid': datasource_luid or os.environ.get('DATASOURCE_LUID'),
        'tooling_llm_model': tooling_llm_model or os.environ.get('TOOLING_MODEL')
    }

    return config


def json_to_markdown_table(json_data):
    if isinstance(json_data, str):
        json_data = json.loads(json_data)
    # Check if the JSON data is a list and not empty
    if not isinstance(json_data, list) or not json_data:
        raise ValueError(f"Invalid JSON data, you may have an error or if the array is empty then it was not possible to resolve the query your wrote: {json_data}")

    headers = json_data[0].keys()

    markdown_table = "| " + " | ".join(headers) + " |\n"
    markdown_table += "| " + " | ".join(['---'] * len(headers)) + " |\n"

    for entry in json_data:
        row = "| " + " | ".join(str(entry[header]) for header in headers) + " |"
        markdown_table += row + "\n"

    return markdown_table
