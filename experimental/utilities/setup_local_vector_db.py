import os
from dotenv import load_dotenv
import jwt
from datetime import datetime, timedelta, timezone
from uuid import uuid4
import requests

# Import helper functions from existing modules
from experimental.utilities.auth import jwt_connected_app
from experimental.utilities.metadata import get_datasources_metadata
from experimental.utilities.search_datasources import (
    format_datasources_for_rag,
    create_datasources_vector_db,
    query_datasources_vector_db
)

# Load environment variables (Tableau creds, OpenAI API key, etc.)
load_dotenv()

# Read Tableau authentication config from environment
tableau_server   = os.getenv('TABLEAU_DOMAIN')   
tableau_site     = os.getenv('SITE_NAME')        
tableau_user     = os.getenv('TABLEAU_USER')     

# Credentials for generating auth token via connnected app
tableau_jwt_client_id    = os.getenv('TABLEAU_JWT_CLIENT_ID')
tableau_jwt_secret_id    = os.getenv('TABLEAU_JWT_SECRET_ID')
tableau_jwt_secret = os.getenv('TABLEAU_JWT_SECRET')
tableau_api_version  = os.getenv('TABLEAU_API_VERSION') 

DEFAULT_COLLECTION_NAME = f"{tableau_site}_tableau_datasource_vector_search"

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


def build_tableau_vector_db(debug: bool = False) -> None:
    """
    Authenticate with Tableau and build (or rebuild) the local 'datasources' vector database.
    This fetches all Tableau datasources, formats them for RAG, and stores them in a ChromaDB collection.
    """

    access_scopes = [
        "tableau:content:read",
        "tableau:viz_data_service:read"
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
    published_list = datasources_metadata.get('publishedDatasources', [])

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

# If executed as a script, run the build process.
if __name__ == "__main__":
    # Optionally, set debug mode via an environment variable or directly here.
    debug_mode = os.getenv('DEBUG', 'False').lower() in ('true', '1', 'yes')
    build_tableau_vector_db(debug=debug_mode)

