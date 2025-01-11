import os
from typing import Dict, Annotated, Optional

from langchain_core.tools import tool
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import SystemMessage

from langchain_openai import ChatOpenAI

from langgraph.prebuilt import InjectedState

from community.langchain_community.tools.tableau.prompts import vds_prompt
from community.langchain_community.utilities.tableau.analyze_data import AnalyzeDataInputs, augment_datasource_metadata, get_headlessbi_data

@tool("analyze_tableau_datasource")
async def analyze_data(
    query: str,
    tableau_credentials: Annotated[Dict, InjectedState("tableau_credentials")],
    datasource_state: Annotated[Dict, InjectedState("datasource")]
) -> dict:
    """
    Queries Tableau data sources for analytical Q&A. Returns a data set you can use to answer user questions.
    You need a data source to target to use this tool. If a target data source is unknown, use a data source
    search tool to find the right resource and retry with more information or ask the user to provide it.

    Prioritize this tool if the user asks you to analyze and explore data. This tool includes Agent summarization
    and is not meant for direct data set exports. To be more efficient, query all the data you need in a single
    request rather than selecting small slices of data in multiple requests
    """

    # credentials to access Tableau environment on behalf of the user
    tableau_auth =  tableau_credentials['session']
    tableau_url = tableau_credentials['url']
    if not tableau_auth or not tableau_url:
        # lets the Agent know this error cannot be resolved by the end user
        raise KeyError("Critical Error: Tableau credentials were not provided by the client application. INSTRUCTION: Do not ask the user to provide credentials directly or in chat since they should come from a secure application.")

    # Getting data source for VDS querying from InjectedState
    tableau_datasource = datasource_state['luid'] if datasource_state and 'luid' in datasource_state else None

    # Check if we have a valid datasource
    if not tableau_datasource:
        # Lets the Agent know that the LUID is missing and it needs to use an alternative tool
        raise KeyError("The Datasource LUID is missing. Use a data source search tool to find an appropriate query target that matches the user query.")

    # 1. Initialize Langchain chat template with an augmented prompt containing metadata for the datasource
    query_data_prompt = ChatPromptTemplate.from_messages([
        SystemMessage(content = await augment_datasource_metadata(
            api_key = tableau_auth,
            url = tableau_url,
            datasource_luid = tableau_datasource,
            prompt = vds_prompt
        )),
        ("user", "{utterance}")
    ])

    # 2. Instantiate language model and execute the prompt to write a VizQL Data Service query
    query_writer = ChatOpenAI(
        model=os.getenv('TOOLING_MODEL'),
        temperature=0
    )

    # 3. Query data from Tableau's VizQL Data Service using the dynamically written payload
    async def get_data(vds_query):
        return await get_headlessbi_data(
            api_key = tableau_auth,
            url = tableau_url,
            datasource_luid = tableau_datasource,
            payload = vds_query.content
        )

    # this chain defines the flow of data through the system
    chain = query_data_prompt | query_writer | get_data

    # invoke the chain to generate a query and obtain data
    vizql_data = await chain.ainvoke(query)

    # Return the structured output
    return await vizql_data
