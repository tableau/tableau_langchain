import os
from dotenv import load_dotenv

# importing from latest local
from experimental.tools.simple_datasource_qa import initialize_simple_datasource_qa
from langchain_core.tools import tool
from typing import Optional
from experimental.utilities.vizql_data_service import list_datasources

# importing from remote `pkg`
# from langchain_tableau.tools.simple_datasource_qa import initialize_simple_datasource_qa


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


# Tableau VizQL Data Service Query Tool (MCP-only)
analyze_datasource = initialize_simple_datasource_qa(
    domain=tableau_domain,
    site=tableau_site,
    jwt_client_id=tableau_jwt_client_id,
    jwt_secret_id=tableau_jwt_secret_id,
    jwt_secret=tableau_jwt_secret,
    tableau_api_version=tableau_api_version,
    tableau_user=tableau_user,
    datasource_luid=None,
    tooling_llm_model=tooling_llm_model
)

@tool("list_tableau_datasources")
def list_tableau_datasources(filter: Optional[str] = None) -> str:
    """List published Tableau datasources available on the configured site. Optional query filter."""
    mcp_url = os.getenv('TABLEAU_MCP_URL', 'https://tableau-mcp-bierschenk-2df05b623f7a.herokuapp.com/tableau-mcp')
    try:
        results = list_datasources(url=mcp_url, filter=filter)
        if not isinstance(results, list) or not results:
            return "No datasources found."
        lines = []
        for ds in results[:50]:
            if isinstance(ds, dict):
                name = ds.get('name') or ds.get('contentUrl') or 'Unnamed'
                luid = ds.get('id') or ''
                proj = (ds.get('project') or {}).get('name') if isinstance(ds.get('project'), dict) else None
                line = f"- {name} ({luid})" + (f" • project: {proj}" if proj else '')
                lines.append(line)
        return "\n".join(lines) if lines else "No datasources found."
    except Exception as e:
        return f"Error listing datasources via MCP: {e}"

tools = [ analyze_datasource, list_tableau_datasources ]
