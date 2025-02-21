import os
from langchain_pinecone import PineconeVectorStore
from langchain.tools import Tool
from pinecone import Pinecone

from agents.models import select_embeddings

# Initialize Pinecone client
pinecone = Pinecone(api_key=os.environ["PINECONE_API_KEY"])

# Select embeddings
embeddings = select_embeddings(
    provider=os.environ["MODEL_PROVIDER"],
    model_name=os.environ["EMBEDDING_MODEL"]
)

def initialize_rag_tool(index_name, tool_name, description):
    pinecone_index = pinecone.Index(index_name)

    vectorstore = PineconeVectorStore(
        index=pinecone_index,
        embedding=embeddings,
        text_key="_node_content"
    )

    retriever = vectorstore.as_retriever(
        search_kwargs={"k": 6}
    )

    tool = Tool(
        name=tool_name,
        func=retriever.get_relevant_documents,
        description=description
    )

    return tool


tableau_metrics = initialize_rag_tool(
    index_name=os.environ["METRICS_INDEX"],
    tool_name="tableau_metrics",
    description="""Returns ML insights on user-subscribed metrics.
    Use for queries about metrics, KPIs, or OKRs.

    Make thorough queries for relevant context.
    Use "metrics update" for a summary. For detailed metric info, ask about:
    - dimensions
    - data
    - descriptions
    - drivers
    - unusual changes
    - trends
    - sentiment
    - current & previous values
    - period over period change
    - contributors
    - detractors

    NOT for precise data values. Use a data source query tool for specific values.
    NOT for fetching data values on specific dates

    Examples:
    User: give me an update on my KPIs
    Input: 'update on all KPIs, trends, sentiment"

    User: what is going on with sales?
    Input: 'sales trend, data driving sales, unusual changes, contributors, drivers and detractors'

    User: what is the value of sales in 2024?
    -> wrong usage of this tool, not for specific values"""
)
