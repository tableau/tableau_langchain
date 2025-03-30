from agents.tools import llamaindex_pinecone_retriever, tavily_tool
from community.langchain_community.tools.tableau.analyze_data import analyze_data


def equip_tooling():
    # Knowledge Base tool
    knowledge_base = llamaindex_pinecone_retriever

    # Tableau VizQL Data Service Query Tool
    analyze_datasource = analyze_data

    # Web Search tool
    web_search = tavily_tool()

    # List of tools used to build the state graph and for binding them to nodes
    tools = [knowledge_base, analyze_datasource, web_search]

    return tools
