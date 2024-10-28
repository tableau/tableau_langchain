import os
import time

from pinecone import Pinecone, ServerlessSpec

from semantic_router.encoders import OpenAIEncoder

from langchain_pinecone import PineconeVectorStore
from langchain_core.tools import tool
from langchain_community.tools.tavily_search import TavilySearchResults

from community.tools.tableau.query_data import QueryTableauData


def equip_tooling():
    # Web Search tool
    web_search = tavily_tool()

    # Knowledge Base tool
    knowledge_base = pinecone_vectorstore

    # Example usage of query_data tool
    # tool = QueryTableauData()
    # result = tool.invoke({
    #     "api_key": "your_api_key",
    #     "datasource_id": "your_datasource_id",
    #     "metadata": {"key": "value"},
    #     "endpoint": "https://api.tableau.com/query",
    #     "query": "How many rows are in table1?"
    # })
    # print(result)

    # List of tools used to build the state graph and for binding them to nodes
    tools = [knowledge_base, web_search]

    return tools


def tavily_tool():
    tavily_api_key = os.environ.get('TAVILY_API_KEY')
    tavily = TavilySearchResults(tavily_api_key=tavily_api_key, max_results=2)
    return tavily

@tool("pinecone_vectorstore")
def pinecone_vectorstore(query: str):
    """
    Finds specialist information from the organization's knowledge base using a natural language query.
    """
    pinecone_api_key = os.environ.get("PINECONE_API_KEY")
    index_name = os.environ.get("PINECONE_INDEX_NAME")
    index_region = os.environ.get("PINECONE_ENVIRONMENT")
    retriever_model = os.environ.get("RETRIEVER_MODEL")

    # embedding model used during retrieval
    encoder = OpenAIEncoder(name=retriever_model)

    # initialize pinecone client
    pc = Pinecone(api_key=pinecone_api_key)

    # search for matching index in list of available indexes to client
    existing_indexes = [index_info["name"] for index_info in pc.list_indexes()]
    # if the index does not exist, create one - no matches is better than broken tools
    if index_name not in existing_indexes:
        pc.create_index(
            name=index_name,
            dimension=3072,
            metric="cosine",
            spec=ServerlessSpec(cloud="aws", region=index_region),
        )
        while not pc.describe_index(index_name).status["ready"]:
            time.sleep(1)

    # initializes the index through the Pinecone client
    index = pc.Index(index_name)
    #
    xq = encoder([query])
    xc = index.query(
        vector=xq,
        top_k=3,
        include_metadata=True,
        # filter={"uaf": "amer"},
    )
    context_str = xc["matches"]
    return context_str

@tool("final_answer")
def final_answer(
    introduction: str,
    research_steps: str,
    main_body: str,
    conclusion: str,
    sources: str
):
    """Returns a natural language response to the user in the form of a research
    report. There are several sections to this report, those are:
    - `introduction`: a short paragraph introducing the user's question and the
    topic we are researching.
    - `research_steps`: a few bullet points explaining the steps that were taken
    to research your report.
    - `main_body`: this is where the bulk of high quality and concise
    information that answers the user's question belongs. It is 3-4 paragraphs
    long in length.
    - `conclusion`: this is a short single paragraph conclusion providing a
    concise but sophisticated view on what was found.
    - `sources`: a bulletpoint list provided detailed sources for all information
    referenced during the research process
    """
    if type(research_steps) is list:
        research_steps = "\n".join([f"- {r}" for r in research_steps])
    if type(sources) is list:
        sources = "\n".join([f"- {s}" for s in sources])
    return ""
