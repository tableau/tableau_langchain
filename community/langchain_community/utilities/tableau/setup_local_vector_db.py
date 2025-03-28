import os
from dotenv import load_dotenv

# Import helper functions from existing modules
from community.langchain_community.utilities.tableau.auth import jwt_connected_app
from community.langchain_community.utilities.tableau.metadata import get_datasources_metadata
from community.langchain_community.utilities.tableau.search_datasources import (
    format_datasources_for_rag,
    create_datasources_vector_db,
    query_datasources_vector_db
)

# Default collection name for the vector database
DEFAULT_COLLECTION_NAME = "datasources"

# Load environment variables (Tableau creds, OpenAI API key, etc.)
load_dotenv()

# Read Tableau authentication config from environment
tableau_server   = os.getenv('TABLEAU_DOMAIN')   
tableau_site     = os.getenv('SITE_NAME')        
tableau_user     = os.getenv('TABLEAU_USER')     

# Credentials for generating auth token via connnected app
tableau_client_id    = os.getenv('TABLEAU_JWT_CLIENT_ID')
tableau_secret_id    = os.getenv('TABLEAU_JWT_SECRET_ID')
tableau_secret_value = os.getenv('TABLEAU_JWT_SECRET')
tableau_api_version  = os.getenv('TABLEAU_API_VERSION') 

DEFAULT_COLLECTION_NAME = f"{tableau_site}_vector_store"

def build_tableau_vector_db(debug: bool = False) -> None:
    """
    Authenticate with Tableau and build (or rebuild) the local 'datasources' vector database.
    This fetches all Tableau datasources, formats them for RAG, and stores them in a ChromaDB collection.
    """

    access_scopes = [
        "tableau:content:read",
        "tableau:viz_data_service:read"
    ]


    # Generate Tableau API auth token using the provided credentials
    auth_token = jwt_connected_app(
        jwt_client_id   = tableau_client_id,
        jwt_secret_id   = tableau_secret_id,
        jwt_secret      = tableau_secret_value,
        tableau_domain  = tableau_server,
        tableau_site    = tableau_site,
        tableau_user    = tableau_user,
        tableau_api     = tableau_api_version,
        scopes          = access_scopes
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

