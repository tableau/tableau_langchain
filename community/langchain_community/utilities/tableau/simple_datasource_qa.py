import os
import json
import re
import logging
from typing import Dict, Optional
from dotenv import load_dotenv

from community.langchain_community.utilities.tableau.vizql_data_service import query_vds, query_vds_metadata
from community.langchain_community.utilities.tableau.utils import json_to_markdown_table


def get_headlessbi_data(payload: str, url: str, api_key: str, datasource_luid: str):
    json_payload = json.loads(payload)

    try:
        headlessbi_data = query_vds(
            api_key=api_key,
            datasource_luid=datasource_luid,
            url=url,
            query=json_payload
        )

        if not headlessbi_data or 'data' not in headlessbi_data:
            raise ValueError("Invalid or empty response from query_vds")

        markdown_table = json_to_markdown_table(headlessbi_data['data'])
        return markdown_table

    except ValueError as ve:
        logging.error(f"Value error in get_headlessbi_data: {str(ve)}")
        raise

    except json.JSONDecodeError as je:
        logging.error(f"JSON decoding error in get_headlessbi_data: {str(je)}")
        raise ValueError("Invalid JSON format in the payload")

    except Exception as e:
        logging.error(f"Unexpected error in get_headlessbi_data: {str(e)}")
        raise RuntimeError(f"An unexpected error occurred: {str(e)}")


def get_payload(output):
    try:
        parsed_output = output.split('JSON_payload')[1]
    except IndexError:
        raise ValueError("'JSON_payload' not found in the output")

    match = re.search(r'{.*}', parsed_output, re.DOTALL)
    if match:
        json_string = match.group(0)
        try:
            payload = json.loads(json_string)
            return payload
        except json.JSONDecodeError:
            raise ValueError("Invalid JSON format in the payload")
    else:
        raise ValueError("No JSON payload found in the parsed output")


def get_values(api_key: str, url: str, datasource_luid: str, caption: str):
    column_values = {'fields': [{'fieldCaption': caption}]}
    output = query_vds(
        api_key=api_key,
        datasource_luid=datasource_luid,
        url=url,
        query=column_values
    )
    if output is None:
        return None
    sample_values = [list(item.values())[0] for item in output['data']][:4]
    return sample_values


def augment_datasource_metadata(
    api_key: str,
    url: str,
    datasource_luid: str,
    prompt: Dict[str, str],
    previous_errors: Optional[str] = None,
    previous_error_query: Optional[str] = None
):
    datasource_metadata = query_vds_metadata(
        api_key=api_key,
        url=url,
        datasource_luid=datasource_luid
    )

    for field in datasource_metadata['data']:
        del field['fieldName']
        del field['logicalTableId']

    prompt['data_model'] = datasource_metadata

    if previous_errors:
        prompt['previous_call_error'] = previous_errors
    if previous_error_query:
        prompt['previous_error_query'] = previous_error_query

    return json.dumps(prompt)


def prepare_prompt_inputs(data: dict, user_string: str) -> dict:
    """
    Prepare inputs for the prompt template with explicit, safe mapping.

    Args:
        data (dict): Raw data from VizQL query
        user_input (str): Original user query

    Returns:
        dict: Mapped inputs for PromptTemplate
    """
    return {
        "vds_query": data.get('query', ''),
        "data_source": data.get('data_source', ''),
        "data_table": data.get('data_table', ''),
        "user_input": user_string
    }


def env_vars_simple_datasource_qa(
    domain=None,
    site=None,
    jwt_client_id=None,
    jwt_secret_id=None,
    jwt_secret=None,
    tableau_api_version=None,
    tableau_user=None,
    datasource_luid=None,
    tooling_llm_model=None
):
    """
    Retrieves Tableau configuration from environment variables if not provided as arguments.

    Args:
        domain (str, optional): Tableau domain
        site (str, optional): Tableau site
        jwt_client_id (str, optional): JWT client ID
        jwt_secret_id (str, optional): JWT secret ID
        jwt_secret (str, optional): JWT secret
        tableau_api_version (str, optional): Tableau API version
        tableau_user (str, optional): Tableau user
        datasource_luid (str, optional): Datasource LUID
        tooling_llm_model (str, optional): Tooling LLM model

    Returns:
        dict: A dictionary containing all the configuration values
    """
    # Load environment variables before accessing them
    load_dotenv()

    config = {
        'domain': domain if isinstance(domain, str) and domain else os.environ['TABLEAU_DOMAIN'],
        'site': site or os.environ['TABLEAU_SITE'],
        'jwt_client_id': jwt_client_id or os.environ['TABLEAU_JWT_CLIENT_ID'],
        'jwt_secret_id': jwt_secret_id or os.environ['TABLEAU_JWT_SECRET_ID'],
        'jwt_secret': jwt_secret or os.environ['TABLEAU_JWT_SECRET'],
        'tableau_api_version': tableau_api_version or os.environ['TABLEAU_API_VERSION'],
        'tableau_user': tableau_user or os.environ['TABLEAU_USER'],
        'datasource_luid': datasource_luid or os.environ['DATASOURCE_LUID'],
        'tooling_llm_model': tooling_llm_model or os.environ['TOOLING_MODEL']
    }

    return config
