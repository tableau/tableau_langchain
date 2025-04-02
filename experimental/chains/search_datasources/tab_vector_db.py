from typing import Optional
from pydantic import BaseModel, Field

from langchain.prompts import PromptTemplate
from langchain_core.tools import tool, ToolException
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import SystemMessage

from langchain_openai import ChatOpenAI

from langchain_tableau.tools.prompts import vds_prompt, vds_response
from langchain_tableau.utilities.auth import jwt_connected_app
from langchain_tableau.utilities.simple_datasource_qa import (
    env_vars_simple_datasource_qa,
    augment_datasource_metadata,
    get_headlessbi_data,
    prepare_prompt_inputs
)

from dotenv import load_dotenv
import os


# if arguments are not provided, the tool obtains environment variables directly from .env
env_vars = env_vars_simple_datasource_qa(
    domain=domain,
    site=site,
    jwt_client_id=jwt_client_id,
    jwt_secret_id=jwt_secret_id,
    jwt_secret=jwt_secret,
    tableau_api_version=tableau_api_version,
    tableau_user=tableau_user,
    datasource_luid=datasource_luid,
    tooling_llm_model=tooling_llm_model
)

access_scopes = [
            "tableau:content:read", # for quering Tableau Metadata API
            "tableau:viz_data_service:read" # for querying VizQL Data Service
        ]

tableau_session = jwt_connected_app(
    tableau_domain=env_vars["domain"],
    tableau_site=env_vars["site"],
    jwt_client_id=env_vars["jwt_client_id"],
    jwt_secret_id=env_vars["jwt_secret_id"],
    jwt_secret=env_vars["jwt_secret"],
    tableau_api=env_vars["tableau_api_version"],
    tableau_user=env_vars["tableau_user"],
    scopes=access_scopes
)


# jwt_connected_app(
#     tableau_domain = 'https://' + os.getenv('TABLEAU_DOMAIN'),
#     tableau_site = os.getenv('SITE_NAME'),
#     tableau_api = os.getenv('TABLEAU_API'),
#     tableau_user = os.getenv('TABLEAU_USER'),
#     jwt_client_id = os.getenv('TABLEAU_JWT_CLIENT_ID'),
#     jwt_secret_id = os.getenv('TABLEAU_JWT_SECRET_ID'),
#     jwt_secret = os.getenv('TABLEAU_JWT_SECRET'),
#     scopes = access_scopes
# )

