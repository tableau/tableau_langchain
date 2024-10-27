from agent.community.tools.tableau.query_data import QueryTableauData
from agent.utils import _set_env

_set_env('AGENT_MODEL')
_set_env('OPENAI_API_KEY')

# Example usage of query_data tool
tool = QueryTableauData()
result = tool.invoke({
    "api_key": "your_api_key",
    "datasource_id": "your_datasource_id",
    "metadata": {"key": "value"},
    "endpoint": "https://api.tableau.com/query",
    "query": "How many rows are in table1?"
})

print(result)
