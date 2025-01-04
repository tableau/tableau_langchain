import os
from typing import Dict, Annotated
import json

from langchain_core.tools import tool
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import SystemMessage

from langchain_openai import ChatOpenAI

from langgraph.prebuilt import InjectedState

from community.langchain_community.tools.tableau.prompts import vds_prompt
from community.langchain_community.utilities.tableau.query_data import augment_datasource_metadata, get_headlessbi_data

@tool("Query Tableau Data Source")
def query_data(
    query: str,
    tableau_credentials: Annotated[Dict, InjectedState("tableau_credentials")],
    datasource: Annotated[Dict, InjectedState("datasource")]
) -> dict:
    """
    A tool to query Tableau data sources via the VizQL Data Service HTTP API. The tool will return a data set
    with fields aggregated and filtered to provide analytical insights to the end user. Use this tool to answer
    questions that cannot be adequately answered by existing metrics or workbooks, which means that you must
    explore the underlying data source for answers

    Output is a resulting dataset containing only the fields of data, aggregations and calculations
    needed to answer the input query

    Args:
        query (str): A natural language query describing the data to retrieve or an open-ended question
        that can be answered using information contained in the data source

        tableau_credentials (Dict): Access credentials obtained from InjectedState to interact with a
        Tableau environment on behalf of the user

        datasource (Dict): Metadata about the target data source obtained from InjectedState. The luid
        attribute is mandatory for this tool to work

    Returns:
        dict: A data set relevant to the user's query
    """

    # credentials to access Tableau environment on behalf of the user
    tableau_auth =  tableau_credentials['session']
    tableau_url = tableau_credentials['url']
    if not tableau_auth or not tableau_url:
        # lets the Agent know this error cannot be resolved by the end user
        raise KeyError("Critical Error: Tableau credentials were not provided by the client application. The user cannot provide them either since they come from RunnableConfig")
    # data source for VDS querying
    tableau_datasource = datasource['luid']
    if not tableau_datasource:
        # lets the Agent know that the LUID is missing and it needs to use an alternative tool
        raise KeyError("The Datasource LUID was not provided by the user. Use the search_datasources tool to find an appropriate query target.")

    # augment the prompt template instructing the tool to query a datasource with the required metadata
    datasource_metadata = augment_datasource_metadata(
        api_key=tableau_auth,
        url=tableau_url,
        datasource_luid=tableau_datasource,
        prompt=vds_prompt
    )

    # 1. Initialize Langchain chat template with augmented prompt with desired parameters
    query_data_prompt = ChatPromptTemplate.from_messages([
        SystemMessage(content=json.dumps(datasource_metadata)),
        ("user", "{utterance}")
    ])

    # 2. Instantiate language model and execute the prompt to write a VizQL Data Service query
    query_writer = ChatOpenAI(
        model=os.getenv('AGENT_MODEL'),
        temperature=0
    )

    # 3. Query data from Tableau's VizQL Data Service using the dynamically written payload
    def get_data(vds_query):
        return get_headlessbi_data(
            api_key=tableau_auth,
            url=tableau_url,
            datasource_luid=tableau_datasource,
            payload=vds_query.content
        )

    # this chain defines the flow of data through the system
    chain = query_data_prompt | query_writer | get_data

    # invoke the chain to generate a query and obtain data
    vizql_data = chain.invoke(query)

    # Return the structured output
    return vizql_data
