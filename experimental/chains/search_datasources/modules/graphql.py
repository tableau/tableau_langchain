import tableauserverclient as TSC
from modules.prompts import tab_dashboard_fields
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
       
def fetch_datasources(server, auth):
    with server.auth.sign_in(auth):

        # Read the GraphQL query from the file
        query_file_path = os.path.join('query_data_chain','modules','prompts','tab_datasources.graphql')
        with open(query_file_path, 'r') as f:
            query = f.read()

        # Query the Metadata API and store the response in resp
        resp = server.metadata.query(query)

        if 'errors' in resp:
            print("Error in query:", resp['errors'])
            exit()

        tableauSites = resp['data']['tableauSites']
        # Prepare datasources for RAG
        # datasources = resp['data']['publishedDatasources']

        for site in tableauSites:
            site_name = site.get('name', 'Unnamed site')
            datasources = site.get('publishedDatasources', [])
            print(f"Site: {site_name}, Number of Datasources: {len(datasources)}")

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

                datasource_rest = server.datasources.get_by_id(datasource['luid'])
                datasource['url'] = datasource_rest.webpage_url

                # Simplifying output schema 
                keys_to_extract = [
                    'dashboard_overview',
                    'id',
                    'luid',
                    'url',
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

def process_fields(fields):
    """Process fields and return concatenated string of field entries."""
    field_entries = []
    for field in fields:
        if not field.get('isHidden', True):
            name = field.get('name', '')
            description = field.get('description', '')
            if description:
                description = ' '.join(description.split())
                field_entry = f"- {name}: [{description}]"
            else:
                field_entry = f"- {name}"
            field_entries.append(field_entry)
    return '\n'.join(field_entries)

def flatten_dashboard(dashboard_data):
    """Flatten dashboard structure into a list of dictionaries with RAG format."""
    
    if not dashboard_data or not isinstance(dashboard_data, dict):
        raise ValueError("Invalid dashboard data provided.")
    
    flattened_sheets = []
    
    # workbook = dashboard_data.get('workbook', {})
    workbook = dashboard_data.get('workbook') or {}
    
    for sheet in workbook.get('sheets', []):
        # Process fields for this specific sheet only
        field_instances = process_fields(sheet.get('sheetFieldInstances', []))
        worksheet_fields = process_fields(sheet.get('worksheetFields', []))
        
        # Create RAG overview for this specific sheet only
        rag_column = f"""Sheet: {sheet.get('name')}
Dashboard: {dashboard_data.get('name')}
Workbook: {workbook.get('name')}
Project: {workbook.get('projectName')}

Fields:
{field_instances}

Calculated Fields:
{worksheet_fields}"""
        
        # Create sheet dictionary with all relevant fields
        sheet_dict = {
            # RAG specific field
            'dashboard_overview': rag_column,
            
            # Dashboard level info
            'dashboard_id': dashboard_data.get('id'),
            'dashboard_name': dashboard_data.get('name'),
            'dashboard_luid': dashboard_data.get('luid'),
            'dashboard_path': dashboard_data.get('path'),
            
            # Workbook level info
            'workbook_id': workbook.get('id'),
            'workbook_name': workbook.get('name'),
            'workbook_luid': workbook.get('luid'),
            'workbook_project_name': workbook.get('projectName'),
            
            # Sheet level info
            'sheet_id': sheet.get('id'),
            'sheet_name': sheet.get('name'),
            'sheet_luid': sheet.get('luid'),
            'created_at': sheet.get('createdAt'),
            'updated_at': sheet.get('updatedAt'),
            
            # Raw field data
            'field_instances_raw': field_instances,
            'worksheet_fields_raw': worksheet_fields
        }
        
        flattened_sheets.append(sheet_dict)
    
    return flattened_sheets

# def fetch_dashboard_data(server, auth):
    
#     with server.auth.sign_in(auth):

#         # Get the list of responses
#         resp_list = tab_dashboard_fields.get_all_dashboards("Demonstration", server, auth)
       
#         # Initialize a list to collect all tableau sites
#         all_tableau_sites = []

#         # Iterate over each response in the list
#         for resp in resp_list:
#             if 'data' in resp and 'tableauSites' in resp['data']:
#                 tableau_sites = resp['data']['tableauSites']
#                 all_tableau_sites.extend(tableau_sites)
#             else:
#                 print("No data found in response.")
#                 continue  # Skip to the next response if data is missing

#         processed_dashboards = []

#         # Iterate over each site
#         for site in tableau_sites:
#             print(f"Site Name: {site['name']}")
#             workbooks_connection = site.get('workbooksConnection', {})
#             workbook_nodes = workbooks_connection.get('nodes', [])

#             # Iterate over each workbook
#             for workbook in workbook_nodes:
#                 dashboards = workbook.get('dashboards', [])               

#                 for dashboard in dashboards:
#                     flattened_sheets = flatten_dashboard(dashboard)
#                     # Check if flattened_sheets is a list
#                     if isinstance(flattened_sheets, list):
#                         processed_dashboards.extend(flattened_sheets)
#                     else:
#                         # Handle the case where flattened_sheets is not a list
#                         processed_dashboards.append(flattened_sheets)
        
#         return processed_dashboards
    
def fetch_dashboard_data(server, auth):
    
    with server.auth.sign_in(auth):
        # Get the list of responses
        resp_list = tab_dashboard_fields.get_all_dashboards("Demonstration", server, auth)
        
        print(f"Number of responses received: {len(resp_list)}")
       
        # Initialize a list to collect all tableau sites
        all_tableau_sites = []

        # Iterate over each response in the list
        for i, resp in enumerate(resp_list):
            if 'data' in resp and 'tableauSites' in resp['data']:
                tableau_sites = resp['data']['tableauSites']
                print(f"Response {i+1}: Number of tableau sites: {len(tableau_sites)}")
                all_tableau_sites.extend(tableau_sites)
            else:
                print(f"Response {i+1}: No data found in response.")
                continue  # Skip to the next response if data is missing

        print(f"Total number of tableau sites collected: {len(all_tableau_sites)}")
        
        processed_dashboards = []

        # Iterate over each site
        for site in all_tableau_sites:
            print(f"Processing Site Name: {site['name']}")
            workbooks_connection = site.get('workbooksConnection', {})
            workbook_nodes = workbooks_connection.get('nodes', [])

            print(f"Number of workbooks in site '{site['name']}': {len(workbook_nodes)}")

            # Iterate over each workbook
            for workbook in workbook_nodes:
                dashboards = workbook.get('dashboards', [])
                print(f"Workbook '{workbook.get('name', 'Unnamed')}': Number of dashboards: {len(dashboards)}")
                
                for dashboard in dashboards:
                    flattened_sheets = flatten_dashboard(dashboard)
                    # Check if flattened_sheets is a list
                    if isinstance(flattened_sheets, list):
                        processed_dashboards.extend(flattened_sheets)
                    else:
                        # Handle the case where flattened_sheets is not a list
                        processed_dashboards.append(flattened_sheets)
        
        print(f"Total number of processed dashboards: {len(processed_dashboards)}")
        return processed_dashboards



def save_dashboard_image(server, dashboard_luid, image_dir='./query_data_chain/static/dashboard_images'):
    """
    Save a dashboard image to disk, skipping if the file already exists.
    
    Args:
        server (TSC.Server): Tableau Server Client instance
        dashboard_luid (str): LUID of the dashboard to save
        image_dir (str): Directory to save the image files
    """
    # Check if the image file already exists
    image_path = os.path.join(image_dir, f"{dashboard_luid}.png")
    if os.path.exists(image_path):
        print(f"Skipping image for dashboard LUID: {dashboard_luid} - file already exists.")
        return
    
    try:
        # Get the view and populate the image
        selected_view = server.views.get_by_id(dashboard_luid)
        server.views.populate_image(selected_view)
        
        # Save the image to disk
        os.makedirs(image_dir, exist_ok=True)
        with open(image_path, 'wb') as f:
            f.write(selected_view.image)
        
        print(f"Saved image for dashboard LUID: {dashboard_luid}")
    
    except Exception as e:
        print(f"Error saving image for dashboard LUID: {dashboard_luid} - {str(e)}")
