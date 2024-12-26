from typing import Dict, List, Optional, Any

from langgraph.store.memory import InMemoryStore


def set_tableau_credentials(
    store: InMemoryStore,
    tableau_session: str,
    domain: str,
    site: str
) -> None:
    # insert user credentials to authenticate to a Tableau environment
    user_namespace = ("user_data", "credentials")
    credentials_key = "user_credentials"
    store.put(user_namespace, credentials_key, {
        "session": tableau_session,
        "url": domain,
        "site": site
    })

def set_target_datasource(
    store: InMemoryStore,
    luid: Optional[str] = None,
    name: Optional[str] = None,
    description: Optional[str] = None,
) -> None:
    # insert a datasource for VizQL Data Service querying, content recommendation and visual Q&A
    datasource_namespace = ("analytics", "datasource")
    datasource_key = "detail"
    store.put(datasource_namespace, datasource_key, {
        "luid": luid,
        "name": name,
        "description": description
    })

def set_target_workbook(
    store: InMemoryStore,
    luid: Optional[str] = None,
    name: Optional[str] = None,
    description: Optional[str] = None,
    sheets: Optional[List[str]] = None,
    viz_url: Optional[str] = None
) -> None:
    # insert a workbook for writing embeds, content recommendation and visual Q&A
    workbook_namespace = ("analytics", "workbook")
    workbook_key = "detail"
    store.put(workbook_namespace, workbook_key, {
        "luid": luid,
        "name": name,
        "description": description,
        "sheets": sheets,
        "viz_url": viz_url
    })

def set_vector_store(
    store: InMemoryStore,
    topic: str,
    data: Dict[str, Any],
) -> None:
    # insert topical vector stores for RAG tools
    namespace = ("rag", topic)
    key = "vectors"
    store.put(namespace, key, data)

def validate_credentials(credentials: Dict[str, Any]) -> None:
    # Define the required keys
    required_keys = {
        'tableau_credentials': {
            'session',
            'url',
            'site'
        }
    }

    # Check if 'tableau_credentials' is present in the payload
    if 'tableau_credentials' not in credentials:
        raise ValueError("Missing key: 'tableau_credentials'")

    # Check if all required child keys are present
    for key, child_keys in required_keys.items():
        if key in credentials:
            missing_keys = child_keys - credentials[key].keys()
            if missing_keys:
                raise ValueError(f"Missing credentials keys in '{key}': {', '.join(missing_keys)}")

def initialize_memory(memory_inputs: Dict[str, Any]) -> InMemoryStore:
    # initialize a memory store
    memory = InMemoryStore()
    # throws error if Tableau credentials are not available before initializing agent memory
    try:
        validate_credentials(memory_inputs)
    except ValueError as e:
        print(e)
        raise  # Re-raise to propagate error further

    credentials = memory_inputs['tableau_credentials']
    datasource = memory_inputs.get('datasource')
    workbook = memory_inputs.get('workbook')
    rag = memory_inputs.get('rag')

    if credentials:
        # store tableau credentials to access the environment with tools
        set_tableau_credentials(
            store=memory,
            tableau_session=credentials['session'],
            domain=credentials['url'],
            site=credentials['site']
        )

    if datasource:
        # store datasource for VDS querying, content recommendations and Q&A
        set_target_datasource(
        store=memory,
        luid=datasource.get('luid'),
        name=datasource.get('name'),
        description=datasource.get('description')
    )

    if workbook:
        # store workbook for content recommendations and Q&A
        set_target_workbook(
        store=memory,
        luid=workbook.get('luid'),
        name=workbook.get('name'),
        description=workbook.get('description'),
        sheets=workbook.get('sheets'),
        viz_url=workbook.get('viz_url')
    )

    if rag:
        if rag.get('analytics'):
            # store references to vector indexes on analytical topics
            set_vector_store(
                store=memory,
                topic='analytics',
                data=rag.get('analytics')
            )
        if rag.get('knowledge_base'):
            # store references to vector indexes on knowledge base topics
            set_vector_store(
                store=memory,
                topic='knowledge_base',
                data=rag.get('knowledge_base')
            )

    return memory


# this is now more an example of base memory store syntax set_vectore_store is abstracting
# def set_analytics_vectorstore(**kwargs):
#     # insert analytics vector stores for RAG
#     rag_analytics_namespace = ("rag", "analytics")
#     vectors_key = "vectors"
#     kwargs['store'].put(rag_analytics_namespace, vectors_key, {
#         "metrics": {
#             "index": kwargs.get('metrics_index'),
#             "description": kwargs.get('metrics_description')
#         },
#         "workbooks": {
#             "index": kwargs.get('workbooks_index'),
#             "description": kwargs.get('workbooks_description')
#         },
#         "datasources": {
#             "index": kwargs.get('datasources_index'),
#             "description": kwargs.get('datasources_description')
#         }
#     })
