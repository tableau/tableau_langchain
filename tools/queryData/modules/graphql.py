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

def fetch_dashboard_data_old(server, auth):
    with server.auth.sign_in(auth):
        # Query the Metadata API and store the response in resp
        query = """
            query GetAllDashboards {
                dashboards {
                    id
                    name
                    path
                    workbook {
                        id
                        name
                        luid
                        projectName
                        tags {
                            name
                        }
                        sheets {
                            id
                            name
                            createdAt
                            updatedAt
                            sheetFieldInstances {
                                name
                                description
                                isHidden
                                id
                            }
                            worksheetFields{
                                name
                                description
                                isHidden
                                formula
                                aggregation
                                id
                            }
                        }
                    }
                }
            }
        """
        resp = server.metadata.query(query)
        return resp['data']['dashboards']

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
        return resp['data']['publishedDatasources']

def main():
    server, auth = get_tableau_client()
    # dashboards = fetch_dashboard_data(server, auth)
    # sheets = fetch_sheets_data(server, auth)
    datasources = fetch_datasources(server, auth)
    for datasource in datasources:
        print(datasource)

    # for sheet in sheets:
    #     print(sheet)

    # Print the result
    # for dashboard in dashboards:
    #     print(f"Dashboard ID: {dashboard['id']}, Name: {dashboard['name']}, Path: {dashboard['path']}")

if __name__ == "__main__":
    main()
