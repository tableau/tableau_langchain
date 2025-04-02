from modules import graphql, vectorstore
import json 
server, auth = graphql.get_tableau_client()
tab_datasources = graphql.fetch_datasources(server, auth)

#vectorstore.prepare_documents_for_chroma(tab_datasources, text_field = 'dashboard_overview')

print('Datasources fetched')

# try:
#     filtered_datasource = next(ds for ds in tab_datasources if ds['id'] == '00060764-11dc-4bd4-c3ca-7baec2f16444')
#     print(filtered_datasource)
# except StopIteration:
#     print("Datasource not found")

# # Helper function to convert values to strings
# def convert_to_string(value):
#     if isinstance(value, dict):
#         return str(value)
#     elif isinstance(value, list):
#         return ', '.join(map(str, value))
#     else:
#         return str(value)
    
# # print(f"\nCreating new collection: {collection_name}")
# documents = []
# ids = []
# metadatas = []

# for i, datasource in enumerate(tab_datasources):
#     try:
#         # Extract the text to embed
#         text_to_embed = datasource.get('dashboard_overview', '')
#         #print(text_to_embed)
        
#         # if debug:
#         #     print(f"\nProcessing document {i+1}/{len(filtered_datasource)}")
#         #     print(f"Text length: {len(str(text_to_embed))}")
#         #     print("First 100 chars of text:", str(text_to_embed)[:100])
        
#         # if not text_to_embed:
#         #     print(f"Warning: Empty dashboard_overview for document {i+1}")
#         #     continue
        
#         # Extract the unique identifier
#         unique_id = str(datasource.get('id', f'doc_{i}'))
#         #print(unique_id)
        
#         # Prepare metadata (exclude 'dashboard_overview' and 'id')
#         metadata = {k: v for k, v in datasource.items() 
#                     if k not in ['dashboard_overview', 'id']}
        
#         # Remove any nested data structures from metadata
#         metadata = {k: convert_to_string(v) for k, v in metadata.items() 
#                     if isinstance(v, (str, int, float, bool, dict, list))}
        
#         # if debug and i == 0:
#         #     print("\nSample metadata structure:")
#         #     print(json.dumps(metadata, indent=2)[:200] + "...")
        
#         documents.append(text_to_embed)
#         ids.append(unique_id)
#         metadatas.append(metadata)
        
#     except Exception as e:
#         print(f"Error processing document {i+1}: {str(e)}")
#         print(f"Problematic datasource: {json.dumps(datasource, indent=2)}")
#         raise

# print(str(len(documents))+ ' documents to upload')
# print(str(len(ids))+ ' ids to upload')
# print(str(len(metadatas))+ ' metadatas to upload')
# print(documents[0])

collection = vectorstore.setup_vector_db(datasources = tab_datasources, mode = 'recreate', debug = True)
#collection = vectorstore.setup_vector_db(datasources = tab_datasources)

print('Vector store created')

user_query = 'movies'
results = collection.query(
    query_texts=[user_query], 
    n_results=10 
)

metadatas = results['metadatas']
distances = results['distances']

# Initialize an empty list to store extracted data
extracted_data = []

for meta_list, dist_list in zip(metadatas, distances):
    for metadata, distance in zip(meta_list, dist_list):
        name = metadata.get('name', 'N/A')
        url = metadata.get('url', 'N/A')
        luid = metadata.get('luid', 'N/A')
        isCertified = metadata.get('isCertified', 'N/A')
        updatedAt = metadata.get('updatedAt', 'N/A')
        
        # Append the extracted data to the list, including 'distance'
        extracted_data.append({
            'name': name,
            'url': url,
            'luid': luid,
            'isCertified': isCertified,
            'updatedAt': updatedAt,
            'distance': distance
        })


for item in extracted_data:
    print(f"Name: {item['name']}")
    print(f"URL: {item['url']}")
    print(f"LUID: {item['luid']}")
    print(f"Certified?: {item['isCertified']}")
    print(f"Last Update: {item['updatedAt']}")
    print(f"Vector distance: {item['distance']}")
    print("-" * 40)



