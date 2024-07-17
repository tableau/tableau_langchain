
import os, requests, json

# request metadata of declared datasource (READ_METADATA)
def read():
    url = os.getenv('READ_METADATA')
    payload = json.dumps({
        "connection": {
            "tableauServerName": os.getenv('TABLEAU_DOMAIN'),
            "siteId": os.getenv('SITE_NAME'),
            "datasource": os.getenv('DATA_SOURCE')
        },
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
