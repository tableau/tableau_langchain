import os
from langchain_community.tools.tavily_search import TavilySearchResults

from community.tools.tableau.query_data import QueryTableauData

def equip_tooling():
    # LLM Search API
    tavily_api_key = os.getenv('TAVILY_API_KEY')
    tavily = TavilySearchResults(tavily_api_key=tavily_api_key, max_results=2)

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
    tools = [tavily]

    return tools
