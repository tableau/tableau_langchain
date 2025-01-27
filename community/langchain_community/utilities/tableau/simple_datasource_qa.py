import json
import re
from typing import Dict, Optional
import logging

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
