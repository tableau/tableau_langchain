import os
from dotenv import load_dotenv
import jwt
from datetime import datetime, timedelta, timezone
from uuid import uuid4
import requests
import json

# Import helper functions from existing modules
from experimental.utilities.search_datasources import (
    create_datasources_vector_db,
    query_datasources_vector_db
)

# Load environment variables (Tableau creds, OpenAI API key, etc.)
load_dotenv()

# Read Tableau authentication config from environment
tableau_server   = 'https://' + os.getenv('TABLEAU_SRV_DOMAIN')   
tableau_site     = os.getenv('SRV_SITE_NAME')        
tableau_user     = os.getenv('TABLEAU_SRV_USER')     

# Credentials for generating auth token via connnected app
tableau_jwt_client_id    = os.getenv('TABLEAU_SRV_JWT_CLIENT_ID')
tableau_jwt_secret_id    = os.getenv('TABLEAU_SRV_JWT_SECRET_ID')
tableau_jwt_secret = os.getenv('TABLEAU_SRV_JWT_SECRET')
tableau_api_version  = os.getenv('TABLEAU_SRV_API') 

DEFAULT_COLLECTION_NAME = f"{tableau_site}_tableau_datasource_vector_search"
debug = False

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
    # access_scopes = [
    #     "tableau:content:read",
    #     "tableau:viz_data_service:read"
    # ]

    access_scopes = [
        "tableau:content:read"
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

print('login attempt')

auth_token = generate_tableau_auth_token(
            jwt_client_id=tableau_jwt_client_id,
            jwt_secret_id=tableau_jwt_secret_id,
            jwt_secret=tableau_jwt_secret,
            tableau_server=tableau_server,
            tableau_site=tableau_site,
            tableau_user=tableau_user,
            tableau_api_version=tableau_api_version
        )
print('login success')
# Retrieve all published datasource metadata via Tableau Metadata API

def get_datasources_query():
    """
    Generate GraphQL query for retrieving published datasources metadata.
    
    :return: GraphQL query string
    """
    query = """
    query Datasources {
	    tableauSites(filter: { name: "Demonstration" }) {
        publishedDatasources {
            name
            description
            luid
            isCertified
            vizportalUrlId
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
}
    """
    return query

def get_datasources_metadata(api_key: str, domain: str):
    """
    Synchronously query Tableau Metadata API for all datasources
    
    :param api_key: X-Tableau-Auth token
    :param domain: Tableau server domain
    :return: Datasources metadata dictionary
    """
    full_url = f"{domain}/api/metadata/graphql"

    query = get_datasources_query()

    payload = json.dumps({
        "query": query,
        "variables": {}
    })

    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'X-Tableau-Auth': api_key
    }

    response = requests.post(full_url, headers=headers, data=payload)
    response.raise_for_status()  # Raise an exception for bad status codes

    dictionary = response.json()

    return dictionary['data']

def format_datasources_for_rag(datasources_data, debug: bool = False):
    """
    Format Tableau datasources for RAG (Retrieval-Augmented Generation) purposes
    
    :param datasources_data: Raw GraphQL response data from get_datasources_metadata
    :param debug: Enable debug logging
    :return: List of formatted datasource dictionaries optimized for RAG search
    """
    if not datasources_data or not isinstance(datasources_data, dict):
        raise ValueError("Invalid datasources data provided.")
    
    formatted_datasources = []
    
    # Extract publishedDatasources from the response
    # published_datasources = datasources_data.get('publishedDatasources', [])
    published_datasources = datasources_data.get('tableauSites', [])
    published_datasources = published_datasources[0]
    published_datasources = published_datasources['publishedDatasources']
    
    if debug:
        print(f"Total datasources to process: {len(published_datasources)}")
    
    for datasource in published_datasources:
        # Skip datasources without a name
        datasource_name = datasource.get('name')
        if not datasource_name:
            continue
        
        # Process fields for RAG
        fields = datasource.get('fields', [])
        field_entries = []
        
        for field in fields:
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
        dashboard_overview = f"""Datasource: {datasource_name}
{datasource.get('description', 'No description available')}
Project: {datasource.get('projectName', 'No project specified')}

Datasource Columns:
{concatenated_field_entries}"""
        
        # Prepare formatted datasource dictionary
        formatted_datasource = {
            'dashboard_overview': dashboard_overview,
            'name': datasource_name,
            'luid': datasource.get('luid'),
            'url' : tableau_server + '/#/site/' + tableau_site + '/datasources/'+ datasource.get('vizportalUrlId') + '/connections',
            'description': datasource.get('description', 'No description'),
            'project_name': datasource.get('projectName'),
            'is_certified': datasource.get('isCertified'),
            'last_refresh_time': datasource.get('extractLastRefreshTime'),
            'last_incremental_update_time': datasource.get('extractLastIncrementalUpdateTime'),
            'last_update_time': datasource.get('extractLastUpdateTime'),
            'has_active_warning': datasource.get('hasActiveWarning'),
        }
        
        # Add owner information
        owner = datasource.get('owner', {})
        formatted_datasource.update({
            'owner_username': owner.get('username'),
            'owner_name': owner.get('name'),
            'owner_email': owner.get('email')
        })
        
        formatted_datasources.append(formatted_datasource)
    
    if debug:
        print(f"Processed {len(formatted_datasources)} datasources for RAG")
    
    return formatted_datasources


def build_tableau_vector_db(debug: bool = False) -> None:
    """
    Authenticate with Tableau and build (or rebuild) the local 'datasources' vector database.
    This fetches all Tableau datasources, formats them for RAG, and stores them in a ChromaDB collection.
    """

    # access_scopes = [
    #     "tableau:content:read",
    #     "tableau:viz_data_service:read"
    # ]

    access_scopes = [
        "tableau:content:read"
    ]

    auth_token = generate_tableau_auth_token(
            jwt_client_id=tableau_jwt_client_id,
            jwt_secret_id=tableau_jwt_secret_id,
            jwt_secret=tableau_jwt_secret,
            tableau_server=tableau_server,
            tableau_site=tableau_site,
            tableau_user=tableau_user,
            tableau_api_version=tableau_api_version
        )

    # Retrieve all published datasource metadata via Tableau Metadata API
    datasources_metadata = get_datasources_metadata(domain=tableau_server, api_key=auth_token)
    
    # The returned metadata is a dict, expected to have a 'publishedDatasources' list
    # published_list = datasources_metadata.get('publishedDatasources', [])
    published_list = datasources_metadata.get('tableauSites', [])
    published_list = published_list[0]
    published_list = published_list['publishedDatasources']

    # Format the raw metadata for RAG use (create text overviews for each datasource)
    formatted_datasources = format_datasources_for_rag(datasources_metadata, debug=debug)

    # Create or rebuild the ChromaDB collection with the formatted datasource documents
    vector_collection = create_datasources_vector_db(
        datasources=formatted_datasources,
        debug=debug,
        collection_name=DEFAULT_COLLECTION_NAME
    )

def query_tableau_vector_db(query_text: str, collection_name: str,n_results: int = 3, debug: bool = False):
    """
    Query the local 'datasources' vector database for a given text query.
    If the vector database does not exist, it will be built first.
    Returns the query results (list of matching datasource IDs and metadata).
    """
    load_dotenv()

    # Attempt to query the existing vector database
    results = query_datasources_vector_db(
        query_text     = query_text,
        collection_name= collection_name,
        n_results      = n_results,
        debug          = debug
    )
    # If no collection was found (results is None), build the database and try again
    if results is None:
        build_tableau_vector_db(debug=debug)
        results = query_datasources_vector_db(
            query_text     = query_text,
            collection_name= collection_name,
            n_results      = n_results,
            debug          = debug
        )
    # `results` is expected to be a dictionary with keys like 'luid', 'documents', 'distances', 'metadatas'
    if results is None:
        return None

    # For convenience, print out the top results in a readable format if debug is enabled
    if debug and isinstance(results, dict):
        top_ids       = results.get('luid', [])
        top_documents = results.get('documents', [])
        top_scores    = results.get('distances', [])
        top_metadatas = results.get('metadatas', [])

        for idx, ds_id in enumerate(top_ids, start=1):
            ds_name = top_metadatas[idx-1].get('name', 'Unknown')
            score   = top_scores[idx-1]
            excerpt = top_documents[idx-1][:200].replace('\n', ' ') + "..."
    return results


def get_databoards_query():
    """
    Generate GraphQL query for retrieving published datasources metadata.
    
    :return: GraphQL query string
    """
    query = """
        query dashboards{ 
        tableauSites(filter: { name: "Demonstration" }) {
            workbooks {
                dashboards {
                luid
                name
                path
                createdAt
                updatedAt
                }
            }
        }
    }
    """
    return query

def get_dashboards_metadata(api_key: str, domain: str):
    """
    Synchronously query Tableau Metadata API for all datasources
    
    :param api_key: X-Tableau-Auth token
    :param domain: Tableau server domain
    :return: Datasources metadata dictionary
    """
    full_url = f"{domain}/api/metadata/graphql"

    query = get_databoards_query()

    payload = json.dumps({
        "query": query,
        "variables": {}
    })

    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'X-Tableau-Auth': api_key
    }

    response = requests.post(full_url, headers=headers, data=payload)
    response.raise_for_status()  # Raise an exception for bad status codes

    dictionary = response.json()

    return dictionary['data']

def format_dashboards_for_rag(dashboards_data, debug: bool = False):
    """
    Format Tableau dashboards for RAG (Retrieval-Augmented Generation) purposes
    
    :param dashboards_data: Raw GraphQL response data from get_dashboards_metadata
    :param debug: Enable debug logging
    :return: List of formatted datasource dictionaries optimized for RAG search
    """
    if not dashboards_data or not isinstance(dashboards_data, dict):
        raise ValueError("Invalid dashboards data provided.")
    
    formatted_dashboards = []
    
    # Extract publishedDatasources from the response
    # published_dashboards = dashboards_data.get('publishedDatasources', [])
    published_dashboards = dashboards_data.get('dashboards', [])
    
    if debug:
        print(f"Total dashboards to process: {len(published_dashboards)}")
    
    for dashboard in published_dashboards:
        # Skip dashboards without a name
        dashboard_name = dashboard.get('name')
        if not dashboard_name:
            continue
        
        # Prepare formatted dashboard dictionary
        formatted_dashboard = {
            'name': dashboard_name,
            'luid': dashboard.get('luid'),
            'path': dashboard.get('path'),
            'created_at': dashboard.get('createdAt'),
            'updated_at': dashboard.get('updatedAt')
        }
        
        formatted_dashboards.append(formatted_dashboard)
    
    if debug:
        print(f"Processed {len(formatted_dashboards)} dashboards for RAG")
    
    return formatted_dashboards