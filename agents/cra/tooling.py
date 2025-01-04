from agents.tools import tableau_metrics, tavily_tool
from community.langchain_community.tools.tableau.query_data import query_data

# Metrics RAG tool
metrics = tableau_metrics

# Tableau VizQL Data Service Query Tool
query_datasource = query_data

# Web Search tool
# web_search = tavily_tool()

# List of tools used to build the state graph and for binding them to nodes
tools = [ metrics, query_datasource ]
