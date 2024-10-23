import tableauserverclient as TSC
from dotenv import load_dotenv
import os

def get_tableau_client():
    load_dotenv()
    tableau_server = 'https://' + os.getenv('TABLEAU_DOMAIN')
    tableau_pat_name = os.getenv('PAT_NAME')
    tableau_pat_secret = os.getenv('PAT_SECRET')
    tableau_sitename = os.getenv('SITE_NAME')
    tableau_auth = TSC.PersonalAccessTokenAuth(tableau_pat_name, tableau_pat_secret, tableau_sitename)
    server = TSC.Server(tableau_server, use_server_version=True)
    return server, tableau_auth

def fetch_dashboard_data(server, auth):
    with server.auth.sign_in(auth):
        # Read the GraphQL query from the file
        query_file_path = os.path.join('tools','queryData','prompts', 'tab_dashboard_fields.graphql')
        with open(query_file_path, 'r') as f:
            query = f.read()
        # Query the Metadata API and store the response in resp
        resp = server.metadata.query(query)
        return resp['data']['dashboards']
    
def fetch_sheets_data(server, auth):
    with server.auth.sign_in(auth):
        # Read the GraphQL query from the file
        query_file_path = os.path.join('tools','queryData','prompts', 'tab_sheets.graphql')
        with open(query_file_path, 'r') as f:
            query = f.read()
        # Query the Metadata API and store the response in resp
        resp = server.metadata.query(query)
        return resp['data']['sheets']
    
def fetch_datasources(server, auth):
    with server.auth.sign_in(auth):

        # Read the GraphQL query from the file
        query_file_path = os.path.join('tools','queryData','prompts', 'tab_datasources.graphql')
        with open(query_file_path, 'r') as f:
            query = f.read()

        # Query the Metadata API and store the response in resp
        resp = server.metadata.query(query)
        
        # Prepare datasources for RAG
        datasources = resp['data']['publishedDatasources']

        for datasource in datasources:

            # Combine datasource columns (is not hidden) to one cell for RAG
            fields = datasource['fields']

            field_entries = []
            for field in fields:
                # Exclude columns that are hidden
                if not field.get('isHidden', True):
                    name = field.get('name', '')
                    description = field.get('description', '')
                    # If there's a description include it
                    if description:
                        # Remove newlines and extra spaces
                        description = ' '.join(description.split())
                        field_entry = f"- {name}: [{description}]"
                    else:
                        field_entry = "- " + name
                    field_entries.append(field_entry)

            # Combining Datasource columns
            concatenated_field_entries = '\n'.join(field_entries)

            # Datasource RAG headers
            datasource_name = datasource['name']
            datasource_desc = datasource['description']
            datasource_project = datasource['projectName']

            # Formating Output for readability
            rag_column = f"Datasource: {datasource_name}\n{datasource_desc}\n{datasource_project}\n\nDatasource Columns:\n{concatenated_field_entries}"
            
            datasource['dashboard_overview'] = rag_column

            # Simplifying output schema 
            keys_to_extract = [
                'dashboard_overview',
                'id',
                'luid',
                'uri',
                'vizportalId',
                'vizportalUrlId',
                'name',
                'hasExtracts',
                'createdAt',
                'updatedAt',
                'extractLastUpdateTime',
                'extractLastRefreshTime',
                'extractLastIncrementalUpdateTime',
                'projectName',
                'containerName',
                'isCertified',
                'description'
            ]

            # Create a new dictionary with only the specified keys
            datasource = {key: datasource.get(key) for key in keys_to_extract}

        return datasources

