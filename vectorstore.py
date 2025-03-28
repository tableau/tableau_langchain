import os
from dotenv import load_dotenv
load_dotenv()
# # Import Tableau authentication and metadata retrieval functions
# from login import generate_tableau_auth_token

# from community.langchain_community.utilities.tableau.metadata import get_datasources_metadata

# # Import vector database helper functions
# from community.langchain_community.utilities.tableau.search_datasources import (
#     format_datasources_for_rag,
#     create_datasources_vector_db,
#     query_datasources_vector_db
# )

from community.langchain_community.utilities.tableau.setup_local_vector_db import query_tableau_vector_db


tableau_site     = os.getenv('SITE_NAME')        
collection_name =  f"{tableau_site}_vector_store"

# Optional: Simple query example
query_text = "what does the cow say?"
results = query_tableau_vector_db(
    query_text=query_text,
    collection_name=collection_name,
    n_results=1,
    debug=False
)
print(results)

# def main():
#     # Load environment variables
#     load_dotenv()

#     # Tableau configuration from environment variables
#     tableau_server = os.getenv('TABLEAU_CLD_DOMAIN')
#     tableau_site = os.getenv('CLD_SITE_NAME')
#     tableau_jwt_client_id = os.getenv('TABLEAU_CLD_JWT_CLIENT_ID')
#     tableau_jwt_secret_id = os.getenv('TABLEAU_CLD_JWT_SECRET_ID')
#     tableau_jwt_secret = os.getenv('TABLEAU_CLD_JWT_SECRET')
#     tableau_api_version = os.getenv('TABLEAU_CLD_API') 
#     tableau_user = os.getenv('TABLEAU_CLD_USER') 

#     try:
#         # Generate authentication token
#         auth_token = generate_tableau_auth_token(
#             jwt_client_id=tableau_jwt_client_id,
#             jwt_secret_id=tableau_jwt_secret_id,
#             jwt_secret=tableau_jwt_secret,
#             tableau_server=tableau_server,
#             tableau_site=tableau_site,
#             tableau_user=tableau_user,
#             tableau_api_version=tableau_api_version
#         )
        
#         # Retrieve datasources metadata
#         datasources_metadata = get_datasources_metadata(
#             domain=tableau_server,
#             api_key=auth_token
#         )
        
#         # Format datasources for RAG
#         formatted_datasources = format_datasources_for_rag(datasources_metadata, debug=True)
        
#         # datasources_collection =  f"{tableau_site}_tableau_datasource_vector_search"

#         # Create Vector Database
#         # vector_db = create_datasources_vector_db(
#         #     datasources=formatted_datasources,
#         #     debug=True,
#         #     collection_name = f"{tableau_site}_tableau_datasource_vector_search"
#         # )

#         collection_name = f"{tableau_site}_tableau_datasource_vector_search"
        
        
#         # Optional: Simple query example
#         query_text = "what does the cow say?"
#         results = query_tableau_vector_db(
#             query_text=query_text,
#             collection_name=collection_name,
#             n_results=1,
#             debug=False
#         )
#         print(results)
        
#         return results

#     except Exception as e:
#         print(f"Error in Tableau Datasource Vector DB Setup: {e}")
#         return None

# if __name__ == '__main__':
#     main()