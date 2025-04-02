from modules import graphql, vectorstore
import json 
import os
server, auth = graphql.get_tableau_client()
tab_dashboards = graphql.fetch_dashboard_data(server, auth)
print('Dashboards fetched')

#collection = vectorstore.setup_vector_db(datasources = tab_dashboards, collection_name = 'dash_RAG', mode = 'recreate', debug = True)
collection = vectorstore.setup_vector_db(datasources = tab_dashboards, collection_name = 'dash_RAG', debug = True)
#collection =''

print('Vector store created')

user_query = 'soccer match'
results = collection.query(
    query_texts=[user_query], 
    n_results=50 
)

metadatas = results['metadatas']
distances = results['distances']

# Initialize an empty list to store extracted data
extracted_data = []

# with server.auth.sign_in(auth):
#     for meta_list, dist_list in zip(metadatas, distances):
#         for metadata, distance in zip(meta_list, dist_list):
#             dashboard_name = metadata.get('dashboard_name', 'N/A')
#             sheet_name = metadata.get('sheet_name', 'N/A')
#             workbook_luid = metadata.get('workbook_luid', 'N/A')
#             dashboard_luid = metadata.get('dashboard_luid', 'N/A')
            
#             # Append the extracted data to the list, including 'distance'
#             extracted_data.append({
#                 'dashboard_name': dashboard_name,
#                 'dashboard_luid': dashboard_luid,
#                 'sheet_name': sheet_name,
#                 'workbook_luid': workbook_luid,
#                 'distance': distance
#             })

#             # Initialize an empty dictionary to hold the aggregated results
#             aggregated_data = {}

#             # Iterate over each record in the extracted data
#             for record in extracted_data:
#                 dashboard_name = record['dashboard_name']
#                 dashboard_luid = record['dashboard_luid']
#                 workbook_luid = record['workbook_luid']
#                 distance = record['distance']

#                 if dashboard_name not in aggregated_data:
#                     # Initialize the aggregation for this dashboard
#                     aggregated_data[dashboard_name] = {
#                         'dashboard_name': dashboard_name,
#                         'dashboard_luid': dashboard_luid,
#                         'workbook_luid': workbook_luid,
#                         'min_distance': distance
#                     }
#                 else:
#                     # Update MAX of dashboard_luid
#                     if dashboard_luid > aggregated_data[dashboard_name]['dashboard_luid']:
#                         aggregated_data[dashboard_name]['dashboard_luid'] = dashboard_luid

#                     # Update MAX of workbook_luid
#                     if workbook_luid > aggregated_data[dashboard_name]['workbook_luid']:
#                         aggregated_data[dashboard_name]['workbook_luid'] = workbook_luid

#                     # Update MIN of distance
#                     if distance < aggregated_data[dashboard_name]['min_distance']:
#                         aggregated_data[dashboard_name]['min_distance'] = distance

#     # Convert the aggregated data to a list if needed
#     aggregated_list = list(aggregated_data.values())

#     # Filter out entries where 'dashboard_luid' is empty or None
#     filtered_list = [item for item in aggregated_list if item.get('dashboard_luid')]

#     for item in filtered_list:
#         graphql.save_dashboard_image(server, item['dashboard_luid'])


# for item in filtered_list:
#     print(f"Dashboard Name: {item['dashboard_name']}")
#     print(f"  Max Dashboard LUID: {item['dashboard_luid']}")
#     print(f"  Max Workbook LUID: {item['workbook_luid']}")
#     print(f"  Min Distance: {item['min_distance']}")
#     print("-" * 40)

with server.auth.sign_in(auth):
    extracted_data = []  
    
    for meta_list, dist_list in zip(metadatas, distances):
        for metadata, distance in zip(meta_list, dist_list):
            dashboard_name = metadata.get('dashboard_name', 'N/A')
            sheet_name = metadata.get('sheet_name', 'N/A')
            workbook_luid = metadata.get('workbook_luid', 'N/A')
            dashboard_luid = metadata.get('dashboard_luid', 'N/A')
            
            # Append the extracted data to the list, including 'distance'
            extracted_data.append({
                'dashboard_name': dashboard_name,
                'dashboard_luid': dashboard_luid,
                'sheet_name': sheet_name,
                'workbook_luid': workbook_luid,
                'distance': distance
            })
    
    # Initialize an empty dictionary to hold the aggregated results
    aggregated_data = {}
    
    # Iterate over each record in the extracted data
    for record in extracted_data:
        dashboard_name = record['dashboard_name']
        dashboard_luid = record['dashboard_luid']
        workbook_luid = record['workbook_luid']
        distance = record['distance']
    
        if dashboard_name not in aggregated_data:
            # Initialize the aggregation for this dashboard
            aggregated_data[dashboard_name] = {
                'dashboard_name': dashboard_name,
                'dashboard_luid': dashboard_luid,
                'workbook_luid': workbook_luid,
                'min_distance': distance
            }
        else:
            # Update MAX of dashboard_luid
            if dashboard_luid > aggregated_data[dashboard_name]['dashboard_luid']:
                aggregated_data[dashboard_name]['dashboard_luid'] = dashboard_luid
    
            # Update MAX of workbook_luid
            if workbook_luid > aggregated_data[dashboard_name]['workbook_luid']:
                aggregated_data[dashboard_name]['workbook_luid'] = workbook_luid
    
            # Update MIN of distance
            if distance < aggregated_data[dashboard_name]['min_distance']:
                aggregated_data[dashboard_name]['min_distance'] = distance
    
    # Convert the aggregated data to a list if needed
    aggregated_list = list(aggregated_data.values())
    
    # Filter out entries where 'dashboard_luid' is empty or None
    filtered_list = [item for item in aggregated_list if item.get('dashboard_luid')]
    
    for item in filtered_list:
        graphql.save_dashboard_image(server, item['dashboard_luid'])
    
    # Print the aggregated results
    for item in filtered_list:
        print(f"Dashboard Name: {item['dashboard_name']}")
        print(f"  Max Dashboard LUID: {item['dashboard_luid']}")
        print(f"  Max Workbook LUID: {item['workbook_luid']}")
        print(f"  Min Distance: {item['min_distance']}")
        print("-" * 40)
