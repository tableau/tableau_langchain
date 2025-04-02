import os
import chromadb
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv

from chromadb.utils import embedding_functions
#import chromadb.embedding_functions as embedding_functions
from chromadb.api.models.Collection import Collection
from chromadb.errors import InvalidCollectionException
from chromadb.config import Settings


def format_datasources_for_rag(
    datasources_data: Dict[str, Any], 
    debug: bool = False
) -> List[Dict[str, Any]]:
    """
    Format Tableau datasources for RAG (Retrieval-Augmented Generation) purposes
    
    :param datasources_data: Raw GraphQL response data from get_datasources_metadata
    :param debug: Enable debug logging
    :return: List of formatted datasource dictionaries optimized for RAG search
    """
    if not datasources_data or not isinstance(datasources_data, dict):
        raise ValueError("Invalid datasources data provided.")
    
    formatted_datasources = []
    
    # Extract publishedDatasources from the response
    published_datasources = datasources_data.get('publishedDatasources', [])
    
    if debug:
        print(f"Total datasources to process: {len(published_datasources)}")
    
    for datasource in published_datasources:
        # Skip datasources without a name
        datasource_name = datasource.get('name')
        if not datasource_name:
            continue
        
        # Process fields for RAG
        fields = datasource.get('fields', [])
        field_entries = []
        
        for field in fields:
            name = field.get('name', '')
            description = field.get('description', '')
            
            # Format field entry with description if available
            if description:
                # Remove newlines and extra spaces
                description = ' '.join(description.split())
                field_entry = f"- {name}: [{description}]"
            else:
                field_entry = f"- {name}"
            
            field_entries.append(field_entry)
        
        # Combine field entries
        concatenated_field_entries = '\n'.join(field_entries)
        
        # Create dashboard overview for RAG
        dashboard_overview = f"""Datasource: {datasource_name}
{datasource.get('description', 'No description available')}
Project: {datasource.get('projectName', 'No project specified')}

Datasource Columns:
{concatenated_field_entries}"""
        
        # Prepare formatted datasource dictionary
        formatted_datasource = {
            'dashboard_overview': dashboard_overview,
            'name': datasource_name,
            'luid': datasource.get('luid'),
            'description': datasource.get('description', 'No description'),
            'project_name': datasource.get('projectName'),
            'is_certified': datasource.get('isCertified'),
            'last_refresh_time': datasource.get('extractLastRefreshTime'),
            'last_incremental_update_time': datasource.get('extractLastIncrementalUpdateTime'),
            'last_update_time': datasource.get('extractLastUpdateTime'),
            'has_active_warning': datasource.get('hasActiveWarning'),
        }
        
        # Add owner information
        owner = datasource.get('owner', {})
        formatted_datasource.update({
            'owner_username': owner.get('username'),
            'owner_name': owner.get('name'),
            'owner_email': owner.get('email')
        })
        
        formatted_datasources.append(formatted_datasource)
    
    if debug:
        print(f"Processed {len(formatted_datasources)} datasources for RAG")
    
    return formatted_datasources


def create_datasources_vector_db(
    datasources: List[Dict[str, Any]], 
    debug: bool = False,
    collection_name: Optional[str] = None
) -> Collection:
    """
    Create a ChromaDB vector database for Tableau datasources
    
    :param datasources: List of formatted datasource dictionaries
    :param debug: Enable debug logging
    :param collection_name: Optional custom collection name
    :return: ChromaDB Collection object
    """
    # Load environment variables
    load_dotenv()
    
    # Set default collection name if none provided
    if collection_name is None:
        site_name = os.getenv('SITE_NAME', 'tableau')
        collection_name = f"{site_name}_tableau_datasource_vector_search"
    
    # Set up embedding function
    embedding_function = embedding_functions.OpenAIEmbeddingFunction(
        api_key=os.getenv('OPENAI_API_KEY'),
        model_name="text-embedding-ada-002"
    )
    
    # Initialize ChromaDB client
    chroma_client = chromadb.PersistentClient(
        path="vector_db",
        settings=Settings(
            persist_directory="vector_db"
        )
    )

    # Delete existing collection if it exists
    collection_names = chroma_client.list_collections()
    if collection_name in collection_names:
        chroma_client.delete_collection(name=collection_name)
        if debug:
            print(f"Deleted existing collection: {collection_name}")

    
    # Create new collection
    collection = chroma_client.create_collection(
        name=collection_name,
        embedding_function=embedding_function
    )
    
    # Prepare documents for Chroma
    documents = []
    ids = []
    metadatas = []
    
    for idx, datasource in enumerate(datasources):
        text_to_embed = datasource.get('dashboard_overview', '')
        unique_id = str(datasource.get('luid', f'doc_{idx}'))
        
        # Prepare metadata with only non-None values
        metadata = {}
        for k, v in datasource.items():
            if k not in ['dashboard_overview', 'luid']:
                # Convert None to empty string, keep other values
                if v is not None:
                    # Convert complex types to strings
                    if isinstance(v, (list, dict)):
                        metadata[k] = str(v)
                    else:
                        metadata[k] = v
        
        documents.append(text_to_embed)
        ids.append(unique_id)
        metadatas.append(metadata)
        
        # Debug print to check metadata
        if debug and idx == 0:
            print("First document metadata:")
            print(metadata)
    
    # Add documents to the collection
    if documents:
        collection.add(
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )
        
        if debug:
            print(f"Added {len(documents)} documents to the collection")
    
    return collection


def query_datasources_vector_db(
    query_text: str, 
    collection_name: str,
    n_results: int = 3,
    debug: bool = False
) -> Optional[Dict[str, Any]]:
    """
    Query the local Tableau datasources vector database
    
    :param query_text: Text to search for
    :param collection_name: The name of the collection to query
    :param n_results: Number of results to return
    :param debug: Enable debug logging
    :return: Dictionary of search results or None if database not found
    """
    # Load environment variables
    load_dotenv()
    
    # Set up embedding function
    embedding_function = embedding_functions.OpenAIEmbeddingFunction(
        api_key=os.getenv('OPENAI_API_KEY'),
        model_name="text-embedding-ada-002"
    )
    
    # Initialize ChromaDB client
    chroma_client = chromadb.PersistentClient(path="vector_db")
    
    try:
        # Attempt to get the collection
        collection = chroma_client.get_collection(
            name=collection_name,
            embedding_function=embedding_function
        )
    except InvalidCollectionException:
        if debug:
            print(f"No vector database found for collection: {collection_name}")
        return None
    
    # Perform the query
    results = collection.query(
        query_texts=[query_text],
        n_results=n_results
    )
    
    # Process and return results
    processed_results = {
        'luid': results['ids'][0],
        'documents': results['documents'][0],
        'distances': results['distances'][0],
        'metadatas': results['metadatas'][0]
    }
    
    if debug:
        print("\n=== Vector Search Results ===")
        for i, (doc, score, metadata) in enumerate(zip(
            processed_results['luid'], 
            processed_results['documents'], 
            processed_results['distances'], 
            processed_results['metadatas']
        ), 1):
            print(f"\nResult {i} (Similarity Score: {score}):")
            print(f"Datasource Name: {metadata.get('name', 'Unknown')}")
            print("Excerpt:", doc[:300] + "...")
    
    return processed_results['luid']