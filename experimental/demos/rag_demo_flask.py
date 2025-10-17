from flask import Flask, request, jsonify, render_template
from modules import graphql
import chromadb
import numpy as np
from openai import OpenAI
from dotenv import load_dotenv
import os
import sys
import chromadb.utils.embedding_functions as embedding_functions

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from experimental.utilities.security import (
    require_api_key,
    rate_limit,
    check_budget,
    log_request,
    validate_environment,
    usage_tracker,
    rate_limiter,
    require_english
)
from experimental.utilities.ip_blocker import check_ip_blocked, ip_blocker

# Load environment variables
load_dotenv()

# Validate environment and security settings on startup
try:
    validate_environment()
except EnvironmentError as e:
    print(f"❌ Environment validation failed: {e}")
    print("Please set required environment variables before starting the application.")
    sys.exit(1)

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

# Health check endpoint (no auth required)
@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "healthy", "service": "tableau-rag-search"}), 200

# Route to display the search form
@app.route('/', methods=['GET'])
@log_request()
def index():
    return render_template('search.html')

# Route to handle search queries
@app.route('/search', methods=['POST'])
@check_ip_blocked()  # Check IP blocklist first
@log_request()
@require_english()  # Block non-English requests
@require_api_key
@rate_limit(tokens_required=2)  # Search uses 2 tokens (more expensive)
@check_budget()
def search():
    # Get the user's query from the form
    user_input = request.form.get('query')
    if not user_input:
        return jsonify({"error": "No query provided"}), 400

    # Input validation
    if len(user_input) > 500:
        return jsonify({"error": "Query too long. Maximum 500 characters."}), 400

    # Track usage (estimate ~100 tokens for embedding)
    identifier = rate_limiter._get_identifier(request)
    usage_tracker.track_usage(
        identifier=identifier,
        model='text-embedding-3-small',
        input_tokens=len(user_input.split()) * 2,  # Rough estimate
        output_tokens=0
    )

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

# Admin route to view security stats (protect this in production!)
@app.route('/admin/stats', methods=['GET'])
@require_api_key
def admin_stats():
    """Get security and usage statistics."""
    return jsonify({
        'ip_blocking': ip_blocker.get_stats(),
        'blocked_ips': ip_blocker.get_blocked_ips()[:10],  # Show first 10
        'rate_limiting': {
            'per_minute': rate_limiter.max_requests_per_minute,
            'per_hour': rate_limiter.max_requests_per_hour,
            'per_day': rate_limiter.max_requests_per_day
        },
        'budget': {
            'hourly_usd': usage_tracker.hourly_budget,
            'daily_usd': usage_tracker.daily_budget
        }
    }), 200

# Error handler for rate limits
@app.errorhandler(429)
def ratelimit_handler(e):
    """Custom error handler for rate limit exceeded."""
    ip = request.remote_addr
    ip_blocker.record_violation(ip, "rate_limit")
    return jsonify({
        "error": "Rate limit exceeded",
        "message": str(e),
        "retry_after": "60 seconds"
    }), 429

# Error handler for forbidden (blocked IP)
@app.errorhandler(403)
def forbidden_handler(e):
    return jsonify({
        "error": "Access forbidden",
        "message": "Your access has been restricted"
    }), 403

# Run the Flask app
if __name__ == '__main__':
    print("\n" + "="*60)
    print("🚀 Tableau LangChain RAG Demo - SECURED")
    print("="*60)
    print("Security features enabled:")
    print(f"  ✅ API Authentication: {'ENABLED' if len(os.getenv('ALLOWED_API_KEYS', '').split(',')) > 1 else 'DISABLED (Dev Mode)'}")
    print(f"  ✅ Rate Limiting: {rate_limiter.max_requests_per_minute}/min")
    print(f"  ✅ Budget Protection: ${usage_tracker.hourly_budget}/hour, ${usage_tracker.daily_budget}/day")
    print(f"  ✅ IP Blocking: {len(ip_blocker.get_blocked_ips())} IPs blocked")
    print(f"  ✅ Request Logging: api_usage.log")
    print("\nEndpoints:")
    print("  GET  /health       - Health check (no auth)")
    print("  GET  /             - Search form")
    print("  POST /search       - Perform search (requires X-API-Key)")
    print("  GET  /admin/stats  - Security stats (requires X-API-Key)")
    print("\n" + "="*60 + "\n")

    app.run(debug=True)
