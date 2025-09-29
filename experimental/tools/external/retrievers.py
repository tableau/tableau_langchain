import os

try:
    from pinecone import Pinecone
    from langchain_pinecone import PineconeVectorStore
    PINECONE_AVAILABLE = True
except ImportError:
    PINECONE_AVAILABLE = False

from langchain.tools.retriever import create_retriever_tool

from experimental.utilities.models import select_embeddings


def pinecone_retriever_tool(
    name: str,
    description: str,
    pinecone_index: str,
    model_provider: str,
    embedding_model: str,
    text_key: str = "text",
    search_k: int = 6,
    max_concurrency: int = 5
):
    """
    Initializes a Pinecone retriever using langchain-pinecone and creates a LangChain tool.

    Assumes PINECONE_API_KEY and PINECONE_ENVIRONMENT environment variables are set for
    PineconeVectorStore initialization.

    Args:
        name: The name to assign to the created LangChain tool.
        description: The description for the created LangChain tool.
        pinecone_index: The name of the Pinecone index to connect to.
        model_provider: The model vendor such as `openai`, `azure` or `anthropic`
        embedding_model: The embedding model to be used such as `text-embedding-3-small`,
        text_key: Pinecone metadata containing the content, default: `text`,  `_node_content` is another example.
        search_k: The number of documents to retrieve (k). Defaults to 6.
        max_concurrency: The maximum concurrency for retriever requests. Defaults to 5.

    Returns:
        A LangChain BaseTool configured to use the specified Pinecone retriever.

    Raises:
        ImportError: If langchain-pinecone is not installed.
        EnvironmentError: If required Pinecone environment variables are missing.
        Exception: If connection to the Pinecone index fails.
    """
    if not PINECONE_AVAILABLE:
        raise ImportError("Pinecone dependencies are not installed. Please install pinecone-client and langchain-pinecone.")

    # Initialize Pinecone client
    pc = Pinecone(api_key=os.environ.get("PINECONE_API_KEY"))

    embeddings = select_embeddings(
        provider = model_provider or os.environ.get("MODEL_PROVIDER", "openai"),
        model_name = embedding_model or os.environ.get("EMBEDDING_MODEL", "text-embedding-3-small")
    )

    def make_retriever(index_name: str):
        vector_store = PineconeVectorStore.from_existing_index(
            index_name=index_name,
            embedding=embeddings,
            text_key=text_key
        )

        return vector_store.as_retriever(
            search_kwargs={"k": search_k},
            max_concurrency=max_concurrency,
            verbose=False
        )


    retriever = make_retriever(pinecone_index)

    retriever_tool = create_retriever_tool(
        retriever,
        name=name,
        description=description
    )

    return retriever_tool
