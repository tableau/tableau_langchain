import os
from typing import Any, Dict
from dotenv import load_dotenv
from langchain_core.tools import ToolDefinition

# Import necessary functions from the Tableau utilities
from community.langchain_community.utilities.tableau.search_datasources import (
    query_datasources_vector_db,
    create_datasources_vector_db,
    format_datasources_for_rag
)
from community.langchain_community.utilities.tableau.metadata import get_datasources_metadata
from community.langchain_community.utilities.tableau.auth import jwt_connected_app

# Define tool name and description for the agent
_TOOL_NAME: str = "datasource_search"
_TOOL_DESCRIPTION: str = (
    "Search for alternate Tableau data sources (datasets) relevant to the user's query. "
    "Use this if the current dataset may not contain the information needed."
)

def invoke(query: str) -> str:
    """
    Invoke the dataset search tool to find relevant Tableau datasources for the given query.
    Returns a description of the most relevant datasource(s) found, or a message if none found.
    """
    # Load environment variables (for OpenAI API key and Tableau credentials)
    load_dotenv()
    # Default collection name for the vector store (uses SITE_NAME if available)
    site_name = os.getenv('SITE_NAME', 'tableau')
    collection_name = f"{site_name}_tableau_datasource_vector_search"

    # Perform a vector search on datasource metadata for the query
    results: Dict[str, Any] = query_datasources_vector_db(
        query_text=query, 
        collection_name=collection_name, 
        n_results=3, 
        debug=False
    )
    # If no vector index exists yet (results is None), build it and query again
    if results is None:
        try:
            # Authenticate to Tableau and retrieve all datasource metadata
            # Generate an auth token via the connected app (JWT) credentials
            auth_token = jwt_connected_app(
                jwt_client_id=os.getenv('TABLEAU_JWT_CLIENT_ID'),
                jwt_secret_id=os.getenv('TABLEAU_JWT_SECRET_ID'),
                jwt_secret=os.getenv('TABLEAU_JWT_SECRET'),
                tableau_domain=os.getenv('TABLEAU_DOMAIN'),
                tableau_site=os.getenv('SITE_NAME'),
                tableau_user=os.getenv('TABLEAU_USER'),
                tableau_api=os.getenv('TABLEAU_API_VERSION', '3.20'),
                scopes=["tableau:content:read", "tableau:viz_data_service:read"]
            )
            # Fetch all published datasources metadata via Tableau Metadata API
            all_datasources = get_datasources_metadata(api_key=auth_token, domain=os.getenv('TABLEAU_DOMAIN'))
            # Format the raw metadata into documents suitable for retrieval (RAG format)
            formatted_docs = format_datasources_for_rag(all_datasources)
            # Create a persistent ChromaDB collection with these documents (rebuilding any existing one)
            create_datasources_vector_db(datasources=formatted_docs, collection_name=collection_name)
            # Now perform the search query again on the newly built vector database
            results = query_datasources_vector_db(query_text=query, collection_name=collection_name, n_results=3)
        except Exception as e:
            # Return an error message if authentication or data fetching fails
            return f"Error during dataset search: {str(e)}"

    # If still no results or no relevant dataset found
    if not results or not results.get('luid'):
        return "No alternative dataset was found for the given query."

    # Process the top search result(s)
    top_ids = results.get('luid', [])
    top_meta = results.get('metadatas', [])
    # Take the best match (first result)
    best_id = top_ids[0] if top_ids else None
    best_metadata = top_meta[0] if top_meta else {}
    best_name = best_metadata.get('name', 'Unknown Data Source')
    best_desc = best_metadata.get('description', None)

    # Prepare an output message describing the top dataset and optionally a second one
    output_msg = f"Suggested alternate dataset: '{best_name}' (ID: {best_id})."
    if best_desc:
        # Include a short description snippet if available
        snippet = best_desc.strip()
        if len(snippet) > 150:
            snippet = snippet[:150].rstrip() + "..."
        output_msg += f" Description: {snippet}"
    # Optionally mention the second-best match
    if len(top_ids) > 1:
        second_name = top_meta[1].get('name', 'Unnamed Data Source')
        output_msg += f" Another possible match is '{second_name}'."

    return output_msg

# Define the tool for integration with the agent
TOOL_DEFINITION = ToolDefinition(
    name=_TOOL_NAME,
    description=_TOOL_DESCRIPTION,
    invoke=invoke
)
