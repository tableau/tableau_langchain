
import requests
import json

# read in the datasource metadata of the datasource that is listed in vault
def read(env_vars):
    url = env_vars['READ_METADATA']
    payload = json.dumps({
        "connection": {
            "tableauServerName": env_vars['TABLEAU_DOMAIN'],
            "siteId": env_vars['SITE_NAME'],
            "datasource": env_vars['DATA_SOURCE']
        },
    })

    headers = {
    'Credential-Key': env_vars['PAT_NAME'],
    'Credential-value': env_vars['PAT_SECRET'],
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
        #df = pd.DataFrame(data)

        # Display the first few rows of the DataFrame
        #print("Table view of data from the public REST API:")
        #print(df.head())
        #print(df.all())
        return data
        #display(df.head())
    else:
        print("Failed to fetch data from the API. Status code:", response.status_code)
        print(response.text)
