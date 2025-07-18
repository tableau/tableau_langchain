import os
from dotenv import load_dotenv

from langchain_tableau.tools.simple_datasource_qa import initialize_simple_datasource_qa

# Load environment variables before accessing them
load_dotenv()
tableau_domain = os.environ['EACANADA_TABLEAU_DOMAIN']
tableau_site = os.environ['EACANADA_TABLEAU_SITE']
tableau_jwt_client_id = os.environ['EACANADA_TABLEAU_JWT_CLIENT_ID']
tableau_jwt_secret_id = os.environ['EACANADA_TABLEAU_JWT_SECRET_ID']
tableau_jwt_secret = os.environ['EACANADA_TABLEAU_JWT_SECRET']
tableau_api_version = os.environ['TABLEAU_API_VERSION']
tableau_user = os.environ['EACANADA_TABLEAU_USER']
datasource_luid = os.environ['OMNICELL_DATASOURCE_LUID']
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

# List of tools used to build the state graph and for binding them to nodes
tools = [ analyze_datasource ]
