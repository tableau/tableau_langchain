import os
from dotenv import load_dotenv
from typing import Dict, Any, Optional

from langchain_tableau.tools.simple_datasource_qa import initialize_simple_datasource_qa
from langchain_core.tools import ToolException, Tool

from experimental.agents.tools import tableau_metrics, tavily_tool
from experimental.tools.datasource_qa import initialize_datasource_qa

from experimental.tools.search_datasource import initialize_datasource_search

from experimental.utilities.metadata import get_data_dictionary

# Load environment variables before accessing them
load_dotenv()
tableau_domain = os.environ['TABLEAU_DOMAIN']
tableau_site = os.environ['TABLEAU_SITE']
tableau_jwt_client_id = os.environ['TABLEAU_JWT_CLIENT_ID']
tableau_jwt_secret_id = os.environ['TABLEAU_JWT_SECRET_ID']
tableau_jwt_secret = os.environ['TABLEAU_JWT_SECRET']
tableau_api_version = os.environ['TABLEAU_API_VERSION']
tableau_user = os.environ['TABLEAU_USER']
datasource_luid = os.environ['DATASOURCE_LUID']
tooling_llm_model = os.environ['TOOLING_MODEL']

# Global variable to track the current datasource LUID
current_datasource_luid = datasource_luid

# Function to create the datasource QA tool with a specific LUID
def create_datasource_qa_tool(luid: str):
    """Create a datasource QA tool with the specified datasource LUID"""
    return initialize_simple_datasource_qa(
        domain=tableau_domain,
        site=tableau_site,
        jwt_client_id=tableau_jwt_client_id,
        jwt_secret_id=tableau_jwt_secret_id,
        jwt_secret=tableau_jwt_secret,
        tableau_api_version=tableau_api_version,
        tableau_user=tableau_user,
        datasource_luid=luid,
        tooling_llm_model=tooling_llm_model
    )

# Initial creation of the datasource QA tool with default LUID
analyze_datasource = create_datasource_qa_tool(datasource_luid)

datasource_search = initialize_datasource_search()


# Create a new tool for switching the datasource
def switch_datasource_tool(luid: str) -> str:
    global analyze_datasource, current_datasource_luid, tools  # ensure tools is imported/accessible

    if not luid or luid.strip() == "":
        raise ToolException("No datasource LUID provided")
    
    try:
        # Create authentication token
        auth_token = {
            "jwt_client_id": tableau_jwt_client_id,
            "jwt_secret_id": tableau_jwt_secret_id,
            "jwt_secret": tableau_jwt_secret,
            "tableau_domain": tableau_domain,
            "tableau_site": tableau_site,
            "tableau_user": tableau_user,
            "tableau_api": tableau_api_version,
            "scopes": ["tableau:content:read", "tableau:viz_data_service:read"]
        }
        
        # Get metadata about the datasource (to validate the LUID)
        metadata = get_data_dictionary(api_key=auth_token, domain=tableau_domain, datasource_luid=luid)
        metadata = metadata['publishedDatasources'][0]
        
        # Create a new datasource QA tool instance with the new LUID
        new_tool = create_datasource_qa_tool(luid)
        current_datasource_luid = luid
        
        # Update the global pointer for analyze_datasource
        analyze_datasource = new_tool
        
        # Optionally, update the tools list if it's mutable so the agent will use the new tool instance.
        for idx, t in enumerate(tools):
            if t.name == "datasource_qa":  
                tools[idx] = new_tool
                break

        datasource_name = metadata.get("name", "Unknown")
        return f"Successfully switched to datasource: '{datasource_name}' (ID: {luid})"
    
    except Exception as e:
        raise ToolException(f"Failed to switch datasource: {str(e)}")

# Create the tool for datasource switching
switch_datasource = Tool(
    name="switch_datasource",
    description="Switch to a different Tableau datasource using its LUID (ID). Use this tool when you've found a more relevant datasource through the datasource_search tool and want to query it instead.",
    func=switch_datasource_tool
)

# List of tools used to build the state graph and for binding them to nodes
# tools = [tableau_metrics, analyze_datasource, datasource_search, switch_datasource]
tools = [datasource_search, switch_datasource]