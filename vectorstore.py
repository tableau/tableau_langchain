import os
from experimental.utilities.setup_local_vector_db import query_tableau_vector_db

from dotenv import load_dotenv
load_dotenv()


tableau_site     = os.getenv('SITE_NAME')        
collection_name =  f"{tableau_site}_tableau_datasource_vector_search"

# Simple query example
query_text = "who won gold in olympic rowing?"
results = query_tableau_vector_db(
    query_text=query_text,
    collection_name=collection_name,
    n_results=10,
    debug=False
)
# print(results[0])

# print(f"Results type: {type(results)}")

# if results and len(results) > 0:
#     print(f"First result type: {type(results[0])}")
#     print(f"First result sample: {results[0]}")

# # Initialize an empty list to store extracted data
# extracted_data = []

# # Process the list of results directly
# for result in results:
#     # Each result should be a dictionary with metadata
#     if isinstance(result, dict):
#         # Extract relevant fields
#         extracted_data.append({
#             'name': result.get('name', 'N/A'),
#             'url': result.get('url', 'N/A'),
#             'dashboard_luid': result.get('luid', 'datasource'),  # Default to 'datasource' if not found
#             'isCertified': result.get('isCertified', 'N/A'),
#             'updatedAt': result.get('updatedAt', 'N/A'),
#             'distance': result.get('distance', 0)  # Use 0 as default if distance not available
#         })
#     else:
#         print(f"Unexpected result type: {type(result)}")

# Process the top search results
# top_ids = results.get('luid', [])
# top_meta = results.get('metadatas', [])
# best_id = top_ids[0] if top_ids else None
# best_metadata = top_meta[0] if top_meta else {}
# best_name = best_metadata.get('name', 'Unknown Data Source')
# best_desc = best_metadata.get('description', None)

print(results)

# print(results['luid']) 
# # print(results['documents'])
# print(results['distances']) 
# metadata = results['metadatas']
# for item in metadata:
#     print(item)
#     print(item.get('name'))

#     print(item.get('has_active_warning'))
#     print(item.get('is_certified'))
#     print(item.get('project_name'))


# print(top_meta)
extracted_data = []

num_items = len(results['luid'])

# Iterate over the indices of the lists
for i in range(num_items):
    # Get the metadata for the current index
    metadata = results['metadatas'][i]
    
    # Append a dictionary with the desired fields
    extracted_data.append({
        'name': metadata.get('name', 'N/A'),
        'has_active_warning': metadata.get('has_active_warning', 'N/A'),
        'dashboard_luid': results['luid'][i],
        'is_certified': metadata.get('is_certified', 'N/A'),
        'project_name': metadata.get('project_name', 'N/A'),
        'distance': results['distances'][i]
    })

print(extracted_data)