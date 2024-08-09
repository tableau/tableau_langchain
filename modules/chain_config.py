import os, json

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import SystemMessage
from langchain_core.output_parsers import StrOutputParser, JsonOutputParser
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain.globals import set_verbose

from modules import metadata, api
from prompts import nlq_to_vds
from agents import pandas

# defines the langtab chain
def create_chain():
    set_verbose(True)

    # 1. Prompt template
    datasource_metadata = metadata.read()
    nlq_to_vds.prompt['data_model'] = datasource_metadata
    headless_bi_prompt_string = json.dumps(nlq_to_vds.prompt)

    active_prompt_template = ChatPromptTemplate.from_messages([
        SystemMessage(content=headless_bi_prompt_string),
        ("user", "{query}")
    ])

    # 2. Chat model
    llm = ChatOpenAI(model=os.environ['VDS_AGENT_MODEL'])

    # 3. Parser
    output_parser = StrOutputParser()

    # 4. Pandas agent
    pandas_agent = pandas.analyze

    # 5. API response
    json_parser = api.vds_transform

    chain = active_prompt_template | llm | output_parser | pandas_agent | json_parser

    return chain

# Define the data structure for the response
class VDS_Query_Response(BaseModel):
    data: str = Field(description="the table of data containing the response to the query")
    behavioral: str = Field(description="a behavioral summary of the reasoning and explanation behind the action taken")
