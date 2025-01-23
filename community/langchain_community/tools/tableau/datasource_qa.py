import os

from langchain_core.tools import tool
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import SystemMessage

from langchain_openai import ChatOpenAI

from community.langchain_community.tools.tableau.prompts import vds_prompt
from community.langchain_community.utilities.tableau.analyze_data import augment_datasource_metadata, get_headlessbi_data
from community.langchain_community.utilities.tableau.utils import authenticate_tableau_user

@tool("datasource_qa")
async def datasource_qa(
    query: str,
) -> dict:
    """
    Queries a Tableau data source for analytical Q&A. Returns a data set you can use to answer user questions.
    You need a data source to target to use this tool. If a target data source is unknown, use a data source
    search tool to find the right resource and retry with more information or ask the user to provide it.

    Prioritize this tool if the user asks you to analyze and explore data. This tool includes Agent summarization
    and is not meant for direct data set exports. To be more efficient, query all the data you need in a single
    request rather than selecting small slices of data in multiple requests
    """

    domain = os.environ['TABLEAU_DOMAIN']
    site = os.environ['TABLEAU_SITE']

    # define required authorizations to Tableau resources to support Agent operations
    access_scopes = [
        "tableau:content:read", # for quering Tableau Metadata API
        "tableau:viz_data_service:read" # for querying VizQL Data Service
    ]

    tableau_session = await authenticate_tableau_user(
        jwt_client_id=os.environ['TABLEAU_JWT_CLIENT_ID'],
        jwt_secret_id=os.environ['TABLEAU_JWT_SECRET_ID'],
        jwt_secret=os.environ['TABLEAU_JWT_SECRET'],
        tableau_api=os.environ['TABLEAU_API'],
        tableau_user=os.environ['TABLEAU_USER'],
        tableau_domain=domain,
        tableau_site=site,
        scopes=access_scopes
    )

    # credentials to access Tableau environment on behalf of the user
    tableau_auth =  tableau_session['credentials']['token']
    if not tableau_auth or not domain:
        # lets the Agent know this error cannot be resolved by the end user
        raise KeyError("Critical Error: Tableau credentials were not provided by the client application. INSTRUCTION: Do not ask the user to provide credentials directly or in chat since they should come from a secure application.")

    # Data source for VDS querying
    tableau_datasource = os.environ['DATASOURCE_LUID']

    # Check if we have a valid datasource
    if not tableau_datasource:
        # Lets the Agent know that the LUID is missing and it needs to use an alternative tool
        raise KeyError("The Datasource LUID is missing. Use a data source search tool to find an appropriate query target that matches the user query.")

    # 1. Initialize Langchain chat template with an augmented prompt containing metadata for the datasource
    query_data_prompt = ChatPromptTemplate.from_messages([
        SystemMessage(content = await augment_datasource_metadata(
            api_key = tableau_auth,
            url = domain,
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
            url = domain,
            datasource_luid = tableau_datasource,
            payload = vds_query.content
        )

    # this chain defines the flow of data through the system
    chain = query_data_prompt | query_writer | get_data

    # invoke the chain to generate a query and obtain data
    vizql_data = await chain.ainvoke(query)

    # Return the structured output
    return vizql_data
