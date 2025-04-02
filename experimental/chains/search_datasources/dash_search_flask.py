from modules import graphql, vectorstore
from flask import Flask, request, jsonify, render_template, send_file
import json 
import os
server, auth = graphql.get_tableau_client()
tab_dashboards = graphql.fetch_dashboard_data(server, auth)

# Initialize Flask app
app = Flask(__name__)

print('Dashboards fetched')

collection = vectorstore.setup_vector_db(datasources = tab_dashboards, collection_name = 'dash_RAG', mode = 'recreate', debug = True)
#collection = vectorstore.setup_vector_db(datasources = tab_dashboards, collection_name = 'dash_RAG', debug = True)

print('Vector store created')

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

    # Perform the query
    results = collection.query(
        query_texts=[user_input],
        n_results=10  
    )

    metadatas = results['metadatas']
    distances = results['distances']

    # Initialize an empty list to store extracted data
    extracted_data = []
    seen_dashboard_luids = set()

    with server.auth.sign_in(auth):
        for meta_list, dist_list in zip(metadatas, distances):
            for metadata, distance in zip(meta_list, dist_list):
                dashboard_name = metadata.get('dashboard_name', 'N/A')
                path = metadata.get('dashboard_path', 'N/A')
                sheet_name = metadata.get('sheet_name', 'N/A')
                workbook_name = metadata.get('workbook_name', 'N/A')
                dashboard_luid = metadata.get('dashboard_luid')

                graphql.save_dashboard_image(server, dashboard_luid)
                
                if dashboard_luid and dashboard_luid not in seen_dashboard_luids:
                    seen_dashboard_luids.add(dashboard_luid)
                   
                    # Append the extracted data to the list, including 'distance'
                    extracted_data.append({
                        'dashboard_name': dashboard_name,
                        'dashboard_luid': dashboard_luid,
                        'path': path,
                        'sheet_name': sheet_name,
                        'workbook_name': workbook_name,
                        'distance': distance
                    })


    for item in extracted_data:
        print(f"Sheet Name: {item['sheet_name']}")
        print(f"Workbook Name: {item['workbook_name']}")
        print(f"Dashboard Name: {item['dashboard_name']}")
        print(f"Dashboard LUID: {item['dashboard_luid']}")
        print(f"Path: {item['path']}")

        print(f"Vector distance: {item['distance']}")
        print("-" * 40)
    
    # Render the results template
    return render_template('results.html', results=extracted_data, query=user_input)

# Run the Flask app
if __name__ == '__main__':
    app.run(debug=True)

