#langchain and langgraph package imports
from langchain_openai import ChatOpenAI
from langchain.agents import initialize_agent, AgentType
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langgraph.prebuilt import create_react_agent

#langchain_tableau imports
from langchain_tableau.tools.simple_datasource_qa import initialize_simple_datasource_qa

from community.langchain_community.utilities.tableau.utils import http_post

import os
import jwt
from datetime import datetime, timedelta, timezone
from uuid import uuid4
import requests
from dotenv import load_dotenv
load_dotenv()

tableau_server = os.getenv('TABLEAU_CLD_DOMAIN')
tableau_site = os.getenv('CLD_SITE_NAME')
tableau_jwt_client_id = os.getenv('TABLEAU_CLD_JWT_CLIENT_ID') #a JWT client ID (obtained through Tableau's admin UI)
tableau_jwt_secret_id = os.getenv('TABLEAU_CLD_JWT_SECRET_ID') #a JWT secret ID (obtained through Tableau's admin UI)
tableau_jwt_secret = os.getenv('TABLEAU_CLD_JWT_SECRET') #a JWT secret ID (obtained through Tableau's admin UI)
tableau_api_version = os.getenv('TABLEAU_CLD_API') 
tableau_user = os.getenv('TABLEAU_CLD_USER') 

print(tableau_site)
print(tableau_api_version)

# For this cookbook we are connecting to the Superstore dataset that comes by default with every Tableau server
datasource_luid = os.getenv('TABLEAU_CLD_SUPERSTORE_LUID') #the target data source for this Tool
access_scopes = [
            "tableau:content:read", # for quering Tableau Metadata API
            "tableau:viz_data_service:read" # for querying VizQL Data Service
        ]

# Encode the payload and secret key to generate the JWT
token = jwt.encode(
    {
    "iss": tableau_jwt_client_id,
    "exp": datetime.now(timezone.utc) + timedelta(minutes=5),
    "jti": str(uuid4()),
    "aud": "tableau",
    "sub": tableau_user,
    "scp": access_scopes
    },
    tableau_jwt_secret,
    algorithm = "HS256",
    headers = {
    'kid': tableau_jwt_secret_id,
    'iss': tableau_jwt_client_id
    }
)

# authentication endpoint + request headers & payload
endpoint = f"{tableau_server}/api/{tableau_api_version}/auth/signin"

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

print(endpoint)
print(payload)

response = requests.post(endpoint, headers=headers, json=payload)

# Check if the request was successful (status code 200)
if response.status_code == 200:
    print(response.json())
else:
    error_message = (
        f"Failed to authenticate to the Tableau site. "
        f"Status code: {response.status_code}. Response: {response.text}"
        f"Tried Endpoint: {endpoint}."
        f"Payload: {payload}."
    )
    print(RuntimeError(error_message))


print('Done')


