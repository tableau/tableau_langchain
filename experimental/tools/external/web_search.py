import os

from langchain_core.tools import tool
from tavily import TavilyClient


def tavily_tool():
    """Return a Tavily web search tool (LangChain-compatible)."""
    tavily_api_key = os.environ.get("TAVILY_API_KEY")
    client = TavilyClient(api_key=tavily_api_key)

    @tool
    def tavily_search(query: str) -> str:
        """Search the web for current information. Use for questions about recent events, facts, or general knowledge."""
        response = client.search(query=query, max_results=2)
        if not response.get("results"):
            return "No results found."
        return "\n\n".join(
            f"{r.get('title', '')}: {r.get('content', '')}" for r in response["results"]
        )

    return tavily_search
