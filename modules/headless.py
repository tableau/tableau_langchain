import os, requests, json, pandas as pd

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
        # Print the response data
        #print("Response Data:")
        #print(response.json())
        data = response.json()['data']
        # Create a pandas DataFrame from the JSON data
        df = pd.DataFrame(data)

        # Display the first few rows of the DataFrame
        #print("Table view of data from the public REST API:")
        #print(df.head())
        #print(df.all())
        return df
        #display(df.head())
    else:
        print("Failed to fetch data from the API. Status code:", response.status_code)
        print(response.text)
