from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field
from typing import Any, Dict, Tuple, Type

class QueryInput(BaseModel):
    pat_name: str = Field(description="PAT name for authentication to Tableau Headless BI")
    pat_key: str = Field(description= "PAT token value for authentication to Tableau Headless BI")
    tab_server_url: str = Field(description="tableau server url")
    tab_site: str = Field(description="tableau site name")
    datasource_id: str = Field(description="ID of the Tableau datasource")
    metadata: Dict[str, Any] = Field(description="Metadata describing the dataset for accurate querying")
    endpoint: str = Field(description="Headless BI API endpoint for querying the datasource")
    query: str = Field(description="Detailed question about the dataset")

class QueryTableauData(BaseTool):
    name: str = "query_tableau_datasource"
    description: str = """
    A tool to query Tableau data sources on-demand using natural language.

    Tableau users will regularly define user-friendly data models powering
    business outcomes via visual analytics. These same models and semantics
    translate into powerful Q&A and analytical capabilities for Agents.

    Input to this tool is a natural language user question and details
    required to query the target Tableau data source.

    Output is a resulting dataset only containing the fields,
    aggregations and calculations needed to answer the user's question.
    """
    args_schema: Type[BaseModel] = QueryInput  # Specify the argument schema


    def _run(self, api_key: str, datasource_id: str, metadata: Dict[str, Any], endpoint: str, query: str) -> Dict[str, Any]:
        # Logic to construct the query payload
        # Here you would implement the logic to create the JSON payload based on the inputs
        # For demonstration, we will create a simple payload
        payload = {
            "query": query,
            "datasource_id": datasource_id,
            "metadata": metadata
        }

        # Justification for the query
        query_plan = f"""
        The query was constructed to answer the question: '{query}'.
        It uses the datasource ID: {datasource_id} and includes relevant metadata.
        """

        # Return the structured output
        return {
            "query_plan": query_plan,
            "payload": payload
        }
