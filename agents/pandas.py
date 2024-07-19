import re
import json
from langchain_openai import ChatOpenAI
from langchain.agents.agent_types import AgentType
from langchain_experimental.agents.agent_toolkits import create_pandas_dataframe_agent

from modules import headless

async def analyze(input_variables: dict) -> dict:
    query = input_variables['query']
    payload = get_payload(query)
    df = headless.query(payload)

    agent = create_pandas_dataframe_agent(
        ChatOpenAI(temperature=0, model="gpt-3.5-turbo-0125"),
        df,
        verbose=True,
        agent_type=AgentType.OPENAI_FUNCTIONS,
        allow_dangerous_code=True,
    )

    instruct_header = "Answer the following query directly by executing the necessary python code. Give a succinct explanation of the steps you took and how you know the answer is correct: "

    analysis = agent.invoke(instruct_header + query)

    print('analysis keys:', type(analysis), '\n', list(analysis.keys()))
    print('-----------------------------------------')
    print('pandas agent input:', type(analysis['input']), '\n', analysis['input'])
    print('-----------------------------------------')
    print('pandas agent output:', type(analysis['output']), '\n', analysis['output'])

    response_template = {
        "title": "ChainOutput",
        "analysis": analysis['output']
    }

    response = json.dumps(response_template)

    print('api response', response)

    # return response

    return json.dumps({ 'analysis': analysis })

    # # sample output
    # {
    #     "title": "ChainOutput",
    #     "type": "object",
    #     "properties": {
    #         "analysis": {
    #             "title": "Analysis"
    #         }
    #     }
    # }


def get_payload(output):
    # print reasoning
    print(output.split('JSON_payload')[0])
    # parse LLM output and query headless BI
    parsed_output = output.split('JSON_payload')[1]

    match = re.search(r'{.*}', parsed_output, re.DOTALL)
    if match:
        json_string = match.group(0)
        payload = json.loads(json_string)
        return payload
