import os, requests, json

def get_data(query_url, datasource_luid, auth_secret, query):
    url = query_url
    payload = json.dumps({
        "datasource": {
            "datasourceLuid": datasource_luid
    },
        "query": query
    })

    headers = {
    'X-Tableau-Auth': auth_secret,
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