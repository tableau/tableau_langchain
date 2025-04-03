import os
from dotenv import load_dotenv

from langchain_tableau.tools.simple_datasource_qa import initialize_simple_datasource_qa

from experimental.agents.tools import tableau_metrics, tavily_tool

# Load environment variables before accessing them
load_dotenv()
tableau_domain = os.environ['KEYNOTE_DOMAIN']
tableau_site = os.environ['KEYNOTE_SITE']
tableau_jwt_client_id = os.environ['KEYNOTE_JWT_CLIENT_ID']
tableau_jwt_secret_id = os.environ['KEYNOTE_JWT_SECRET_ID']
tableau_jwt_secret = os.environ['KEYNOTE_JWT_SECRET']
tableau_api_version = os.environ['KEYNOTE_API_VERSION']
tableau_user = os.environ['KEYNOTE_USER']
datasource_luid = os.environ['KEYNOTE_DATASOURCE_LUID']
tooling_llm_model = os.environ['TOOLING_MODEL']


# Tableau VizQL Data Service Query Tool
analyze_datasource = initialize_simple_datasource_qa(
    domain=tableau_domain,
    site=tableau_site,
    jwt_client_id=tableau_jwt_client_id,
    jwt_secret_id=tableau_jwt_secret_id,
    jwt_secret=tableau_jwt_secret,
    tableau_api_version=tableau_api_version,
    tableau_user=tableau_user,
    datasource_luid=datasource_luid,
    tooling_llm_model=tooling_llm_model
)

# Web Search tool
# web_search = tavily_tool()

# List of tools used to build the state graph and for binding them to nodes
tools = [ analyze_datasource ]
