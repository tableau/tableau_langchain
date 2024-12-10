import os, jwt, json
import aiohttp
from datetime import datetime, timedelta, timezone

from uuid import uuid4

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
async def authenticate():
    # Encode the payload and secret key to generate the JWT
    token = jwt.encode(
        {
        "iss": os.environ['TABLEAU_JWT_CLIENT_ID'],
        "exp": datetime.now(timezone.utc) + timedelta(minutes=5),
        "jti": str(uuid4()),
        "aud": "tableau",
        "sub": os.environ['TABLEAU_USER'],
        "scp": [
            "tableau:content:read",
            "tableau:insights:read",
            "tableau:insight_definitions_metrics:read",
            "tableau:insight_metrics:read",
            "tableau:metric_subscriptions:read",
        ]
        },
        os.environ['TABLEAU_REST_JWT_SECRET'],
        algorithm = "HS256",
        headers = {
        'kid': os.environ['TABLEAU_REST_JWT_SECRET_ID'],
        'iss': os.environ['TABLEAU_JWT_CLIENT_ID']
        }
    )

    # authentication endpoint + request headers & payload
    endpoint = f"{os.environ['TABLEAU_DOMAIN']}/api/{os.environ['TABLEAU_API']}/auth/signin"

    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }

    payload = {
        "credentials": {
        "jwt": token,
        "site": {
            "contentUrl": os.environ['TABLEAU_SITE'],
        }
        }
    }

    response = await http_post(endpoint=endpoint, headers=headers, payload=payload)
    return response['body']
