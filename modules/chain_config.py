import os

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import SystemMessage
from langchain_core.output_parsers import StrOutputParser
from langchain.globals import set_verbose

from modules import metadata, api
from agents import pandas

# defines the langtab chain
def create_chain():
    set_verbose(True)

    # 1. Prompt template incorporating datasource metadata
    headless_bi_prompt_string = metadata.instantiate_prompt()
    # passes instructions and metadata to Langchain prompt template
    active_prompt_template = ChatPromptTemplate.from_messages([
        SystemMessage(content=headless_bi_prompt_string),
        ("user", "{query}")
    ])

    # 2. Chat model (BYOM)
    llm = ChatOpenAI(model=os.environ['VDS_AGENT_MODEL'], temperature=0)

    # 3. Standard Langchain parser
    output_parser = StrOutputParser()

    # 4. Langchain pandas agent
    pandas_agent = pandas.analyze

    # 5. natural language response in the expected API format
    json_parser = api.vds_transform

    # this chain defines the flow of data through the system
    chain = active_prompt_template | llm | output_parser | pandas_agent | json_parser

    return chain
