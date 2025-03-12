from modules import graphql, vectorstore
from flask import Flask, request, jsonify, render_template, send_file
import json 
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

server, auth = graphql.get_tableau_client()
tab_datasources = graphql.fetch_datasources(server, auth)
#tab_dashboards = graphql.fetch_dashboard_data(server, auth)
tab_dashboards = tab_datasources
print('Datasources fetched')

#collection = vectorstore.load_vector_db(collection_name = 'datasources')
#collection = vectorstore.setup_vector_db(datasources = tab_datasources, collection_name = 'datasources', mode = 'recreate', debug = True)
collection = vectorstore.setup_vector_db(datasources = tab_datasources)
collection_dash = vectorstore.setup_vector_db(datasources = tab_dashboards, collection_name = 'dash_RAG')

print('Vector store created')

# Initialize Flask app
app = Flask(__name__)

# Route to display the search form
@app.route('/', methods=['GET'])
def index():
    return render_template('search.html')

@app.route('/static/dashboard_images/<path:filename>')
def serve_dashboard_image(filename):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    image_path = os.path.join(base_dir, 'static/dashboard_images', filename)

    if os.path.exists(image_path):
        return send_file(image_path, mimetype='image/png')
    else:
        return jsonify({"error": f"Image for dashboard LUID '{filename}' not found."}), 404


# Route to handle search queries
@app.route('/search', methods=['POST'])
def search():
    # Get the user's query from the form
    user_input = request.form.get('query')
    if not user_input:
        return jsonify({"error": "No query provided"}), 400
    
    # Query the datasource collection
    results = collection.query(
        query_texts=[user_input], 
        n_results=10 
    )

    # Query the dashboard collection
    results_dash = collection_dash.query(
        query_texts=[user_input], 
        n_results=10 
    )

    # Process datasource results
    metadatas = results['metadatas']
    distances = results['distances']

    datasource_data = []

    for meta_list, dist_list in zip(metadatas, distances):
        for metadata, distance in zip(meta_list, dist_list):
            datasource_data.append({
                'type': 'datasource',
                'name': metadata.get('name', 'N/A'),
                'luid': 'datasource',
                'url': metadata.get('url', 'N/A'),
                'isCertified': metadata.get('isCertified', 'N/A'),
                'updatedAt': metadata.get('updatedAt', 'N/A'),
                'distance': distance
            })

    # Process dashboard results
    metadatas_dash = results_dash['metadatas']
    distances_dash = results_dash['distances']

    dashboard_data = []

    for meta_list, dist_list in zip(metadatas_dash, distances_dash):
        for metadata, distance in zip(meta_list, dist_list):
            dashboard_data.append({
                'type': 'dashboard',
                'name': metadata.get('dashboard_name', 'N/A'),
                'luid': metadata.get('dashboard_luid', 'N/A'),
                'sheet_name': metadata.get('sheet_name', 'N/A'),
                'workbook_luid': metadata.get('workbook_luid', 'N/A'),
                'distance': distance
            })

    # Aggregate dashboard data if needed
    aggregated_dashboards = {}

    for item in dashboard_data:
        name = item['name']
        distance = item['distance']

        if name not in aggregated_dashboards:
            aggregated_dashboards[name] = item
        else:
            # Update the minimum distance
            if distance < aggregated_dashboards[name]['distance']:
                aggregated_dashboards[name]['distance'] = distance

    # Convert aggregated dashboards to a list
    dashboard_data = list(aggregated_dashboards.values())

    # Combine both lists
    combined_results = datasource_data + dashboard_data

    # Sort the combined results by 'distance' in ascending order
    sorted_results = sorted(combined_results, key=lambda x: x['distance'])

    # Render the results template
    return render_template('results.html', results=sorted_results, query=user_input)

    # # Perform the query
    # results = collection.query(
    #     query_texts=[user_input], 
    #     n_results=10 
    # )

    # results_dash = collection_dash.query(
    #     query_texts=[user_input], 
    #     n_results=10 
    # )

    # metadatas = results['metadatas']
    # distances = results['distances']

    # # Initialize an empty list to store extracted data
    # extracted_data = []

    # for meta_list, dist_list in zip(metadatas, distances):
    #     for metadata, distance in zip(meta_list, dist_list):
    #         name = metadata.get('name', 'N/A')
    #         url = metadata.get('url', 'N/A')
    #         luid = metadata.get('luid', 'N/A')
    #         isCertified = metadata.get('isCertified', 'N/A')
    #         updatedAt = metadata.get('updatedAt', 'N/A')
            
    #         # Append the extracted data to the list, including 'distance'
    #         extracted_data.append({
    #             'name': name,
    #             'url': url,
    #             'dashboard_luid': 'datasource',
    #             'isCertified': isCertified,
    #             'updatedAt': updatedAt,
    #             'distance': distance
    #         })

    # # Render the results template
    # return render_template('results.html', results=extracted_data, query=user_input)

# Run the Flask app
if __name__ == '__main__':
    app.run(debug=True)
