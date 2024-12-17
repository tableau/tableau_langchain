import jwt, json, aiohttp, os, getpass

from datetime import datetime, timedelta, timezone

from uuid import uuid4


def _set_env(var: str):
    """
    if environment variable not set, safely prompts user for value returns the newly resolved variable
    """
    if not os.environ.get(var):
        os.environ[var] = getpass.getpass(f"{var}: ")

# reusable asynchronous HTTP GET requests
async def http_get(endpoint, headers):
    async with aiohttp.ClientSession() as session:
        async with session.get(endpoint, headers=headers) as response:
            responseHeaders = dict(response.headers)
            responseBody = await response.json()

            responseObject = {
                "headers": responseHeaders,
                "body": responseBody
            }
            return responseObject

# reusable asynchronous HTTP POST requests
async def http_post(endpoint, headers, payload):
    formattedPayload = json.dumps(payload)
    async with aiohttp.ClientSession() as session:
        async with session.post(endpoint, headers=headers, data=formattedPayload) as response:
            responseHeaders = dict(response.headers)
            responseBody = await response.json()

            responseObject = {
                "headers": responseHeaders,
                "body": responseBody
            }
            return responseObject

# authenticates user to Tableau
async def authenticate_tableau_user(**kwargs):
    # Encode the payload and secret key to generate the JWT
    token = jwt.encode(
        {
        "iss": kwargs['jwt_client_id'],
        "exp": datetime.now(timezone.utc) + timedelta(minutes=5),
        "jti": str(uuid4()),
        "aud": "tableau",
        "sub": kwargs['tableau_user'],
        "scp": [
            "tableau:content:read", # for quering Tableau Metadata API
            "tableau:insights:read", # for quering Tableau Pulse
            "tableau:insight_definitions_metrics:read", # for quering Tableau Pulse
            "tableau:insight_metrics:read", # for quering Tableau Pulse
            "tableau:metric_subscriptions:read", # for quering Tableau Pulse
            "tableau:viz_data_service:read" # for querying VizQL Data Service
        ]
        },
        kwargs['jwt_secret'],
        algorithm = "HS256",
        headers = {
        'kid': kwargs['jwt_secret_id'],
        'iss': kwargs['jwt_client_id']
        }
    )

    # authentication endpoint + request headers & payload
    endpoint = f"{kwargs['tableau_domain']}/api/{kwargs['tableau_api']}/auth/signin"

    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }

    payload = {
        "credentials": {
        "jwt": token,
        "site": {
            "contentUrl": kwargs['tableau_site'],
        }
        }
    }

    response = await http_post(endpoint=endpoint, headers=headers, payload=payload)
    return response['body']
