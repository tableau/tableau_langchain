# #langchain and langgraph package imports
# from langchain_openai import ChatOpenAI
# from langchain.agents import initialize_agent, AgentType
# from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
# from langgraph.prebuilt import create_react_agent
# from langchain_tableau.utilities.auth import jwt_connected_app

# #langchain_tableau imports
# from langchain_tableau.tools.simple_datasource_qa import initialize_simple_datasource_qa

# from community.langchain_community.utilities.tableau.utils import http_post

# import os
# import jwt
# from datetime import datetime, timedelta, timezone
# from uuid import uuid4
# import requests
# from dotenv import load_dotenv
# load_dotenv()

# tableau_server = os.getenv('TABLEAU_CLD_DOMAIN')
# tableau_site = os.getenv('CLD_SITE_NAME')
# tableau_jwt_client_id = os.getenv('TABLEAU_CLD_JWT_CLIENT_ID') #a JWT client ID (obtained through Tableau's admin UI)
# tableau_jwt_secret_id = os.getenv('TABLEAU_CLD_JWT_SECRET_ID') #a JWT secret ID (obtained through Tableau's admin UI)
# tableau_jwt_secret = os.getenv('TABLEAU_CLD_JWT_SECRET') #a JWT secret ID (obtained through Tableau's admin UI)
# tableau_api_version = os.getenv('TABLEAU_CLD_API') 
# tableau_user = os.getenv('TABLEAU_CLD_USER') 

# print(tableau_site)
# print(tableau_api_version)

# # For this cookbook we are connecting to the Superstore dataset that comes by default with every Tableau server
# datasource_luid = os.getenv('TABLEAU_CLD_SUPERSTORE_LUID') #the target data source for this Tool
# access_scopes = [
#             "tableau:content:read", # for quering Tableau Metadata API
#             "tableau:viz_data_service:read" # for querying VizQL Data Service
#         ]

# # Encode the payload and secret key to generate the JWT
# token = jwt.encode(
#     {
#     "iss": tableau_jwt_client_id,
#     "exp": datetime.now(timezone.utc) + timedelta(minutes=5),
#     "jti": str(uuid4()),
#     "aud": "tableau",
#     "sub": tableau_user,
#     "scp": access_scopes
#     },
#     tableau_jwt_secret,
#     algorithm = "HS256",
#     headers = {
#     'kid': tableau_jwt_secret_id,
#     'iss': tableau_jwt_client_id
#     }
# )

# # authentication endpoint + request headers & payload
# endpoint = f"{tableau_server}/api/{tableau_api_version}/auth/signin"

# headers = {
#     'Content-Type': 'application/json',
#     'Accept': 'application/json'
# }

# payload = {
#     "credentials": {
#     "jwt": token,
#     "site": {
#         "contentUrl": tableau_site,
#     }
#     }
# }

# print(endpoint)
# print(payload)

# response = requests.post(endpoint, headers=headers, json=payload)

# # Check if the request was successful (status code 200)
# if response.status_code == 200:
#     print(response.json())
# else:
#     error_message = (
#         f"Failed to authenticate to the Tableau site. "
#         f"Status code: {response.status_code}. Response: {response.text}"
#         f"Tried Endpoint: {endpoint}."
#         f"Payload: {payload}."
#     )
#     print(RuntimeError(error_message))


# print('Done')


# tableau_auth = jwt_connected_app(
#         jwt_client_id=os.environ['TABLEAU_JWT_CLIENT_ID'],
#         jwt_secret_id=os.environ['TABLEAU_JWT_SECRET_ID'],
#         jwt_secret=os.environ['TABLEAU_JWT_SECRET'],
#         tableau_api=os.environ['TABLEAU_API_VERSION'],
#         tableau_user=os.environ['TABLEAU_USER'],
#         tableau_domain=tableau_server,
#         tableau_site=tableau_site,
#         scopes=access_scopes
#     )

# tableau_session = tableau_auth['credentials']['token']
# print(tableau_session)
# print('Done')

###############################

# Claude script

import os
import jwt
from datetime import datetime, timedelta, timezone
from uuid import uuid4
import requests
import json
import pandas as pd

def generate_tableau_auth_token(
    jwt_client_id, 
    jwt_secret_id, 
    jwt_secret, 
    tableau_server, 
    tableau_site, 
    tableau_user,
    tableau_api_version='3.20'
):
    """
    Generate a Tableau authentication token
    
    :return: Authentication token (X-Tableau-Auth)
    """
    # Generate JWT for initial authentication
    access_scopes = [
        "tableau:content:read",
        "tableau:viz_data_service:read"
    ]
    
    jwt_token = jwt.encode(
        {
            "iss": jwt_client_id,
            "exp": datetime.now(timezone.utc) + timedelta(minutes=5),
            "jti": str(uuid4()),
            "aud": "tableau",
            "sub": tableau_user,
            "scp": access_scopes
        },
        jwt_secret,
        algorithm="HS256",
        headers={
            'kid': jwt_secret_id,
            'iss': jwt_client_id
        }
    )
    
    # Authenticate and get X-Tableau-Auth token
    endpoint = f"{tableau_server}/api/{tableau_api_version}/auth/signin"
    
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }
    
    payload = {
        "credentials": {
            "jwt": jwt_token,
            "site": {
                "contentUrl": tableau_site,
            }
        }
    }
    
    try:
        response = requests.post(endpoint, headers=headers, json=payload)
        response.raise_for_status()
        
        # Extract the authentication token
        return response.json()['credentials']['token']
    
    except requests.RequestException as e:
        print(f"Authentication error: {e}")
        print(f"Response content: {response.text}")
        raise

def get_datasources_metadata(
    domain, 
    auth_token
):
    """
    Query Tableau Metadata API for all datasources
    
    :param domain: Tableau server domain
    :param auth_token: X-Tableau-Auth token
    :return: Datasources metadata
    """
    full_url = f"{domain}/api/metadata/graphql"
    
    query = """
    query Datasources {
      publishedDatasources {
        name
        description
        luid
        isCertified
        owner {
          username
          name
          email
        }
        hasActiveWarning
        extractLastRefreshTime
        extractLastIncrementalUpdateTime
        extractLastUpdateTime
        fields {
          name
          description
        }
        projectName
      }
    }
    """
    
    payload = json.dumps({
        "query": query,
        "variables": {}
    })
    
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'X-Tableau-Auth': auth_token
    }
    
    try:
        response = requests.post(full_url, headers=headers, data=payload)
        response.raise_for_status()
        
        return response.json()
    
    except requests.RequestException as e:
        print(f"Error querying Metadata API: {e}")
        print(f"Response content: {response.text}")
        raise

def flatten_datasources(datasources_data):
    """
    Flatten datasources structure into a list of dictionaries
    
    :param datasources_data: Raw GraphQL response data
    :return: List of flattened datasource dictionaries
    """
    if not datasources_data or not isinstance(datasources_data, dict):
        raise ValueError("Invalid datasources data provided.")
    
    flattened_datasources = []
    
    # Extract publishedDatasources from the response
    published_datasources = datasources_data.get('data', {}).get('publishedDatasources', [])
    
    for datasource in published_datasources:
        # Flatten fields
        fields = datasource.get('fields', [])
        fields_str = '\n'.join([f"{f['name']}: {f.get('description', 'No description')}" for f in fields])
        
        # Flatten owner information
        owner = datasource.get('owner', {})
        
        datasource_dict = {
            'name': datasource.get('name'),
            'luid': datasource.get('luid'),
            'description': datasource.get('description', 'No description'),
            'is_certified': datasource.get('isCertified'),
            'project_name': datasource.get('projectName'),
            
            # Owner details
            'owner_username': owner.get('username'),
            'owner_name': owner.get('name'),
            'owner_email': owner.get('email'),
            
            # Extract times
            'last_refresh_time': datasource.get('extractLastRefreshTime'),
            'last_incremental_update_time': datasource.get('extractLastIncrementalUpdateTime'),
            'last_update_time': datasource.get('extractLastUpdateTime'),
            
            # Warning status
            'has_active_warning': datasource.get('hasActiveWarning'),
            
            # Fields
            'fields': fields_str
        }
        
        flattened_datasources.append(datasource_dict)
    
    return flattened_datasources

def format_datasources_for_rag(datasources_data):
    """
    Format Tableau datasources for RAG (Retrieval-Augmented Generation) purposes
    
    :param datasources_data: Raw GraphQL response data
    :return: List of formatted datasource dictionaries
    """
    if not datasources_data or not isinstance(datasources_data, dict):
        raise ValueError("Invalid datasources data provided.")
    
    formatted_datasources = []
    
    # Extract publishedDatasources from the response
    published_datasources = datasources_data.get('data', {}).get('publishedDatasources', [])
    
    for datasource in published_datasources:

        datasource_name = datasource.get('name')
        if not datasource_name:
            continue
        
        # Process fields for RAG
        fields = datasource.get('fields', [])
        field_entries = []
        
        for field in fields:
            # Skip hidden fields (assuming we want visible fields only)
            if not field.get('isHidden', False):
                name = field.get('name', '')
                description = field.get('description', '')
                
                # Format field entry with description if available
                if description:
                    # Remove newlines and extra spaces
                    description = ' '.join(description.split())
                    field_entry = f"- {name}: [{description}]"
                else:
                    field_entry = f"- {name}"
                
                field_entries.append(field_entry)
        
        # Combine field entries
        concatenated_field_entries = '\n'.join(field_entries)
        
        # Create dashboard overview for RAG
        dashboard_overview = f"""Datasource: {datasource.get('name', 'Unnamed Datasource')}
{datasource.get('description', 'No description available')}
Project: {datasource.get('projectName', 'No project specified')}

Datasource Columns:
{concatenated_field_entries}"""
        
        # Prepare keys to extract
        keys_to_extract = [
            'id',
            'luid',
            'uri',
            'vizportalId',
            'vizportalUrlId',
            'name',
            'hasExtracts',
            'createdAt',
            'updatedAt',
            'extractLastUpdateTime',
            'extractLastRefreshTime',
            'extractLastIncrementalUpdateTime',
            'projectName',
            'containerName',
            'isCertified',
            'description'
        ]
        
        # Create formatted datasource dictionary
        formatted_datasource = {
            'dashboard_overview': dashboard_overview,
            **{key: datasource.get(key) for key in keys_to_extract}
        }
        
        # Add owner information
        owner = datasource.get('owner', {})
        formatted_datasource.update({
            'owner_username': owner.get('username'),
            'owner_name': owner.get('name'),
            'owner_email': owner.get('email')
        })
        
        formatted_datasources.append(formatted_datasource)
    
    return formatted_datasources

def main():
    # Tableau configuration from environment variables
    tableau_server = os.getenv('TABLEAU_CLD_DOMAIN')
    tableau_site = os.getenv('CLD_SITE_NAME')
    tableau_jwt_client_id = os.getenv('TABLEAU_CLD_JWT_CLIENT_ID')
    tableau_jwt_secret_id = os.getenv('TABLEAU_CLD_JWT_SECRET_ID')
    tableau_jwt_secret = os.getenv('TABLEAU_CLD_JWT_SECRET')
    tableau_api_version = os.getenv('TABLEAU_CLD_API') 
    tableau_user = os.getenv('TABLEAU_CLD_USER') 

    try:
        # Generate authentication token
        auth_token = generate_tableau_auth_token(
            jwt_client_id=tableau_jwt_client_id,
            jwt_secret_id=tableau_jwt_secret_id,
            jwt_secret=tableau_jwt_secret,
            tableau_server=tableau_server,
            tableau_site=tableau_site,
            tableau_user=tableau_user,
            tableau_api_version=tableau_api_version
        )
        
        # Retrieve datasources metadata
        datasources_metadata = get_datasources_metadata(
            domain=tableau_server,
            auth_token=auth_token
        )
        
        # Format datasources for RAG
        formatted_datasources = format_datasources_for_rag(datasources_metadata)
        
        # Convert to DataFrame
        datasources_df = pd.DataFrame(formatted_datasources)
        
        # Display the table
        print("\nTableau Datasources (RAG Format):")
        print(datasources_df[['name', 'dashboard_overview']])
        
        # Optional: Save to CSV
        csv_filename = 'tableau_datasources_rag.csv'
        datasources_df.to_csv(csv_filename, index=False)
        print(f"\nDatasources saved to {csv_filename}")
        
        return datasources_df

    except Exception as e:
        print(f"Error in Metadata API retrieval: {e}")
        return None

if __name__ == '__main__':
    main()