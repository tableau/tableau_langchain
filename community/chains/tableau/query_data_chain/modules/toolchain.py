import os

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import SystemMessage
from langchain_core.output_parsers import StrOutputParser, JsonOutputParser
from langchain.globals import set_verbose

from modules import metadata, headless

# defines query_data_chain
def create_chain():
    # Check if the environment variable ENV is set to 'development'
    if os.getenv('DEBUG') == 1:
        set_verbose(True)
    else:
        set_verbose(False)

    # 1. Prompt template incorporating datasource metadata
    headless_bi_prompt_string = metadata.instantiate_prompt()
    # passes instructions and metadata to Langchain prompt template
    active_prompt_template = ChatPromptTemplate.from_messages([
        SystemMessage(content=headless_bi_prompt_string),
        ("user", "{query}")
    ])

    # 2. Chat model (BYOM)
    llm = ChatOpenAI(model=os.environ['AGENT_MODEL'], temperature=0)

    # 3. Query Data
    headlessbi_data = headless.get_data

    # 4. Standard Langchain string parser for terminal outputs
    output_parser = StrOutputParser()

    # 5. Standard Langchain string parser for API responses
    json_parser = JsonOutputParser()

    # this chain defines the flow of data through the system
    chain = active_prompt_template | llm | headlessbi_data

    return chain
