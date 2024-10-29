from tools.others import llamaindex_pinecone_retriever, tavily_tool


def equip_tooling():
    # Knowledge Base tool
    knowledge_base = llamaindex_pinecone_retriever

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

    # Web Search tool
    web_search = tavily_tool()

    # List of tools used to build the state graph and for binding them to nodes
    tools = [knowledge_base, web_search]

    return tools
