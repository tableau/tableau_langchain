import re
import json
from typing import Optional

from langchain.prompts import PromptTemplate
from langchain_core.tools import tool, ToolException

from langchain_tableau.tools.prompts import vds_query, vds_prompt_data
from langchain_tableau.utilities.auth import jwt_connected_app
from langchain_tableau.utilities.models import select_model
from langchain_tableau.utilities.simple_datasource_qa import (
    env_vars_simple_datasource_qa,
    augment_datasource_metadata,
    get_headlessbi_data,
)

def _extract_json_payload(raw_output: str) -> str:
    """Extracts the JSON payload from the model's raw output."""
    match = re.search(r"<json_payload>(.*?)</json_payload>", raw_output, re.DOTALL)
    if match:
        return match.group(1).strip()

    # Fallback for models that ignore the tags
    json_match = re.search(r"^\s*\{.*\}\s*$", raw_output, re.DOTALL)
    if json_match:
        return json_match.group(0).strip()

    raise ToolException(f"Tool Error: The query-writing model failed to return a valid JSON payload. Output: {raw_output}")


def initialize_simple_datasource_qa(
    domain: Optional[str] = None,
    site: Optional[str] = None,
    jwt_client_id: Optional[str] = None,
    jwt_secret_id: Optional[str] = None,
    jwt_secret: Optional[str] = None,
    tableau_api_version: Optional[str] = None,
    tableau_user: Optional[str] = None,
    datasource_luid: Optional[str] = None,
    model_provider: Optional[str] = None,
    tooling_llm_model: Optional[str] = None
):
    """
    Initializes a robust, self-correcting tool for querying a Tableau Data Source.
    """
    env_vars = env_vars_simple_datasource_qa(
        domain=domain, site=site, jwt_client_id=jwt_client_id, jwt_secret_id=jwt_secret_id,
        jwt_secret=jwt_secret, tableau_api_version=tableau_api_version, tableau_user=tableau_user,
        datasource_luid=datasource_luid, model_provider=model_provider, tooling_llm_model=tooling_llm_model
    )

    @tool
    def simple_datasource_qa(user_input: str) -> str:
        """
        You are an AI Analyst. When you need to answer a question about data, use this tool.
        Provide the full, natural language question from the user.
        For example: 'What were the total sales for each region last quarter?'
        The tool will return a markdown table with the data.
        """
        # Session scopes
        access_scopes = ["tableau:content:read", "tableau:viz_data_service:read"]
        try:
            tableau_session = jwt_connected_app(
                tableau_domain=env_vars["domain"], tableau_site=env_vars["site"],
                jwt_client_id=env_vars["jwt_client_id"], jwt_secret_id=env_vars["jwt_secret_id"],
                jwt_secret=env_vars["jwt_secret"], tableau_api=env_vars["tableau_api_version"],
                tableau_user=env_vars["tableau_user"], scopes=access_scopes
            )
            tableau_auth = tableau_session['credentials']['token']
        except Exception as e:
            raise ToolException(f"CRITICAL ERROR: Could not authenticate to the Tableau site successfully. Error: {e}")

        # Models and Prompts
        query_writer = select_model(
            provider=env_vars["model_provider"], model_name=env_vars["tooling_llm_model"], temperature=0
        )
        query_writing_prompt = PromptTemplate(
            input_variables=[
                "task", "vds_schema", "sample_queries", "error_queries", "data_dictionary",
                "data_model", "previous_call_error", "previous_vds_payload"
            ],
            template=vds_query
        )
        query_writing_chain = query_writing_prompt | query_writer

        # Internal Retry Loop
        max_retries = 2
        last_error = None
        last_payload = None

        for attempt in range(max_retries):
            try:
                # 1. Prepare prompt with context (and errors from previous attempt)
                query_writing_data = augment_datasource_metadata(
                    task=user_input, api_key=tableau_auth, url=env_vars["domain"],
                    datasource_luid=env_vars["datasource_luid"], prompt=vds_prompt_data,
                    previous_errors=str(last_error) if last_error else None,
                    previous_vds_payload=last_payload
                )

                # 2. Generate the JSON query
                vds_query_result = query_writing_chain.invoke(query_writing_data)
                vds_payload = _extract_json_payload(vds_query_result.content)
                last_payload = vds_payload # Store for potential next attempt

                # Check for model-generated error message
                payload_dict = json.loads(vds_payload)
                if 'error' in payload_dict:
                    return f"Could not complete the request. Reason: {payload_dict['error']}"

                # 3. Execute the query
                data_table = get_headlessbi_data(
                    api_key=tableau_auth, url=env_vars["domain"],
                    datasource_luid=env_vars["datasource_luid"], payload=vds_payload
                )
                return data_table # Success! Exit the loop and return the data.

            except Exception as e:
                # Failure. Store error and loop again.
                last_error = e
                # On the final attempt, raise the error to the agent
                if attempt == max_retries - 1:
                    raise ToolException(f"The tool failed to query the data source after {max_retries} attempts. Last error: {e}")

        return "Tool failed to retrieve data after multiple attempts." # Should not be reached

    return simple_datasource_qa
