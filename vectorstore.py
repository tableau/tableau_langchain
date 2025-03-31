import os
from community.langchain_community.utilities.tableau.setup_local_vector_db import query_tableau_vector_db

from dotenv import load_dotenv
load_dotenv()


tableau_site     = os.getenv('SITE_NAME')        
collection_name =  f"{tableau_site}_vector_store"

# Simple query example
query_text = "who won gold in olympic rowing?"
results = query_tableau_vector_db(
    query_text=query_text,
    collection_name=collection_name,
    n_results=1,
    debug=False
)
print(results[0])

