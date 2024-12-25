from agents.tools import llamaindex_pinecone_retriever, tavily_tool
from community.langchain_community.tools.tableau.query_data import query_data

# Knowledge Base tool
knowledge_base = llamaindex_pinecone_retriever

# Tableau VizQL Data Service Query Tool
query_datasource = query_data

# Web Search tool
# web_search = tavily_tool()

# List of tools used to build the state graph and for binding them to nodes
tools = [ knowledge_base, query_datasource ]
