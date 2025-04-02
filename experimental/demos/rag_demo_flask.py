from flask import Flask, request, jsonify, render_template
from modules import graphql
import chromadb
import numpy as np
from openai import OpenAI
from dotenv import load_dotenv
import os
import chromadb.utils.embedding_functions as embedding_functions

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)

openai_client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

def get_embedding_openai(text, model="text-embedding-3-small"):
   text = text.replace("\n", " ")
   return openai_client.embeddings.create(input = [text], model=model).data[0].embedding


openai_ef = embedding_functions.OpenAIEmbeddingFunction(
                api_key=os.getenv('OPENAI_API_KEY'),
                model_name="text-embedding-3-small"
            )

def convert_to_string(value):
    if isinstance(value, dict):
        return str(value)
    elif isinstance(value, list):
        return ', '.join(map(str, value))
    else:
        return str(value)
    
# Initialize the Chroma client
chroma_client = chromadb.PersistentClient(path="data")
collection_name = 'tableau_datasource_RAG_search'

# Try to get the collection
try:
    collection = chroma_client.get_collection(name=collection_name, embedding_function=openai_ef)
    print("Collection exists.")
except Exception as e:
    print("Collection does not exist. Creating collection...")
    # Fetch data from Tableau
    server, auth = graphql.get_tableau_client()
    datasources = graphql.fetch_datasources(server, auth)

    documents = []
    ids = []
    metadatas = []

    for datasource in datasources:
        # Extract the text to embed
        text_to_embed = datasource['dashboard_overview']

        # Extract the unique identifier
        unique_id = datasource['id']

        # Prepare metadata (exclude 'dashboard_overview' and 'id')
        metadata = {k: v for k, v in datasource.items() if k not in ['dashboard_overview', 'id']}

        # Convert metadata values to strings
        metadata = {k: convert_to_string(v) for k, v in metadata.items() if isinstance(v, (str, int, float, bool, dict, list))}

        documents.append(text_to_embed)
        ids.append(unique_id)
        metadatas.append(metadata)

    # Create the collection and add data
    collection = chroma_client.get_or_create_collection(name=collection_name, embedding_function=openai_ef)
    collection.add(
        documents=documents,
        metadatas=metadatas,
        ids=ids
    )

# Route to display the search form
@app.route('/', methods=['GET'])
def index():
    return render_template('search.html')

# Route to handle search queries
@app.route('/search', methods=['POST'])
def search():
    # Get the user's query from the form
    user_input = request.form.get('query')
    if not user_input:
        return jsonify({"error": "No query provided"}), 400

    # Perform the query
    results = collection.query(
        query_texts=[user_input],
        n_results=5  
    )

    metadatas = results['metadatas']
    distances = results['distances']

    # Initialize an empty list to store extracted data
    extracted_data = []

    for meta_list, dist_list in zip(metadatas, distances):
        for metadata, distance in zip(meta_list, dist_list):
            name = metadata.get('name', 'N/A')
            uri = metadata.get('uri', 'N/A')
            luid = metadata.get('luid', 'N/A')
            isCertified = metadata.get('isCertified', 'N/A')
            updatedAt = metadata.get('updatedAt', 'N/A')

            # Append the extracted data to the list, including 'distance'
            extracted_data.append({
                'name': name,
                'uri': uri,
                'luid': luid,
                'isCertified': isCertified,
                'updatedAt': updatedAt,
                'distance': distance
            })

    # Render the results template
    return render_template('results.html', results=extracted_data, query=user_input)

# Run the Flask app
if __name__ == '__main__':
    app.run(debug=True)
