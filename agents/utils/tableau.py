import jwt
from datetime import datetime, timedelta, timezone
from uuid import uuid4

from agents.utils.other import http_post


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
        "scp": kwargs['scopes']
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
