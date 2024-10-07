import os, requests, json

# define the headless BI query template
def query(query):
    url = os.getenv('VDS_URL')
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
        print("here is the JSON output I've generated and will send to VDS: " + data)
        return data
    else:
        print("Failed to fetch data from the API. Status code:", response.status_code)
        print(response.text)
