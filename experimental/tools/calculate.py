from typing import Optional, Any
import json
import re
from pydantic import BaseModel, Field

from langchain.prompts import PromptTemplate
from langchain.schema import AIMessage
from langchain_core.tools import tool, ToolException

from experimental.utilities.auth import jwt_connected_app
from experimental.utilities.models import select_model
from experimental.tools.calc_prompt import (
    calcs_prompt_data,
    CALC_PROMPT
)
from experimental.utilities.datasource_qa import env_vars_datasource_qa, augment_datasource_metadata

# New structured output model
class CalcOutput(BaseModel):
    calc_formula: str = Field(..., description="The raw Tableau calc formula string")
    calc_name: str = Field(..., description="The name for the calculated field")
    user_friendly_explanation: str = Field(
        ..., description="A human-readable explanation of what the calc does"
    )

class tableau_calc_input(BaseModel):
    user_input: str = Field(
        ...,
        description="Describes a tableau calculation in natural language.",
        examples=["an LOD calculation that shows the average sales per customer"],
    )


def initialize_generate_calc_string(
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
    Initializes the Langgraph tool called 'generate_calc_string' for generating calculated fields
    related to a user's question on a target data source. The user question may explcitly ask for a
    calculation string or it may be implicit in the data question.

    Args:
        domain (Optional[str]): The domain of the Tableau server.
        site (Optional[str]): The site name on the Tableau server.
        jwt_client_id (Optional[str]): The client ID for JWT authentication.
        jwt_secret_id (Optional[str]): The secret ID for JWT authentication.
        jwt_secret (Optional[str]): The secret for JWT authentication.
        tableau_api_version (Optional[str]): The version of the Tableau API to use.
        tableau_user (Optional[str]): The Tableau user to authenticate as.
        datasource_luid (Optional[str]): The LUID of the data source to perform QA on.
        tooling_llm_model (Optional[str]): The LLM model to use for tooling operations.

    Returns:
        function: A decorated function that can be used as a langgraph tool for generating tableau calculations.

    The returned function (generate_calc_string) takes the following parameters:
        user_input (str): The user's query or command in natural language.

    It returns a dictionary containing the results of the QA operation.

    Note:
        If arguments are not provided, the function will attempt to read them from
        environment variables, typically stored in a .env file.
    """
    # if arguments are not provided, the tool obtains environment variables directly from .env
    env_vars = env_vars_datasource_qa(
        domain=domain,
        site=site,
        jwt_client_id=jwt_client_id,
        jwt_secret_id=jwt_secret_id,
        jwt_secret=jwt_secret,
        tableau_api_version=tableau_api_version,
        tableau_user=tableau_user,
        datasource_luid=datasource_luid,
        model_provider=model_provider,
        tooling_llm_model=tooling_llm_model
    )

    @tool("generate_calc_string", args_schema=tableau_calc_input)
    def generate_calc_string(
        user_input: str,
        previous_call_error: Optional[str] = None,
        previous_vds_payload: Optional[str] = None
    ) -> Any:
        """
        Generates a Tableau calculation string based on the user's or system's input. This tool should only be used in
        2 scenarios:
        1. When the user is explicitly asking for a Tableau calculation string to be generated.
        2. When a data question requies that a derived field be created in order to answer the question. For example,
        if the user asks about profit margin, but the profit margin field does not exist in the data source, use this tool
        to generate a calculation string for profit margin then pass it in the query datasource tool.

        This tool is not intended to be used in Tableau authoring. Instead the output will be returend to the user or the
        calc string will be passed to the query datasource tool to be executed as part of a semantic query.

        If you received an error after using this tool, mention it in your next attempt to help the tool correct itself.
        """
        # Session scopes are limited to only required authorizations to Tableau resources that support tool operations
        try:
            tableau_session = jwt_connected_app(
                tableau_domain=env_vars["domain"],
                tableau_site=env_vars["site"],
                jwt_client_id=env_vars["jwt_client_id"],
                jwt_secret_id=env_vars["jwt_secret_id"],
                jwt_secret=env_vars["jwt_secret"],
                tableau_api=env_vars["tableau_api_version"],
                tableau_user=env_vars["tableau_user"],
                scopes=["tableau:content:read"]
            )
        except Exception as e:
            raise ToolException(f"Authentication failed: {e}")

        tableau_auth = tableau_session['credentials']['token']
        tableau_datasource = env_vars["datasource_luid"]

        # 0. Fetch & augment metadata + inject functions
        prompt_dict = augment_datasource_metadata(
            task=user_input,
            api_key=tableau_auth,
            url=domain,
            datasource_luid=tableau_datasource,
            prompt=calcs_prompt_data,
            previous_errors=previous_call_error,
            previous_vds_payload=previous_vds_payload
        )
        prompt_dict['calc_functions'] = calcs_prompt_data['calc_functions']

        # Build PromptTemplate and chain
        calc_prompt = PromptTemplate(
            input_variables=["task", "calc_functions", "data_dictionary", "data_model"],
            template=CALC_PROMPT
        )
        calc_writer = select_model(
            provider=env_vars["model_provider"],
            model_name=env_vars["tooling_llm_model"],
            temperature=0
        )
        chain = calc_prompt | calc_writer

        # Invoke chain and extract text
        payload = {
            "task": prompt_dict["task"],
            "calc_functions": prompt_dict["calc_functions"],
            "data_dictionary": prompt_dict["data_dictionary"],
            "data_model": prompt_dict["data_model"],
        }
        raw_response = chain.invoke(payload)
        #text = raw_response.content if isinstance(raw_response, AIMessage) else raw_response

        # # Extract JSON block from response
        # json_text = None
        # # try fenced code block
        # fenced = re.search(r"```json\s*(\{.*?\})\s*```", text, re.DOTALL)
        # if fenced:
        #     json_text = fenced.group(1)
        # else:
        #     # fallback to first top-level JSON object
        #     match = re.search(r"(\{.*\})", text, re.DOTALL)
        #     if match:
        #         json_text = match.group(1)

        # if not json_text:
        #     raise ToolException(f"No JSON payload found in LLM response. Response was: {text}")

        # # Parse JSON with error handling
        # try:
        #     parsed = json.loads(json_text)
        # except Exception as e:
        #     raise ToolException(f"Failed to parse JSON from LLM payload: {e}\nPayload was: {json_text}")

        # # Validate and return structured output
        # try:
        #     output = CalcOutput.model_validate(parsed)
        # except Exception as e:
        #     raise ToolException(f"Validation of CalcOutput failed: {e}\nParsed JSON: {parsed}")

        return raw_response

    return generate_calc_string
