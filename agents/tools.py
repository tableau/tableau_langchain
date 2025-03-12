import os
import time

from langchain_core.tools import tool
from langchain_core.prompts import PromptTemplate
from langchain_community.tools.tavily_search import TavilySearchResults


from llama_index.core import VectorStoreIndex
from llama_index.core.retrievers import VectorIndexRetriever
from llama_index.vector_stores.pinecone import PineconeVectorStore

from pinecone import Pinecone, ServerlessSpec
from pinecone.grpc import PineconeGRPC


from semantic_router.encoders import OpenAIEncoder

def tavily_tool():
    tavily_api_key = os.environ.get('TAVILY_API_KEY')
    tavily = TavilySearchResults(tavily_api_key=tavily_api_key, max_results=2)
    return tavily

@tool("tableau_metrics")
def tableau_metrics(query: str):
    """
    Query a vector database for relevant information to the user query regarding
    how their metrics performing. This reference contains machine learning insights
    used to provide up to date and reliable data regarding all kinds of aspects related
    to the user's subscribed metrics.

    Prioritize using this tool if the user mentions metrics, KPIs, OKRs or similar.
    Make few and simple queries that reflect the user's question unless you are instructed
    to write thorough summaries, reports or analysis requiring multiple complex queries.
    """
    pinecone_api_key = os.environ["PINECONE_API_KEY"]
    index_name = os.environ["PINECONE_METRICS_INDEX"]
    index_region = os.environ["PINECONE_ENVIRONMENT"]

    # Initialize connection to Pinecone
    pc = PineconeGRPC(api_key=pinecone_api_key)

    # search for matching index in list of available indexes to client
    existing_indexes = [index_info["name"] for index_info in pc.list_indexes()]
    # if the index does not exist, create one - no matches is better than broken tools
    if index_name not in existing_indexes:
        pc.create_index(
            name=index_name,
            dimension=1536,
            metric="cosine",
            spec=ServerlessSpec(cloud="aws", region=index_region),
        )
        while not pc.describe_index(index_name).status["ready"]:
            time.sleep(1)

    # Initialize your index
    pinecone_index = pc.Index(index_name)

    # Initialize VectorStore
    vector_store = PineconeVectorStore(pinecone_index=pinecone_index)

    # Instantiate VectorStoreIndex object from your vector_store object
    vector_index = VectorStoreIndex.from_vector_store(vector_store=vector_store)

    # Grab 5 search results
    retriever = VectorIndexRetriever(index=vector_index, similarity_top_k=5)

    # Query vector DB
    docs = retriever.retrieve(query)

    # Extract content from retrieved documents
    metrics_content = "\n".join([doc.get_content() for doc in docs])

    metrics_response = """
    This is the output of a tool that retrieves updated information about the user's metrics and KPIs from a remote
    vector database. Your job is to answer the user's questions with this context.

    This is the relevant data about the user's metrics:
    {metrics}

    This is the user's question, task or command:
    {user_input}

    Based on the provided context, formulate a comprehensive and informative response to the user_input.
    Your response should be:
    1. Unless the user_input explicitly asks for detailed, thorough and comprehensive analysis you should prioritize
    generating brief, simple and concise answers to provide a quick response.
    2. Provide additional insights or conclusions only when relevant to the user, don't generate additional insights
    that are unasked for

    Your synthesized response:
    """

    response_prompt = PromptTemplate(
        input_variables=["metrics", "user_input"],
        template=metrics_response
    )

    # Format the prompt with the retrieved metrics and the original query
    formatted_prompt = response_prompt.format(metrics=metrics_content, user_input=query)

    return formatted_prompt


@tool("tableau_datasources_catalog")
def tableau_datasources(query: str):
    """
    Query a vector database to find the most relevant or useful Tableau data source to answer
    the user query. Datasources will have descriptions and fields that may match the needs
    of the user, use this information to determine the best data resource to target. Use this tool
    if you must query a data source but you do not know which one to target.

    Output is various chunks of text in vector format for summarization.

    Args:
        query (str): A natural language query describing the data to retrieve or an open-ended question
        that can be answered using information contained in the data source

    Returns:
        dict: A data set relevant to the user's query
    """
    pinecone_api_key = os.environ["PINECONE_API_KEY"]
    index_name = os.environ["PINECONE_DATASOURCES_INDEX"]
    index_region = os.environ["PINECONE_ENVIRONMENT"]

    # Initialize connection to Pinecone
    pc = PineconeGRPC(api_key=pinecone_api_key)

    # search for matching index in list of available indexes to client
    existing_indexes = [index_info["name"] for index_info in pc.list_indexes()]
    # if the index does not exist, create one - no matches is better than broken tools
    if index_name not in existing_indexes:
        pc.create_index(
            name=index_name,
            dimension=1536,
            metric="cosine",
            spec=ServerlessSpec(cloud="aws", region=index_region),
        )
        while not pc.describe_index(index_name).status["ready"]:
            time.sleep(1)

    # Initialize your index
    pinecone_index = pc.Index(index_name)

    # Initialize VectorStore
    vector_store = PineconeVectorStore(pinecone_index=pinecone_index)

    # Instantiate VectorStoreIndex object from your vector_store object
    vector_index = VectorStoreIndex.from_vector_store(vector_store=vector_store)

    # Grab 5 search results
    retriever = VectorIndexRetriever(index=vector_index, similarity_top_k=5)

    # Query vector DB
    answer = retriever.retrieve(query)

    # Inspect results
    if (os.environ["DEBUG"] == 1):
        print([i.get_content() for i in answer])

    return answer


@tool("tableau_workbooks_catalog")
def tableau_workbooks(query: str):
    """
    Query a vector database to find the most relevant or useful Tableau workbooks to answer
    the user query. Workbooks contain multiple individual charts and dashboards with a description
    that may match the needs of the user, use this information to recommend the best visual
    analytics resource to explore.

    Output is various chunks of text in vector format for summarization.

    Args:
        query (str): A natural language query describing the data to retrieve or an open-ended question
        that can be answered using information contained in the data source

    Returns:
        dict: A data set relevant to the user's query
    """
    pinecone_api_key = os.environ["PINECONE_API_KEY"]
    index_name = os.environ["PINECONE_WORKBOOKS_INDEX"]
    index_region = os.environ["PINECONE_ENVIRONMENT"]

    # Initialize connection to Pinecone
    pc = PineconeGRPC(api_key=pinecone_api_key)

    # search for matching index in list of available indexes to client
    existing_indexes = [index_info["name"] for index_info in pc.list_indexes()]
    # if the index does not exist, create one - no matches is better than broken tools
    if index_name not in existing_indexes:
        pc.create_index(
            name=index_name,
            dimension=1536,
            metric="cosine",
            spec=ServerlessSpec(cloud="aws", region=index_region),
        )
        while not pc.describe_index(index_name).status["ready"]:
            time.sleep(1)

    # Initialize your index
    pinecone_index = pc.Index(index_name)

    # Initialize VectorStore
    vector_store = PineconeVectorStore(pinecone_index=pinecone_index)

    # Instantiate VectorStoreIndex object from your vector_store object
    vector_index = VectorStoreIndex.from_vector_store(vector_store=vector_store)

    # Grab 5 search results
    retriever = VectorIndexRetriever(index=vector_index, similarity_top_k=5)

    # Query vector DB
    answer = retriever.retrieve(query)

    # Inspect results
    if (os.environ["DEBUG"] == 1):
        print([i.get_content() for i in answer])

    return answer


@tool("semantic_pinecone_retriever")
def semantic_pinecone_retriever(query: str):
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
