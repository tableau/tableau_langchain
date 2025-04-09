import os
import time
from flask import Flask, request, jsonify, render_template, send_file, redirect, url_for
from dotenv import load_dotenv
from experimental.utilities.setup_local_vector_db import query_tableau_vector_db
from experimental.utilities.similar_datasources import (
    compute_pairwise_similarities,
    write_similarities_to_csv,
    export_vector_db_metadata_to_csv,
    export_combined_to_json
)
from experimental.demos.server_similar_datasources import create_similarities_report_server
import tempfile
import pandas as pd

# Load environment variables
load_dotenv()

# Configuration
tableau_site = os.getenv('SITE_NAME')
collection_name = f"{tableau_site}_tableau_datasource_vector_search"

# Setup directories:
# Previously, you had a separate 'html' folder for D3 content.
# Now, everything is consolidated into the ui_templates folder.
base_dir = os.path.dirname(os.path.abspath(__file__))
template_dir = os.path.join(base_dir, 'ui_templates')
static_dir = os.path.join(template_dir, 'static')
# Since everything is in ui_templates, we assign d3_dir to the same location.
d3_dir = template_dir

# Initialize Flask app with the new template & static folders
app = Flask(__name__, 
           template_folder=template_dir, 
           static_folder=static_dir)

# Serve the similarities.json file from the ui_templates folder.
@app.route('/similarities.json')
def serve_similarities_json():
    response = send_file(os.path.join(d3_dir, 'similarities.json'))
    # Optional: disable caching to always get the latest version.
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response

# Home route (redirects to search page)
@app.route('/')
def index():
    return render_template('search.html')

# Search form route
@app.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        user_input = request.form.get('query')
        if not user_input:
            return jsonify({"error": "No query provided"}), 400

        results = query_tableau_vector_db(
            query_text=user_input,
            collection_name=collection_name,
            n_results=10,
            debug=False
        )

        extracted_data = []
        num_items = len(results['luid'])
        for i in range(num_items):
            metadata = results['metadatas'][i]
            extracted_data.append({
                'name': metadata.get('name', 'N/A'),
                'has_active_warning': metadata.get('has_active_warning', 'N/A'),
                'dashboard_luid': results['luid'][i],
                'url': metadata.get('url', 'N/A'), 
                'is_certified': metadata.get('is_certified', 'N/A'),
                'project_name': metadata.get('project_name', 'N/A'),
                'distance': results['distances'][i]
            })

        return render_template('results.html', results=extracted_data, query=user_input)
    
    return render_template('search.html')

# D3 visualization route
@app.route('/similar_datasources')
def similar_datasources():
    # Generate similarities.json in the ui_templates folder.
    output_dir = d3_dir
    os.makedirs(output_dir, exist_ok=True)
    combined_json = os.path.join(output_dir, "similarities.json")

    # Generate the similarities JSON if it does not exist or is outdated.
    if not os.path.exists(combined_json) or os.path.getmtime(combined_json) < (time.time() - 3600):
        create_similarities_report_server()
        
    # Render the D3 visualization template.
    return render_template('d3_visualization.html')

# Error handlers
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def server_error(e):
    return render_template('500.html'), 500

if __name__ == '__main__':
    app.run(debug=True)
