import os, requests, json
def read(read_url, datasource_luid, auth_secret):
    url = read_url
    payload = json.dumps({
        "datasource": {
            "datasourceLuid": datasource_luid
    }
    })
    headers = {
    'X-Tableau-Auth': auth_secret,
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