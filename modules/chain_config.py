import json
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import SystemMessage
from langchain_core.output_parsers import StrOutputParser

from modules import metadata
from prompts import nlq_to_vds

def create_chain(env_vars):
    datasource_metadata = metadata.read(env_vars)
    nlq_to_vds.prompt['data_model'] = datasource_metadata
    headless_bi_prompt_string = json.dumps(nlq_to_vds.prompt)

    llm = ChatOpenAI(model="gpt-4")

    active_prompt_template = ChatPromptTemplate.from_messages([
        SystemMessage(content=headless_bi_prompt_string),
        ("user", "{utterance}")
    ])

    output_parser = StrOutputParser()
    chain = active_prompt_template | llm | output_parser
    return chain
