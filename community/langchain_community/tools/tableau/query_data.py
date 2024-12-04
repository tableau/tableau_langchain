import os

from pydantic import BaseModel, Field
from typing import Any, Dict, Type
from typing_extensions import Annotated

from langchain_core.tools import BaseTool, tool
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import SystemMessage
from langchain_core.output_parsers import StrOutputParser, JsonOutputParser

from langchain_openai import ChatOpenAI

from community.langchain_community.tools.tableau.prompts import headlessbi_prompt
from community.langchain_community.utilities.tableau.query_data import augment_datasource_metadata, get_headlessbi_data


class QueryInput(BaseModel):
    api_key: str = Field(description="API key for authentication")
    datasource_id: str = Field(description="ID of the Tableau datasource")
    datasource_metadata: Annotated[dict, Field(description="Metadata describing the dataset")]
    endpoint: str = Field(description="API endpoint for querying")
    query: str = Field(description="Detailed question about the dataset")


class StringOnlyQueryInput(BaseModel):
    query: str = Field(description="Detailed question about the dataset")


class QueryTableauData(BaseTool):
    # Must be unique within a set of tools provided to an LLM or agent.
    name: str = "query_tableau_datasource"
    # Describes what the tool does. Used as context by the LLM or agent.
    description: str = """
    A tool to query Tableau data sources on-demand using natural language.

    Input to this tool is a natural language query from a human User or external Agent and
    additional details required to query the target Tableau data source via the VizQL Data Service
    using HTTP and JSON.

    Output is a resulting dataset containing only the fields of data, aggregations and calculations
    needed to answer the input query.

    Args:
        query (str): A natural language query describing the data to retrieve or an open-ended question
        that can be answered using information contained in a Tableau data source.

    Returns:
        dict: A data set relevant to the user's query obtained from Tableau's VizQL Data Service
    """
    # Optional but recommended, and required if using callback handlers. It can be used to provide more information
    # (e.g., few-shot examples) or validation for expected parameters.
    args_schema: Type[BaseModel] = StringOnlyQueryInput

    # def _run(self, api_key: str, datasource_id: str, datasource_metadata: Dict[str, Any], endpoint: str, query: str) -> Dict[str, Any]:

    def _run(self, query: str) -> Dict[str, Any]:
        # Ensure that the query is validated or processed here
        if not query:
            raise ValueError("Query must be provided")

        # 1. Prompt template incorporating datasource metadata
        tool_prompt = augment_datasource_metadata(headlessbi_prompt)
        # passes instructions and metadata to Langchain prompt template
        active_prompt_template = ChatPromptTemplate.from_messages([
            SystemMessage(content=tool_prompt),
            ("user", "{query}")
        ])

        # 2. Language model settings
        llm = ChatOpenAI(model=os.environ['AGENT_MODEL'], temperature=0)

        # 3. Query Data
        headlessbi_data = get_headlessbi_data

        # this chain defines the flow of data through the system
        chain = active_prompt_template | llm | headlessbi_data

        # invoke the chain to generate a query and obtain data
        queried_data = chain.invoke(query)

        # Return the structured output
        return queried_data


@tool
def get_data(query: str) -> dict:
    """
    A tool to query Tableau data sources on-demand using natural language.

    Input to this tool is a natural language query from a human User or external Agent and
    additional details required to query the target Tableau data source via the VizQL Data Service
    using HTTP and JSON.

    Output is a resulting dataset containing only the fields of data, aggregations and calculations
    needed to answer the input query.

    Args:
        query (str): A natural language query describing the data to retrieve or an open-ended question
        that can be answered using information contained in a Tableau data source.

    Returns:
        dict: A data set relevant to the user's query obtained from Tableau's VizQL Data Service
    """
    # Ensure that the query is validated or processed here
    if not query:
        raise ValueError("Query must be provided")

    # 1. Prompt template incorporating datasource metadata
    tool_prompt = augment_datasource_metadata(headlessbi_prompt)
    # passes instructions and metadata to Langchain prompt template
    active_prompt_template = ChatPromptTemplate.from_messages([
        SystemMessage(content=tool_prompt),
        ("user", "{query}")
    ])

    # 2. Language model settings
    llm = ChatOpenAI(model=os.environ['AGENT_MODEL'], temperature=0)

    # 3. Query Data
    headlessbi_data = get_headlessbi_data

    # this chain defines the flow of data through the system
    chain = active_prompt_template | llm | headlessbi_data

    # invoke the chain to generate a query and obtain data
    queried_data = chain.invoke(query)

    # Return the structured output
    return queried_data
