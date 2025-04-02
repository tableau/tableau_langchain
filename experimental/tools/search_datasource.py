from typing import Any, Dict
import os
from dotenv import load_dotenv
from pydantic import BaseModel, Field

from langchain_core.tools import tool, ToolException
from experimental.utilities.search_datasources import (
    query_datasources_vector_db,
    create_datasources_vector_db,
    format_datasources_for_rag
)
from experimental.utilities.metadata import get_datasources_metadata
from experimental.utilities.auth import jwt_connected_app

class DataSourceSearchInputs(BaseModel):
    query: str = Field(
        ...,
        description="The search query to find relevant Tableau data sources."
    )

def initialize_datasource_search():
    """
    Initializes the Langgraph tool for searching alternate Tableau data sources.
    
    Returns:
        A decorated function that can be used as a langgraph tool.
    """
    @tool("datasource_search", args_schema=DataSourceSearchInputs)
    def datasource_search(query: str) -> str:
        """Vector search for Tableau data sources based on the provided query."""
        # Load environment variables (for Tableau and vector search configuration)
        load_dotenv()
        site_name = os.getenv('SITE_NAME', 'tableau')
        collection_name = f"{site_name}_tableau_datasource_vector_search"
        
        # Perform a vector search on datasource metadata
        results: Dict[str, Any] = query_datasources_vector_db(
            query_text=query,
            collection_name=collection_name,
            n_results=3,
            debug=False
        )
        
        # If no vector index exists, create it and re-run the query
        if results is None:
            try:
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
                all_datasources = get_datasources_metadata(
                    api_key=auth_token,
                    domain=os.getenv('TABLEAU_DOMAIN')
                )
                formatted_docs = format_datasources_for_rag(all_datasources)
                create_datasources_vector_db(
                    datasources=formatted_docs,
                    collection_name=collection_name
                )
                results = query_datasources_vector_db(
                    query_text=query,
                    collection_name=collection_name,
                    n_results=3
                )
            except Exception as e:
                raise ToolException(f"Error during dataset search: {str(e)}")
        
        if not results or not results.get('luid'):
            return "No alternative dataset was found for the given query."

        # Process the top search results
        top_ids = results.get('luid', [])
        top_meta = results.get('metadatas', [])
        best_id = top_ids[0] if top_ids else None
        best_metadata = top_meta[0] if top_meta else {}
        best_name = best_metadata.get('name', 'Unknown Data Source')
        best_desc = best_metadata.get('description', None)
        
        output_msg = f"Suggested alternate dataset: '{best_name}' (ID: {best_id})."
        if best_desc:
            snippet = best_desc.strip()
            if len(snippet) > 150:
                snippet = snippet[:150].rstrip() + "..."
            output_msg += f" Description: {snippet}"
        if len(top_ids) > 1:
            second_name = top_meta[1].get('name', 'Unnamed Data Source')
            output_msg += f" Another possible match is '{second_name}'."
        return output_msg

    return datasource_search
