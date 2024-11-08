import chromadb
from openai import OpenAI
from dotenv import load_dotenv
import os
import chromadb.utils.embedding_functions as embedding_functions
from typing import Optional, Union, List, Dict, Any, Callable
from chromadb.errors import InvalidCollectionException
import json

def load_vector_db(
    collection_name: str,
    embedding_function: Optional[Any] = None,
    debug: bool = False
) -> Optional[chromadb.api.models.Collection.Collection]:
    """
    Load an existing ChromaDB vector collection by name without providing data.

    Args:
        collection_name: Name of the collection to load.
        embedding_function: Optional embedding function.
        debug: Whether to print debug information.

    Returns:
        The ChromaDB collection object if found; otherwise, None.
    """
    # Load environment variables
    load_dotenv()

    # Set default embedding function if none provided
    if embedding_function is None:
        embedding_function = embedding_functions.OpenAIEmbeddingFunction(
            api_key=os.getenv('OPENAI_API_KEY'),
            model_name="text-embedding-ada-002"  # Update with your preferred model
        )

    # Initialize ChromaDB client
    chroma_client = chromadb.PersistentClient(path="data")

    # Attempt to retrieve the existing collection
    try:
        collection = chroma_client.get_collection(
            name=collection_name,
            embedding_function=embedding_function
        )
        if debug:
            print(f"Successfully loaded collection: {collection_name}")
        return collection

    except InvalidCollectionException:
        print(f"Collection '{collection_name}' does not exist.")
        return None

def prepare_documents_for_chroma(
    datasources: List[Dict[Any, Any]], 
    debug: bool = False,
    text_field: str = 'dashboard_overview',
    id_field: str = 'id'
) -> tuple[List[str], List[str], List[Dict[str, Any]]]:
    """
    Prepare documents for Chroma DB ingestion with flexible field selection.
    
    Args:
        datasources: List of dictionaries containing the data to be embedded
        debug: Whether to print debug information
        text_field: Field to use for embedding text
        id_field: Field to use for unique document ID
    
    Returns:
        Tuple of (documents, ids, metadatas)
    """
    # Helper function to convert values to strings
    def convert_to_string(value):
        if isinstance(value, dict):
            return str(value)
        elif isinstance(value, list):
            return ', '.join(map(str, value))
        else:
            return str(value)
    
    documents = []
    ids = []
    metadatas = []
    
    for idx, datasource in enumerate(datasources):
        try:
            # Extract the text to embed
            text_to_embed = datasource.get(text_field, '')
            
            if debug:
                print(f"\nProcessing document {idx + 1}/{len(datasources)}")
                if idx == 0:  # Only show detailed debug for first document
                    print(f"Text length: {len(str(text_to_embed))}")
                    print("First 100 chars of text:", str(text_to_embed)[:100])
            
            if not text_to_embed:
                print(f"Warning: Empty {text_field} for document {idx + 1}")
                continue
            
            # Extract the unique identifier
            unique_id = str(datasource.get(id_field, f'doc_{idx}'))
            
            # Prepare metadata (exclude text and id fields)
            metadata = {k: v for k, v in datasource.items() 
                       if k not in [text_field, id_field]}
            
            # Remove any nested data structures from metadata
            metadata = {k: convert_to_string(v) for k, v in metadata.items() 
                       if isinstance(v, (str, int, float, bool, dict, list))}
            
            documents.append(text_to_embed)
            ids.append(unique_id)
            metadatas.append(metadata)
            
        except Exception as e:
            print(f"Error processing document {idx + 1}: {str(e)}")
            print(f"Problematic datasource: {json.dumps(datasource, indent=2)}")
            raise
    
    return documents, ids, metadatas

def setup_vector_db(
    datasources: List[Dict[Any, Any]],
    collection_name: Optional[str] = None,
    embedding_function: Optional[Any] = None,
    mode: str = 'use existing if available',
    debug: bool = False,
    batch_size: int = 1000,
    prepare_func: Optional[Callable] = None
) -> chromadb.Collection:
    """
    Setup a ChromaDB vector database with flexible document preparation.
    
    Args:
        datasources: List of dictionaries containing the data to be embedded
        collection_name: Name of the collection 
        embedding_function: Optional embedding function
        mode: 'use existing if available' or 'recreate'
        debug: Whether to print debug information
        batch_size: Number of documents to process in each batch
        prepare_func: Optional custom function to prepare documents for Chroma
    
    Returns:
        ChromaDB collection object
    """
    # Load environment variables
    load_dotenv()
    
    if debug:
        print("\n=== Debug Information ===")
        print(f"Total number of datasources: {len(datasources)}")
        print(f"Will process in batches of {batch_size}")
        print(f"Sample of first datasource keys: {list(datasources[0].keys()) if datasources else 'No datasources'}")
    
    # Set default collection name if none provided
    if collection_name is None:
        collection_name = os.getenv('SITE_NAME') + '_tableau_datasource_RAG_search'
    
    # Set default embedding function if none provided
    if embedding_function is None:
        openai_client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        embedding_function = embedding_functions.OpenAIEmbeddingFunction(
            api_key=os.getenv('OPENAI_API_KEY'),
            model_name="text-embedding-3-small"
        )
    
    # Use default preparation function if none provided
    if prepare_func is None:
        prepare_func = prepare_documents_for_chroma
    
    # Initialize ChromaDB client
    chroma_client = chromadb.PersistentClient(path="data")
    
    # Function to create new collection with data
    def create_new_collection():
        print(f"\nCreating new collection: {collection_name}")
        total_documents = 0
        
        # Create collection
        new_collection = chroma_client.create_collection(
            name=collection_name,
            embedding_function=embedding_function
        )
        
        # Process in batches
        for batch_start in range(0, len(datasources), batch_size):
            batch_end = min(batch_start + batch_size, len(datasources))
            batch = datasources[batch_start:batch_end]
            
            print(f"\nProcessing batch {(batch_start // batch_size) + 1}/{(len(datasources) + batch_size - 1) // batch_size}")
            
            # Use the custom or default preparation function
            documents, ids, metadatas = prepare_func(
                batch, 
                debug=debug, 
                # You can pass additional parameters if needed
            )
            
            if documents:  # Only add if we have documents in this batch
                new_collection.add(
                    documents=documents,
                    metadatas=metadatas,
                    ids=ids
                )
                total_documents += len(documents)
                print(f"Added {len(documents)} documents in this batch. Total documents so far: {total_documents}")
        
        print(f"\nFinished processing all batches. Total documents added: {total_documents}")
        return new_collection
    
    # Handle collection creation/retrieval based on mode
    if mode.lower() == 'recreate':
        if collection_name in [col.name for col in chroma_client.list_collections()]:
            chroma_client.delete_collection(name=collection_name)
            print(f"Deleted existing collection: {collection_name}")
        
        collection = create_new_collection()
        
    else:  # 'use existing if available'
        try:
            collection = chroma_client.get_collection(
                name=collection_name,
                embedding_function=embedding_function
            )
            print(f"Using existing collection: {collection_name}")
            
        except InvalidCollectionException:
            collection = create_new_collection()
    
    return collection