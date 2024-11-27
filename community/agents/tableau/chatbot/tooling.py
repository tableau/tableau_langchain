from community.tools.others import llamaindex_pinecone_retriever, tavily_tool
from community.tools.tableau.query_data import QueryTableauData


def equip_tooling():
    # Knowledge Base tool
    knowledge_base = llamaindex_pinecone_retriever

    # Tableau Data Source Query Tool
    query_datasource = QueryTableauData

    # Web Search tool
    web_search = tavily_tool()

    # List of tools used to build the state graph and for binding them to nodes
    tools = [knowledge_base, query_datasource, web_search]

    return tools
