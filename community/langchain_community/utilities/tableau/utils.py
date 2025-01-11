from typing import Dict, List, Any, Optional
import json
import aiohttp
import jwt
from datetime import datetime, timedelta, timezone
from uuid import uuid4


async def http_get(endpoint: str, headers: Optional[Dict[str, str]] = None) -> aiohttp.ClientResponse:
    """
    reusable asynchronous HTTP GET requests

    Args:
        endpoint (str): The URL to send the GET request to
        headers (Optional[Dict[str, str]]): Optional headers to include in the request

    Returns:
        Dict[str, Any]: A dictionary containing the response headers and body
    """
    async with aiohttp.ClientSession() as session:
        async with session.get(endpoint, headers=headers) as response:
            return response


async def http_post(endpoint: str, headers: Optional[Dict[str, str]] = None, payload: Dict[str, Any] = None) -> aiohttp.ClientResponse:
    """
    reusable asynchronous HTTP POST requests

    Args:
        endpoint (str): The URL to send the POST request to
        headers (Optional[Dict[str, str]]): Optional headers to include in the request
        payload (Optional[Dict[str, Any]]): The data to send in the body of the request

    Returns:
        Dict[str, Any]: A dictionary containing the response headers and body
    """
    async with aiohttp.ClientSession() as session:
        async with session.post(endpoint, headers=headers, json=payload) as response:
            response_data = await response.json()  # For JSON response
            return response


async def authenticate_tableau_user(
        tableau_domain: str,
        tableau_site: str,
        tableau_api: str,
        tableau_user: str,
        jwt_client_id: str,
        jwt_secret_id: str,
        jwt_secret: str,
        scopes: List[str],
) -> Dict[str, Any]:
    """
    Authenticates a user to Tableau using JSON Web Token (JWT) authentication.

    This function generates a JWT based on the provided credentials and uses it to authenticate
    a user with the Tableau Server or Tableau Online. The JWT is created with a specified expiration
    time and scopes, allowing for secure access to Tableau resources.

    Args:
        tableau_domain (str): The domain of the Tableau Server or Tableau Online instance.
        tableau_site (str): The content URL of the specific Tableau site to authenticate against.
        tableau_api (str): The version of the Tableau API to use for authentication.
        tableau_user (str): The username of the Tableau user to authenticate.
        jwt_client_id (str): The client ID used for generating the JWT.
        jwt_secret_id (str): The key ID associated with the JWT secret.
        jwt_secret (str): The secret key used to sign the JWT.
        scopes (List[str]): A list of scopes that define the permissions granted by the JWT.

    Returns:
        Dict[str, Any]: A dictionary containing the response from the Tableau authentication endpoint,
        typically including an API key or session that is valid for 2 hours and user information.
    """
    # Encode the payload and secret key to generate the JWT
    token = jwt.encode(
        {
        "iss": jwt_client_id,
        "exp": datetime.now(timezone.utc) + timedelta(minutes=5),
        "jti": str(uuid4()),
        "aud": "tableau",
        "sub": tableau_user,
        "scp": scopes
        },
        jwt_secret,
        algorithm = "HS256",
        headers = {
        'kid': jwt_secret_id,
        'iss': jwt_client_id
        }
    )

    # authentication endpoint + request headers & payload
    endpoint = f"{tableau_domain}/api/{tableau_api}/auth/signin"

    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }

    payload = {
        "credentials": {
        "jwt": token,
        "site": {
            "contentUrl": tableau_site,
        }
        }
    }

    response = await http_post(endpoint=endpoint, headers=headers, payload=payload)
    return response['body']
