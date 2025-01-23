import json
import re
from typing import Dict, Any, List
import requests
import jwt
from datetime import datetime, timedelta, timezone
from uuid import uuid4

def query_vds(api_key: str, datasource_luid: str, url: str, query: Dict[str, Any]) -> Dict[str, Any]:
    full_url = f"{url}/api/v1/vizql-data-service/query-datasource"

    payload = {
        "datasource": {
            "datasourceLuid": datasource_luid
        },
        "query": query
    }

    headers = {
        'X-Tableau-Auth': api_key,
        'Content-Type': 'application/json'
    }

    response = requests.post(full_url, headers=headers, json=payload)

    if response.status_code == 200:
        return response.json()
    else:
        error_message = (
            f"Failed to query data source via Tableau VizQL Data Service. "
            f"Status code: {response.status_code}. Response: {response.text}"
        )
        raise RuntimeError(error_message)

def get_headlessbi_data(payload: str, url: str, api_key: str, datasource_luid: str):
    agent_response = get_payload(payload)
    vds_payload = agent_response["payload"]
    query_plan = agent_response["query_plan"]

    if vds_payload:
        headlessbi_data = query_vds(
            api_key=api_key,
            datasource_luid=datasource_luid,
            url=url,
            query=vds_payload
        )

        markdown_table = json_to_markdown(headlessbi_data['data'])

        return {
            "query_plan": query_plan,
            "data": markdown_table
        }
    else:
        return {
            "query_plan": query_plan,
            "data": None
        }

def get_payload(output):
    query_plan = output.split('JSON_payload')[0]
    parsed_output = output.split('JSON_payload')[1]

    match = re.search(r'{.*}', parsed_output, re.DOTALL)
    if match:
        json_string = match.group(0)
        payload = json.loads(json_string)

        return {
            "query_plan": query_plan,
            "payload": payload
        }
    else:
        return {
            "query_plan": query_plan
        }

def json_to_markdown(json_data):
    if isinstance(json_data, str):
        json_data = json.loads(json_data)

    if not isinstance(json_data, list) or not json_data:
        return "Invalid JSON data"

    headers = json_data[0].keys()

    markdown_table = "| " + " | ".join(headers) + " |\n"
    markdown_table += "| " + " | ".join(['---'] * len(headers)) + " |\n"

    for entry in json_data:
        row = "| " + " | ".join(str(entry[header]) for header in headers) + " |"
        markdown_table += row + "\n"

    return markdown_table

def query_vds_metadata(api_key: str, datasource_luid: str, url: str) -> Dict[str, Any]:
    full_url = f"{url}/api/v1/vizql-data-service/read-metadata"

    payload = {
        "datasource": {
            "datasourceLuid": datasource_luid
        }
    }

    headers = {
        'X-Tableau-Auth': api_key,
        'Content-Type': 'application/json'
    }

    response = requests.post(full_url, headers=headers, json=payload)

    if response.status_code == 200:
        return response.json()
    else:
        error_message = (
            f"Failed to obtain data source metadata from VizQL Data Service. "
            f"Status code: {response.status_code}. Response: {response.text}"
        )
        raise RuntimeError(error_message)

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

def augment_datasource_metadata(api_key: str, url: str, datasource_luid: str, prompt: Dict[str, str]):
    datasource_metadata = query_vds_metadata(
        api_key=api_key,
        url=url,
        datasource_luid=datasource_luid
    )

    for field in datasource_metadata['data']:
        del field['fieldName']
        del field['logicalTableId']

        if field['dataType'] == 'STRING':
            string_values = get_values(
                api_key=api_key,
                url=url,
                datasource_luid=datasource_luid,
                caption=field['fieldCaption']
            )
            field['sampleValues'] = string_values

    prompt['data_model'] = datasource_metadata

    return json.dumps(prompt)

def authenticate_tableau_user(
        tableau_domain: str,
        tableau_site: str,
        tableau_api: str,
        tableau_user: str,
        jwt_client_id: str,
        jwt_secret_id: str,
        jwt_secret: str,
        scopes: List[str],
) -> Dict[str, Any]:
    """
    Authenticates a user to Tableau using JSON Web Token (JWT) authentication.

    This function generates a JWT based on the provided credentials and uses it to authenticate
    a user with the Tableau Server or Tableau Online. The JWT is created with a specified expiration
    time and scopes, allowing for secure access to Tableau resources.

    Args:
        tableau_domain (str): The domain of the Tableau Server or Tableau Online instance.
        tableau_site (str): The content URL of the specific Tableau site to authenticate against.
        tableau_api (str): The version of the Tableau API to use for authentication.
        tableau_user (str): The username of the Tableau user to authenticate.
        jwt_client_id (str): The client ID used for generating the JWT.
        jwt_secret_id (str): The key ID associated with the JWT secret.
        jwt_secret (str): The secret key used to sign the JWT.
        scopes (List[str]): A list of scopes that define the permissions granted by the JWT.

    Returns:
        Dict[str, Any]: A dictionary containing the response from the Tableau authentication endpoint,
        typically including an API key or session that is valid for 2 hours and user information.
    """
    # Encode the payload and secret key to generate the JWT
    token = jwt.encode(
        {
        "iss": jwt_client_id,
        "exp": datetime.now(timezone.utc) + timedelta(minutes=5),
        "jti": str(uuid4()),
        "aud": "tableau",
        "sub": tableau_user,
        "scp": scopes
        },
        jwt_secret,
        algorithm = "HS256",
        headers = {
        'kid': jwt_secret_id,
        'iss': jwt_client_id
        }
    )

    # authentication endpoint + request headers & payload
    endpoint = f"{tableau_domain}/api/{tableau_api}/auth/signin"

    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }

    payload = {
        "credentials": {
        "jwt": token,
        "site": {
            "contentUrl": tableau_site,
        }
        }
    }

    response = requests.post(endpoint, headers=headers, json=payload)

    # Check if the request was successful (status code 200)
    if response.status_code == 200:
        return response.json()
    else:
        error_message = (
            f"Failed to authenticate to the Tableau site. "
            f"Status code: {response.status_code}. Response: {response.text}"
        )
        raise RuntimeError(error_message)
