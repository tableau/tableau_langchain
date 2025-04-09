import os

from pinecone import Pinecone

from langchain_pinecone import PineconeVectorStore
from langchain.tools.retriever import create_retriever_tool

from experimental.utilities.models import select_embeddings


def pinecone_retriever_tool(
    name: str,
    description: str,
    pinecone_index: str,
    model_provider: str,
    embedding_model: str
):
    # Initialize Pinecone client
    pc = Pinecone(api_key=os.environ.get("PINECONE_API_KEY"))

    embeddings = select_embeddings(
        provider = model_provider or os.environ.get("MODEL_PROVIDER", "openai"),
        model_name = embedding_model or os.environ.get("EMBEDDING_MODEL", "text-embedding-3-small")
    )

    def make_retriever(index_name: str, concurrency: int = 5):
        vector_store = PineconeVectorStore.from_existing_index(
            index_name=index_name,
            embedding=embeddings,
            text_key="_node_content"
        )

        return vector_store.as_retriever(
            search_kwargs={"k": 6},
            verbose=False
        )


    retriever = make_retriever(pinecone_index)

    retriever_tool = create_retriever_tool(
        retriever,
        name=name,
        description=description
    )

    return retriever_tool
