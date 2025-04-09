#!/usr/bin/env python

import os
import json
import pandas as pd
import requests
import argparse
import tempfile
from dotenv import load_dotenv
from experimental.utilities.similar_datasources import (
    compute_pairwise_similarities,
    write_similarities_to_csv,
    export_vector_db_metadata_to_csv,
    export_combined_to_json,
    transform_json_to_dataframe,
)
from experimental.utilities.setup_local_vector_db import generate_tableau_auth_token
import http.server
import socketserver

# Load environment variables (Tableau creds, OpenAI API key, etc.)
load_dotenv()

# Read Tableau authentication config from environment
tableau_server   = 'https://' + os.getenv('TABLEAU_SRV_DOMAIN')   
tableau_site     = os.getenv('SRV_SITE_NAME')        
tableau_user     = os.getenv('TABLEAU_SRV_USER')     

# Credentials for generating auth token via connnected app
tableau_jwt_client_id    = os.getenv('TABLEAU_SRV_JWT_CLIENT_ID')
tableau_jwt_secret_id    = os.getenv('TABLEAU_SRV_JWT_SECRET_ID')
tableau_jwt_secret = os.getenv('TABLEAU_SRV_JWT_SECRET')
tableau_api_version  = os.getenv('TABLEAU_SRV_API') 

def get_similar_datasources_query() -> str:
    """
    Generate GraphQL query for retrieving published datasources metadata.
    
    Returns:
        GraphQL query string.
    """
    query = """
    query ConnectedWorkbooks {
        tableauSites(filter: { name: "Demonstration" }) {
            name
            luid
            publishedDatasources {
                id
                luid
                uri
                name
                createdAt
                updatedAt
                extractLastUpdateTime
                extractLastRefreshTime
                extractLastIncrementalUpdateTime
                projectName
                fields { 
                    id
                }
                downstreamWorkbooks {
                    id
                } 
            }
        }
    }
    """
    return query



def get_similar_datasources_metadata(api_key: str, domain: str):
    """
    Synchronously query Tableau Metadata API for all datasources.
    
    Args:
        api_key: X-Tableau-Auth token.
        domain: Tableau server domain.
    
    Returns:
        Datasources metadata dictionary.
    """
    full_url = f"{domain}/api/metadata/graphql"
    query = get_similar_datasources_query()
    payload = json.dumps({
        "query": query,
        "variables": {}
    })
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "X-Tableau-Auth": api_key
    }
    response = requests.post(full_url, headers=headers, data=payload)
    response.raise_for_status()  # Raise an exception for bad responses
    dictionary = response.json()
    return dictionary["data"]

def transform_json_to_dataframe(json_obj) -> pd.DataFrame:
    """
    Transform JSON object of datasources metadata into a pandas DataFrame.
    
    Args:
        json_obj: JSON object with datasource metadata.
    
    Returns:
        pandas DataFrame with columns:
            - luid
            - name
            - createdAt
            - updatedAt
            - extractLastUpdateTime
            - extractLastRefreshTime
            - extractLastIncrementalUpdateTime
            - number_of_columns (count of fields)
            - number_of_workbooks (count of downstreamWorkbooks)
    """
    output = []
    for site in json_obj.get("tableauSites", []):
        for ds in site.get("publishedDatasources", []):
            transformed_ds = {
                "luid": ds.get("luid"),
                "name": ds.get("name"),
                "createdAt": ds.get("createdAt"),
                "updatedAt": ds.get("updatedAt"),
                "extractLastUpdateTime": ds.get("extractLastUpdateTime"),
                "extractLastRefreshTime": ds.get("extractLastRefreshTime"),
                "extractLastIncrementalUpdateTime": ds.get("extractLastIncrementalUpdateTime"),
                "number_of_columns": len(ds.get("fields", [])),
                "number_of_workbooks": len(ds.get("downstreamWorkbooks", []))
            }
            output.append(transformed_ds)
    return pd.DataFrame(output)

def create_similarities_report_server():
    # Load environment variables (Tableau creds, OpenAI API key, etc.)
    load_dotenv()

    # Read Tableau authentication config from environment
    tableau_server   = 'https://' + os.getenv('TABLEAU_SRV_DOMAIN')   
    tableau_site     = os.getenv('SRV_SITE_NAME')        
    tableau_user     = os.getenv('TABLEAU_SRV_USER')     

    # Credentials for generating auth token via connnected app
    tableau_jwt_client_id    = os.getenv('TABLEAU_SRV_JWT_CLIENT_ID')
    tableau_jwt_secret_id    = os.getenv('TABLEAU_SRV_JWT_SECRET_ID')
    tableau_jwt_secret = os.getenv('TABLEAU_SRV_JWT_SECRET')
    tableau_api_version  = os.getenv('TABLEAU_SRV_API') 

    # Define the output directory where the final JSON file will be saved.
    OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "ui_templates")
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    COMBINED_JSON = os.path.join(OUTPUT_DIR, "similarities.json")

    # Use a temporary directory for intermediate files
    with tempfile.TemporaryDirectory() as temp_dir:
        SIMILARITIES_CSV = os.path.join(temp_dir, "similarities.csv")
        VECTOR_CSV = os.path.join(temp_dir, "vector_db_export.csv")

        # -------------------------------
        # Vector Database Processing
        # -------------------------------
        tableau_site_val = os.getenv('SITE_NAME', 'default_site')
        COLLECTION_NAME = f"{tableau_site_val}_tableau_datasource_vector_search"
        DB_PATH = "vector_db"  # Path to your Chroma vector database

        try:
            # Compute pairwise similarities and write results to the temporary CSV file
            results = compute_pairwise_similarities(
                collection_name=COLLECTION_NAME,
                db_path=DB_PATH,
                top_k=5
            )
            write_similarities_to_csv(results, SIMILARITIES_CSV)
            print(f"Temporary CSV file '{SIMILARITIES_CSV}' created with the similarity data.")
        except ValueError as e:
            print("Error computing similarities:", e)
            return

        # Export vector database metadata to a temporary CSV file
        export_vector_db_metadata_to_csv(
            collection_name=COLLECTION_NAME,
            db_path=DB_PATH,
            output_csv=VECTOR_CSV
        )

        # -------------------------------
        # Tableau Metadata API Query
        # -------------------------------
        auth_token = generate_tableau_auth_token(
            jwt_client_id=tableau_jwt_client_id,
            jwt_secret_id=tableau_jwt_secret_id,
            jwt_secret=tableau_jwt_secret,
            tableau_server=tableau_server,
            tableau_site=tableau_site,
            tableau_user=tableau_user,
            tableau_api_version=tableau_api_version
        )
        api_key = auth_token
        domain = tableau_server
        if api_key and domain:
            print("Querying Tableau Metadata API for datasources metadata...")
            metadata_json = get_similar_datasources_metadata(api_key, domain)

            df = transform_json_to_dataframe(metadata_json)
            df = df[['luid', 'number_of_columns', 'number_of_workbooks']]
            vec_df = pd.read_csv(VECTOR_CSV)
            vec_df = pd.merge(vec_df, df, how='left', left_on='id', right_on='luid')
            vec_df.to_csv(VECTOR_CSV, index=False)
        else:
            print("TABLEAU_API_KEY and/or TABLEAU_DOMAIN environment variables not set.")

        # -------------------------------
        # Combine CSV files into a single JSON report saved in the OUTPUT_DIR
        # -------------------------------
        export_combined_to_json(
            vector_csv=VECTOR_CSV,
            similarities_csv=SIMILARITIES_CSV,
            output_filename=COMBINED_JSON
        )
        print(f"Combined JSON report saved to '{COMBINED_JSON}'.")

def main():
    # Parse command-line arguments
    parser = argparse.ArgumentParser(
        description="Generate similarities report and optionally serve the output directory."
    )
    parser.add_argument(
        "--serve",
        action="store_true",
        help="After generating the report, serve the output directory via a local HTTP server."
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Port to use for the HTTP server (default is 8000)."
    )
    args = parser.parse_args()

    # Define the output directory where the final JSON file will be saved.
    OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "ui_templates")
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    COMBINED_JSON = os.path.join(OUTPUT_DIR, "similarities.json")

    # Use a temporary directory for intermediate files
    with tempfile.TemporaryDirectory() as temp_dir:
        SIMILARITIES_CSV = os.path.join(temp_dir, "similarities.csv")
        VECTOR_CSV = os.path.join(temp_dir, "vector_db_export.csv")

        # -------------------------------
        # Vector Database Processing
        # -------------------------------
        tableau_site_val = os.getenv('SITE_NAME', 'default_site')
        COLLECTION_NAME = f"{tableau_site_val}_tableau_datasource_vector_search"
        DB_PATH = "vector_db"  # Path to your Chroma vector database

        try:
            # Compute pairwise similarities and write results to the temporary CSV file
            results = compute_pairwise_similarities(
                collection_name=COLLECTION_NAME,
                db_path=DB_PATH,
                top_k=5
            )
            write_similarities_to_csv(results, SIMILARITIES_CSV)
            print(f"Temporary CSV file '{SIMILARITIES_CSV}' created with the similarity data.")
        except ValueError as e:
            print("Error computing similarities:", e)
            return

        # Export vector database metadata to a temporary CSV file
        export_vector_db_metadata_to_csv(
            collection_name=COLLECTION_NAME,
            db_path=DB_PATH,
            output_csv=VECTOR_CSV
        )

        # -------------------------------
        # Tableau Metadata API Query
        # -------------------------------
        auth_token = generate_tableau_auth_token(
            jwt_client_id=tableau_jwt_client_id,
            jwt_secret_id=tableau_jwt_secret_id,
            jwt_secret=tableau_jwt_secret,
            tableau_server=tableau_server,
            tableau_site=tableau_site,
            tableau_user=tableau_user,
            tableau_api_version=tableau_api_version
        )
        api_key = auth_token
        domain = tableau_server
        if api_key and domain:
            print("Querying Tableau Metadata API for datasources metadata...")
            metadata_json = get_similar_datasources_metadata(api_key, domain)

            df = transform_json_to_dataframe(metadata_json)
            df = df[['luid', 'number_of_columns', 'number_of_workbooks']]
            vec_df = pd.read_csv(VECTOR_CSV)
            vec_df = pd.merge(vec_df, df, how='left', left_on='id', right_on='luid')
            vec_df.to_csv(VECTOR_CSV, index=False)
        else:
            print("TABLEAU_API_KEY and/or TABLEAU_DOMAIN environment variables not set.")

        # -------------------------------
        # Combine CSV files into a single JSON report saved in the OUTPUT_DIR
        # -------------------------------
        export_combined_to_json(
            vector_csv=VECTOR_CSV,
            similarities_csv=SIMILARITIES_CSV,
            output_filename=COMBINED_JSON
        )
        print(f"Combined JSON report saved to '{COMBINED_JSON}'.")

    # -------------------------------
    # Optionally serve the report
    # -------------------------------
    if args.serve:
        os.chdir(OUTPUT_DIR)
        port = args.port
        handler = http.server.SimpleHTTPRequestHandler
        with socketserver.TCPServer(("", port), handler) as httpd:
            print(f"Serving '{OUTPUT_DIR}' at http://localhost:{port}")
            try:
                httpd.serve_forever()
            except KeyboardInterrupt:
                print("Server interrupted. Exiting...")

if __name__ == '__main__':
    main()
