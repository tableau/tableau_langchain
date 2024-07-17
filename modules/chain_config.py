import json
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import SystemMessage
from langchain_core.output_parsers import StrOutputParser
from langchain.chains import TransformChain

from modules import metadata
from prompts import nlq_to_vds
from agents import pandas

def create_chain(env_vars):
    # 1. Prompt template
    datasource_metadata = metadata.read(env_vars)
    nlq_to_vds.prompt['data_model'] = datasource_metadata
    headless_bi_prompt_string = json.dumps(nlq_to_vds.prompt)

    active_prompt_template = ChatPromptTemplate.from_messages([
        SystemMessage(content=headless_bi_prompt_string),
        ("user", "{utterance}")
    ])

    # 2. Chat model
    llm = ChatOpenAI(model="gpt-4")

    # 3. Parser
    output_parser = StrOutputParser()

    # 4. Pandas agent
    pandas_agent = TransformChain(
        input_variables=["query"],
        output_variables=["analysis"],
        transform=pandas.analyze
    )

    chain = active_prompt_template | llm | output_parser | pandas_agent

    return chain
