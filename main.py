from tools.query_data import QueryTableauData

# Example usage
tool = QueryTableauData()
result = tool.invoke({
    "api_key": "your_api_key",
    "datasource_id": "your_datasource_id",
    "metadata": {"key": "value"},
    "endpoint": "https://api.tableau.com/query",
    "query": "How many rows are in table1?"
})

print(result)
