import os

from langchain_community.tools.tavily_search import TavilySearchResults


def tavily_tool():
    tavily_api_key = os.environ.get('TAVILY_API_KEY')
    tavily = TavilySearchResults(tavily_api_key=tavily_api_key, max_results=2)
    return tavily
