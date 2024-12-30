import os
import json

from langchain_core.tools import tool
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import SystemMessage
from langchain_core.runnables import RunnableConfig

from langchain_openai import ChatOpenAI

from community.langchain_community.tools.tableau.prompts import vds_prompt
from community.langchain_community.utilities.tableau.query_data import augment_datasource_metadata, get_headlessbi_data

@tool
def query_data(
    query: str,
    config: RunnableConfig,
) -> dict:
    """
    A tool to query Tableau data sources via the VizQL Data Service HTTP API. The tool will return a data set
    with fields aggregated and filtered to provide insights to the end user. Use this tool to answer questions
    that cannot be adequately answered by existing metrics or workbooks.

    Output is a resulting dataset containing only the fields of data, aggregations and calculations
    needed to answer the input query.

    Args:
        query (str): A natural language query describing the data to retrieve or an open-ended question
        that can be answered using information contained in the data source.

    Returns:
        dict: A data set relevant to the user's query
    """

    # see Langgraph docs on accessing runtime values via RunnableConfig: https://langchain-ai.github.io/langgraph/how-tos/pass-config-to-tools
    runtime_values = config['configurable']
    # credentials to access Tableau environment on behalf of the user
    tableau_auth =  runtime_values['tableau_credentials']['session']["credentials"]["token"]
    tableau_url = runtime_values['tableau_credentials']['url']
    # data source for VDS querying
    tableau_datasource = runtime_values['datasource']['luid']

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
