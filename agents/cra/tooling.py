from agents.tools import tableau_metrics, tavily_tool
from community.langchain_community.tools.tableau.analyze_data import analyze_data
from community.langchain_community.tools.tableau.datasource_qa import datasource_qa


# Metrics RAG tool
metrics = tableau_metrics

# Tableau VizQL Data Service Query Tool
analyze_datasource = datasource_qa

# Web Search tool
# web_search = tavily_tool()

# List of tools used to build the state graph and for binding them to nodes
tools = [ metrics, datasource_qa ]
