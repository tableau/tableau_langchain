import os
import json
import requests
import re

from langchain.tools import BaseTool, StructuredTool, tool
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.output_parsers import StrOutputParser

from .prompts import prompt

@tool
def get_data(query: str) -> dict:
    """
    Generates the VizQL data service query payload for retrieving relevant data from a Tableau published datasource.
    It then passes the payload to the query_datasource endpoint exposed by the VizQL data service and returns a json 
    formatted dataframe as output. 

    Args:
        query (str): A natural language query describing the data to retrieve.

    Returns:
        dict: A JSON payload suitable for the VizQL data service.
    """
    llm = ChatOpenAI(model='gpt-4o-mini', temperature=0)

    prompt_template = ChatPromptTemplate.from_messages([
      SystemMessage(content=json.dumps(prompt)),
      ("user", "{utterance}")])
    
    output_parser = StrOutputParser()
    
    chain = prompt_template | llm | output_parser
    
    output = chain.invoke(query)
    parsed_output = output.split('JSON_payload')[1]
    match = re.search(r'{.*}', parsed_output, re.DOTALL)
    if match:
        json_string = match.group(0)
    query_object = json.loads(json_string)

    query_url = os.getenv('QUERY_DATASOURCE')
    datasource_luid = os.getenv('DATASOURCE_LUID')
    auth_secret = os.getenv('AUTH_TOKEN')
    return('here is the query payload I tried to execute' + str({json_string}))
    # payload = json.dumps({
    #     "datasource": {
    #         "datasourceLuid": datasource_luid
    #     },
    #     "query": query_object
    # })

    # headers = {
    #     'X-Tableau-Auth': auth_secret,
    #     'Content-Type': 'application/json'
    # }

    # response = requests.post(query_url, headers=headers, data=payload)

    # if response.status_code == 200:
    #     data = response.json().get('data')
    #     return data
    # else:
    #     raise Exception(f"Failed to fetch data from the API. Status code: {response.status_code}, Response: {response.text}")
    
