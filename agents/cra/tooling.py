from agents.tools import tableau_metrics, tavily_tool
from community.langchain_community.tools.tableau.analyze_data import analyze_data

# Metrics RAG tool
metrics = tableau_metrics

# Tableau VizQL Data Service Query Tool
analyze_datasource = analyze_data

# Web Search tool
# web_search = tavily_tool()

# List of tools used to build the state graph and for binding them to nodes
tools = [ metrics, analyze_datasource ]
