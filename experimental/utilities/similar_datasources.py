import chromadb
import numpy as np
import csv
import ast
import json
import pandas as pd
from typing import Dict, List, Tuple
import os
from dotenv import load_dotenv
load_dotenv()

import requests  # Added for HTTP requests in metadata query

def compute_pairwise_similarities(
    collection_name: str,
    db_path: str = None,
    batch_size: int = None,
    top_k: int = None
) -> Dict[str, List[Tuple[str, float]]]:
    """
    Computes pairwise cosine similarities for all items in a Chroma collection.
    
    Args:
        collection_name: Name of Chroma collection.
        db_path: Path to Chroma database (None for in-memory).
        batch_size: Process in batches to reduce memory (None for single batch).
        top_k: Return only top K matches per item (None for all).
    
    Returns:
        Dictionary with item IDs as keys and a list of tuples as values:
        {item_id: [(similar_id, similarity), ...]}.
    """
    
    # Connect to Chroma
    client = chromadb.PersistentClient(path=db_path) if db_path else chromadb.Client()
    collection = client.get_collection(collection_name)
    
    # Get all embeddings and associated IDs
    result = collection.get(include=["embeddings"])
    embeddings = result["embeddings"]
    ids = result["ids"]
    
    # Check if embeddings is empty
    if embeddings is None or len(embeddings) == 0:
        raise ValueError(f"No embeddings found in collection '{collection_name}'")
    
    # Convert embeddings to NumPy array and normalize them
    emb_matrix = np.array(embeddings, dtype=np.float32)
    norms = np.linalg.norm(emb_matrix, axis=1, keepdims=True)
    normalized_emb = emb_matrix / norms
    
    # Process in batches if specified
    similarities = {}
    total_items = len(ids)
    batch_size = batch_size or total_items
    
    for i in range(0, total_items, batch_size):
        batch = normalized_emb[i:i+batch_size]
        batch_similarities = np.dot(batch, normalized_emb.T)
        
        for idx_in_batch, full_idx in enumerate(range(i, min(i+batch_size, total_items))):
            item_id = ids[full_idx]
            sim_scores = batch_similarities[idx_in_batch]
            
            # Create sorted list of matches (excluding self)
            sorted_indices = np.argsort(-sim_scores)
            matches = [
                (ids[j], float(sim_scores[j])) 
                for j in sorted_indices 
                if j != full_idx
            ]
            
            # Apply top-k filter if specified
            if top_k:
                matches = matches[:top_k]
                
            similarities[item_id] = matches
    
    return similarities

def write_similarities_to_csv(similarities: Dict[str, List[Tuple[str, float]]], filename: str):
    """
    Writes the similarities dictionary to a CSV file with columns:
    source, target, similarity.
    
    Args:
        similarities: Dictionary of similarities.
        filename: Name of the CSV file to write.
    """
    with open(filename, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["source", "target", "similarity"])
        for source, matches in similarities.items():
            for target, similarity in matches:
                writer.writerow([source, target, similarity])

def export_vector_db_metadata_to_csv(
    collection_name: str,
    db_path: str = None,
    output_csv: str = "vector_db_metadata_export.csv"
):
    """
    Exports the Chroma vector database collection metadata to a CSV file.
    Each metadata entry is split into individual columns.
    
    Args:
        collection_name: Name of the Chroma collection.
        db_path: Path to the Chroma database (None for in-memory).
        output_csv: Name of the output CSV file.
    """
    # Connect to Chroma
    client = chromadb.PersistentClient(path=db_path) if db_path else chromadb.Client()
    collection = client.get_collection(collection_name)
    
    # Get metadatas; IDs are returned by default.
    result = collection.get(include=["metadatas"])
    metadatas = result["metadatas"]
    ids = result["ids"]
    
    # Define the expected metadata keys as columns
    metadata_keys = [
        "name",
        "description",
        "has_active_warning",
        "is_certified",
        "last_refresh_time",
        "last_update_time",
        "project_name"
    ]
    
    # Open CSV file for writing
    with open(output_csv, "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        # Write header: id plus each metadata key as a column.
        header = ["id"] + metadata_keys
        writer.writerow(header)
        
        # Process each record
        for idx, item_id in enumerate(ids):
            metadata = metadatas[idx] if metadatas else {}
            # If metadata is a string, convert it to a dictionary.
            if isinstance(metadata, str):
                try:
                    metadata = ast.literal_eval(metadata)
                except Exception:
                    metadata = {}
            # Prepare a row: id followed by each metadata field (use empty string if missing)
            row = [item_id] + [metadata.get(key, "") for key in metadata_keys]
            writer.writerow(row)
    
    print(f"Vector DB metadata exported to '{output_csv}' successfully.")

def export_combined_to_json(
    vector_csv: str,
    similarities_csv: str,
    output_filename: str = "combined_output.json"
):
    """
    Reads the two CSV files (vector DB metadata and similarities), converts them into JSON,
    and combines them into a single JSON file with the following structure:
    
    {
        "nodes": [ ... ],   # Data from the vector DB metadata CSV
        "links": [ ... ]    # Data from the similarities CSV
    }
    
    Args:
        vector_csv: Path to the vector DB metadata CSV file.
        similarities_csv: Path to the similarities CSV file.
        output_filename: Name of the output JSON file.
    """
    # Read CSV files using pandas
    nodes_df = pd.read_csv(vector_csv)
    links_df = pd.read_csv(similarities_csv)
    
    # Convert DataFrames to JSON records (list of dictionaries)
    nodes_json = json.loads(nodes_df.to_json(orient="records"))
    links_json = json.loads(links_df.to_json(orient="records"))
    
    # Combine the JSON objects into one dictionary
    combined_json = {
        "nodes": nodes_json,
        "links": links_json
    }
    
    # Write the combined JSON to a file
    with open(output_filename, 'w') as outfile:
        json.dump(combined_json, outfile, indent=4)
    
    print(f"Combined JSON file created as '{output_filename}'.")

# ============================================================================
# New functions for querying and transforming Tableau Metadata API responses
# ============================================================================

def get_similar_datasources_query() -> str:
    """
    Generate GraphQL query for retrieving published datasources metadata.
    
    Returns:
        GraphQL query string.
    """
    query = """
    query ConnectedWorkbooks {
        tableauSites(filter: { name: "TC25" }) {
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

def get_similar_datasources_metadata(api_key: str, domain: str) -> Dict:
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

def transform_json_to_dataframe(json_obj: Dict) -> pd.DataFrame:
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

