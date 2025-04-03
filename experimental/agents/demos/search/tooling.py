import os
from dotenv import load_dotenv
from typing import Dict, Any, Optional

from langchain_core.tools import ToolException, Tool

from experimental.agents.tools import tableau_metrics, tavily_tool
from experimental.agents.shared_state import get_datasource_luid

# from experimental.tools.datasource_qa import initialize_datasource_qa
from experimental.tools.datasource_qa import initialize_datasource_qa
from experimental.tools.search_datasource import initialize_datasource_search, initialize_datasource_switch

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
datasource_luid = get_datasource_luid()
tooling_llm_model = os.environ['TOOLING_MODEL']

# Function to create the datasource QA tool with a specific LUID
def create_datasource_qa_tool(luid: str):
    """Create a datasource QA tool with the specified datasource LUID"""
    return initialize_datasource_qa(
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

# Initial creation of the datasource QA tool
analyze_datasource = create_datasource_qa_tool(datasource_luid)

datasource_search = initialize_datasource_search()

datasource_switch = initialize_datasource_switch()

# List of tools used to build the state graph and for binding them to nodes
# tools = [tableau_metrics, analyze_datasource, datasource_search, switch_datasource]
tools = [analyze_datasource, datasource_search, datasource_switch]