# import tableauserverclient as TSC
# from dotenv import load_dotenv
# import os

# def get_tableau_client():
#     load_dotenv()
#     tableau_server = 'https://' + os.getenv('TABLEAU_DOMAIN')
#     tableau_pat_name = os.getenv('PAT_NAME')
#     tableau_pat_secret = os.getenv('PAT_SECRET')
#     tableau_sitename = os.getenv('SITE_NAME')
#     tableau_auth = TSC.PersonalAccessTokenAuth(tableau_pat_name, tableau_pat_secret, tableau_sitename)
#     server = TSC.Server(tableau_server, use_server_version=True)
#     return server, tableau_auth

# server, tableau_auth = get_tableau_client()

# # query = """{

# # tableauSites(filter: {name: "Demonstration"}) {
# #   publishedDatasources{
# #       id
# #       luid
# #       uri
# #       vizportalId
# #       vizportalUrlId
# #       name
# #       hasExtracts
# #       createdAt
# #       updatedAt
# #       extractLastUpdateTime
# #       extractLastRefreshTime
# #       extractLastIncrementalUpdateTime
# #       projectName
# #       containerName
# #       isCertified
# #       description
# #       fields {
# #         id
# #         name
# #         fullyQualifiedName
# #         description
# #         isHidden
# #         folderName
# #       }
# #     }
# # }

# # }
# #     """

# # print(os.getenv('SITE_NAME'))

# # with server.auth.sign_in(tableau_auth):

# #     resp = server.metadata.query(query)
# #     datasources = resp['data']['tableauSites']

# #     published_datasources = []

# #     for item in datasources:
# #         # Extract the 'publishedDatasources' from each dictionary if it exists
# #         if 'publishedDatasources' in item:
# #             published_datasources.append(item['publishedDatasources'])

# #     # Now `published_datasources` contains all the 'publishedDatasources' from each dictionary in the list
# #     # published_datasources

# #     for datasource in published_datasources:

# #             # Combine datasource columns (is not hidden) to one cell for RAG
# #             print(datasource)
# #             fields = datasource['fields']

# #             field_entries = []
# #             for field in fields:
# #                 # Exclude columns that are hidden
# #                 if not field.get('isHidden', True):
# #                     name = field.get('name', '')
# #                     description = field.get('description', '')
# #                     # If there's a description include it
# #                     if description:
# #                         # Remove newlines and extra spaces
# #                         description = ' '.join(description.split())
# #                         field_entry = f"- {name}: [{description}]"
# #                     else:
# #                         field_entry = "- " + name
# #                     field_entries.append(field_entry)

# #             # Combining Datasource columns
# #             concatenated_field_entries = '\n'.join(field_entries)

# #             # Datasource RAG headers
# #             datasource_name = datasource['name']
# #             datasource_desc = datasource['description']
# #             datasource_project = datasource['projectName']

# #             # Formating Output for readability
# #             rag_column = f"Datasource: {datasource_name}\n{datasource_desc}\n{datasource_project}\n\nDatasource Columns:\n{concatenated_field_entries}"
            
# #             datasource['dashboard_overview'] = rag_column

# #             # Simplifying output schema 
# #             keys_to_extract = [
# #                 'dashboard_overview',
# #                 'id',
# #                 'luid',
# #                 'uri',
# #                 'vizportalId',
# #                 'vizportalUrlId',
# #                 'name',
# #                 'hasExtracts',
# #                 'createdAt',
# #                 'updatedAt',
# #                 'extractLastUpdateTime',
# #                 'extractLastRefreshTime',
# #                 'extractLastIncrementalUpdateTime',
# #                 'projectName',
# #                 'containerName',
# #                 'isCertified',
# #                 'description'
# #             ]

# #             # Create a new dictionary with only the specified keys
# #             datasource = {key: datasource.get(key) for key in keys_to_extract}

# #     print(datasources[0])


# # with server.auth.sign_in(tableau_auth):
# #     resp = server.metadata.query(query)
# #     datasources = resp['data']['tableauSites']

# #     for site in datasources:
# #         # Checking if 'publishedDatasources' exists and ensuring it's a list before iterating
# #         if 'publishedDatasources' in site and isinstance(site['publishedDatasources'], list):
# #             for datasource in site['publishedDatasources']:
# #                 # Extracting fields only if it exists and is a list
# #                 fields = datasource.get('fields', []) if isinstance(datasource.get('fields'), list) else []

# #                 field_entries = []
# #                 for field in fields:
# #                     if not field.get('isHidden', False):
# #                         name = field.get('name', 'Unnamed field')
# #                         description = field.get('description', '')
# #                         # Formatting the field entry with description if it exists
# #                         field_entry = f"- {name}: {description}" if description else f"- {name}"
# #                         field_entries.append(field_entry)

# #                 # Concatenate all field entries into a single string
# #                 concatenated_field_entries = '\n'.join(field_entries)

# #                 # Prepare the datasource information
# #                 datasource_name = datasource.get('name', 'Unnamed datasource')
# #                 datasource_desc = datasource.get('description', 'No description')
# #                 datasource_project = datasource.get('projectName', 'No project name')

# #                 # Formatted output for each datasource
# #                 rag_column = (f"Datasource: {datasource_name}\n"
# #                               f"Description: {datasource_desc}\n"
# #                               f"Project: {datasource_project}\n\n"
# #                               f"Datasource Columns:\n{concatenated_field_entries}")

# #                 print(rag_column)  
                
                
# #                 # Displaying the formatted information

# #     # Optional: To see how the first site looks after processing
# #     if datasources:
# #         datasources_str = str(datasources[0])
# #         print(datasources_str[:10000])
# #         # print(datasources[0])


# #     # datasources_str = str(datasources)
# #     # # Print the first 100 characters
# #     # print(datasources_str[:10000])
# #     #print(datasources)

# site_name = "Demonstration"

# query = f"""{{
#   tableauSites(filter: {{ name: "{site_name}" }}) {{
#     name
#     publishedDatasources {{
#       id
#       name
#       description
#       projectName
#       fields {{
#         id
#         name
#         fullyQualifiedName
#         description
#         isHidden
#         folderName
#       }}
#     }}
#   }}
# }}"""

# with server.auth.sign_in(tableau_auth):
#     resp = server.metadata.query(query)
#     print(resp)
#     sites = resp['data']['sites']

#     for site in sites:
#         datasources = site.get('datasources', [])
#         for datasource in datasources:
#             fields = datasource.get('fields', [])

#             field_entries = []
#             for field in fields:
#                 if not field.get('isHidden', False):
#                     name = field.get('name', 'Unnamed field')
#                     description = field.get('description', '')
#                     field_entry = f"- {name}: {description}" if description else f"- {name}"
#                     field_entries.append(field_entry)

#             concatenated_field_entries = '\n'.join(field_entries)

#             datasource_name = datasource.get('name', 'Unnamed datasource')
#             datasource_desc = datasource.get('description', 'No description')
#             datasource_project = datasource.get('projectName', 'No project name')

#             rag_column = (f"Datasource: {datasource_name}\n"
#                           f"Description: {datasource_desc}\n"
#                           f"Project: {datasource_project}\n\n"
#                           f"Datasource Columns:\n{concatenated_field_entries}")

#             print(rag_column)


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

server, tableau_auth = get_tableau_client()

with server.auth.sign_in(tableau_auth):
    # Fetch available site names
    resp = server.metadata.query("""{ tableauSites { name } }""")
    if 'errors' in resp:
        print("Error fetching sites:", resp['errors'])
        exit()
    tableauSites = resp['data']['tableauSites']
    print("Available Sites:")
    for site in tableauSites:
        print(f"- {site.get('name')}")

    # Set the exact site name
    site_display_name = "Demonstration"  

    # GraphQL query with the correct site name
    query = f"""{{
      tableauSites(filter: {{ name: "{site_display_name}" }}) {{
        name
        luid
        publishedDatasources {{
          id
          name
          description
          projectName
          fields {{
            id
            name
            fullyQualifiedName
            description
            isHidden
            folderName
          }}
        }}
      }}
    }}"""

    resp = server.metadata.query(query)
    if 'errors' in resp:
        print("Error in query:", resp['errors'])
        exit()
    tableauSites = resp['data']['tableauSites']
    if not tableauSites:
        print(f"No data found for site '{site_display_name}'.")
        exit()

    for site in tableauSites:
        site_name = site.get('name', 'Unnamed site')
        datasources = site.get('publishedDatasources', [])
        print(f"Site: {site_name}, Number of Datasources: {len(datasources)}")
        for datasource in datasources:
            fields = datasource.get('fields', [])
            field_entries = []
            for field in fields:
                if not field.get('isHidden', False):
                    name = field.get('name', 'Unnamed field')
                    description = field.get('description', '')
                    field_entry = f"- {name}: {description}" if description else f"- {name}"
                    field_entries.append(field_entry)
            concatenated_field_entries = '\n'.join(field_entries)
            datasource_name = datasource.get('name', 'Unnamed datasource')
            datasource_desc = datasource.get('description', 'No description')
            datasource_project = datasource.get('projectName', 'No project name')
            rag_column = (f"Datasource: {datasource_name}\n"
                          f"Description: {datasource_desc}\n"
                          f"Project: {datasource_project}\n\n"
                          f"Datasource Columns:\n{concatenated_field_entries}")
            print(rag_column)
            break
