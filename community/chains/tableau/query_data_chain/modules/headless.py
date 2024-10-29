import os, requests, json, re, pandas as pd

# define the headless BI query template
def query(query):
    url = os.getenv('HEADLESSBI_URL')
    payload = json.dumps({
        "connection": {
            "tableauServerName": os.getenv('TABLEAU_DOMAIN'),
            "siteId": os.getenv('SITE_NAME'),
            "datasource": os.getenv('DATA_SOURCE')
        },
        "query": query
    })

    headers = {
    'Credential-Key': os.getenv('PAT_NAME'),
    'Credential-value': os.getenv('PAT_SECRET'),
    'Content-Type': 'application/json'
    }
    response = requests.request("POST", url, headers=headers, data=payload)

    # Check if the request was successful (status code 200)
    if response.status_code == 200:
        data = response.json()['data']
        return data
    else:
        print("Failed to fetch data from the API. Status code:", response.status_code)
        print(response.text)



def get_data(message):
    payload = get_payload(message)
    headlessbi_data = query(payload)

    # Convert to JSON string
    markdown_table = json_to_markdown(headlessbi_data)

    return markdown_table


def get_payload(output):
    content = output.content
    # output reasoning
    print(content.split('JSON_payload')[0])
    # parse LLM output and query headless BI
    parsed_output = content.split('JSON_payload')[1]

    print('*** parsed_output ***', parsed_output)

    match = re.search(r'{.*}', parsed_output, re.DOTALL)
    if match:
        json_string = match.group(0)
        payload = json.loads(json_string)
        return payload


def json_to_markdown(json_data):
    # Parse the JSON data if it's a string
    if isinstance(json_data, str):
        json_data = json.loads(json_data)

    # Check if the JSON data is a list and not empty
    if not isinstance(json_data, list) or not json_data:
        return "Invalid JSON data"

    # Extract headers from the first dictionary
    headers = json_data[0].keys()

    # Create the Markdown table header
    markdown_table = "| " + " | ".join(headers) + " |\n"
    markdown_table += "| " + " | ".join(['---'] * len(headers)) + " |\n"

    # Add each row to the Markdown table
    for entry in json_data:
        row = "| " + " | ".join(str(entry[header]) for header in headers) + " |"
        markdown_table += row + "\n"

    return markdown_table
