import os

from langchain.prompts import PromptTemplate
from langchain_core.tools import tool
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import SystemMessage

from langchain_openai import ChatOpenAI

from community.langchain_community.tools.tableau.prompts import vds_prompt, vds_response
from community.langchain_community.utilities.tableau.datasource_qa import augment_datasource_metadata, get_headlessbi_data, authenticate_tableau_user, prepare_prompt_inputs

@tool("datasource_qa")
def datasource_qa(
    user_input: str,
    previous_call_error: str = None,
) -> dict:
    """
    Queries a Tableau data source for analytical Q&A. Returns a data set you can use to answer user questions.
    You need a data source to target to use this tool. If a target data source is unknown, use a data source
    search tool to find the right resource and retry with more information or ask the user to provide it.

    Prioritize this tool if the user asks you to analyze and explore data. This tool includes Agent summarization
    and is not meant for direct data set exports. To be more efficient, query all the data you need in a single
    request rather than selecting small slices of data in multiple requests

    If you received an error after using this tool, mention it in your next attempt to help the tool correct itself.
    """
    domain = os.environ['TABLEAU_DOMAIN']
    site = os.environ['TABLEAU_SITE']

    # define required authorizations to Tableau resources to support Agent operations
    access_scopes = [
        "tableau:content:read", # for quering Tableau Metadata API
        "tableau:viz_data_service:read" # for querying VizQL Data Service
    ]

    tableau_session = authenticate_tableau_user(
        jwt_client_id=os.environ['TABLEAU_JWT_CLIENT_ID'],
        jwt_secret_id=os.environ['TABLEAU_JWT_SECRET_ID'],
        jwt_secret=os.environ['TABLEAU_JWT_SECRET'],
        tableau_api=os.environ['TABLEAU_API_VERSION'],
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
        SystemMessage(content = augment_datasource_metadata(
            api_key = tableau_auth,
            url = domain,
            datasource_luid = tableau_datasource,
            prompt = vds_prompt,
            previous_errors = previous_call_error
        )),
        ("user", "{utterance}")
    ])

    # 2. Instantiate language model and execute the prompt to write a VizQL Data Service query
    query_writer = ChatOpenAI(
        model=os.getenv('TOOLING_MODEL'),
        temperature=0
    )

    # 3. Query data from Tableau's VizQL Data Service using the dynamically written payload
    def get_data(vds_query):
        data = get_headlessbi_data(
            api_key = tableau_auth,
            url = domain,
            datasource_luid = tableau_datasource,
            payload = vds_query.content
        )

        return {
            "vds_query": vds_query,
            "data_table": data,
        }

    # 4. Prepare inputs for Agent response
    def response_inputs(input):
        data = {
            "query": input.get('vds_query', ''),
            "data_source": tableau_datasource,
            "data_table": input.get('data_table', ''),
        }
        inputs = prepare_prompt_inputs(data=data, user_string=user_input)
        return inputs

    # 5. Response template for the Agent
    enhanced_prompt = PromptTemplate(
        input_variables=["data_source", "vds_query", "data_table", "user_input"],
        template=vds_response
    )

    # this chain defines the flow of data through the system
    chain = query_data_prompt | query_writer | get_data | response_inputs | enhanced_prompt

    # invoke the chain to generate a query and obtain data
    vizql_data = chain.invoke(user_input)

    # Return the structured output
    return vizql_data
