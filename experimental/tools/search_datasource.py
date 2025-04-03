from typing import Any, Dict
import os
from dotenv import load_dotenv
from pydantic import BaseModel, Field

from experimental.agents.shared_state import set_datasource_luid

from langchain_core.tools import tool, ToolException
from experimental.utilities.search_datasources import (
    query_datasources_vector_db,
    create_datasources_vector_db,
    format_datasources_for_rag
)
from experimental.utilities.metadata import get_datasources_metadata, get_data_dictionary
from experimental.utilities.auth import jwt_connected_app
from experimental.tools.datasource_qa import initialize_datasource_qa

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
                    tableau_api=os.getenv('TABLEAU_API_VERSION', '3.21'),
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


# Define the input schema for datasource switching.
class DataSourceSwitchInputs(BaseModel):
    luid: str = Field(
        ...,
        description="The LUID (ID) of the Tableau datasource to switch to."
    )
def initialize_datasource_switch():
    """
    Initializes the Langgraph tool for switching the active Tableau datasource.
    
    Returns:
        A decorated function that can be used as a Langgraph tool.
    """
    @tool("switch_datasource", args_schema=DataSourceSwitchInputs)
    def switch_datasource(luid: str) -> str:
        """Switch to a different Tableau datasource using its LUID."""
        global analyze_datasource, current_datasource_luid
        # Import the tools list from the module where it's defined.
        from experimental.agents.demos.search.tooling import tools as agent_tools

        if not luid or luid.strip() == "":
            raise ToolException("No datasource LUID provided")
        
        load_dotenv()
        try:
            auth_token = jwt_connected_app(
                jwt_client_id=os.getenv('TABLEAU_JWT_CLIENT_ID'),
                jwt_secret_id=os.getenv('TABLEAU_JWT_SECRET_ID'),
                jwt_secret=os.getenv('TABLEAU_JWT_SECRET'),
                tableau_domain=os.getenv('TABLEAU_DOMAIN'),
                tableau_site=os.getenv('SITE_NAME'),
                tableau_user=os.getenv('TABLEAU_USER'),
                tableau_api=os.getenv('TABLEAU_API_VERSION', '3.21'),
                scopes=["tableau:content:read", "tableau:viz_data_service:read"]
            )
            tableau_auth = auth_token['credentials']['token']
            
            metadata = get_data_dictionary(
                api_key=tableau_auth, 
                domain=os.getenv('TABLEAU_DOMAIN'), 
                datasource_luid=luid
            )
            metadata = metadata['publishedDatasources'][0]

            def create_datasource_qa_tool(luid: str):
                return initialize_datasource_qa(
                    domain=os.getenv('TABLEAU_DOMAIN'),
                    site=os.getenv('SITE_NAME'),
                    jwt_client_id=os.getenv('TABLEAU_JWT_CLIENT_ID'),
                    jwt_secret_id=os.getenv('TABLEAU_JWT_SECRET_ID'),
                    jwt_secret=os.getenv('TABLEAU_JWT_SECRET'),
                    tableau_api_version=os.getenv('TABLEAU_API_VERSION', '3.21'),
                    tableau_user=os.getenv('TABLEAU_USER'),
                    datasource_luid=luid,
                    tooling_llm_model=os.getenv('TOOLING_MODEL')
                )
                        
            new_tool = create_datasource_qa_tool(luid)
            current_datasource_luid = luid
            analyze_datasource = new_tool
            
            # Update the global tools list from the tooling module.
            for idx, t in enumerate(agent_tools):
                if t.name == "datasource_qa":
                    agent_tools[idx] = new_tool
                    break

            set_datasource_luid(luid)

            datasource_name = metadata.get("name", "Unknown")
            return f"Successfully switched to datasource: '{datasource_name}' (ID: {luid})"
        
        except Exception as e:
            raise ToolException(f"Failed to switch datasource: {str(e)}")
    
    return switch_datasource
