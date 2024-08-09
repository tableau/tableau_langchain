import os, re, json, pandas as pd

from langchain_openai import ChatOpenAI
from langchain.agents.agent_types import AgentType
from langchain_experimental.agents.agent_toolkits import create_pandas_dataframe_agent

from modules import headless

def analyze(query):
    payload = get_payload(query)
    vds_data = headless.query(payload)
    # Create a pandas DataFrame from the JSON data
    df = pd.DataFrame(vds_data)

    agent = create_pandas_dataframe_agent(
        ChatOpenAI(temperature=0, model=os.environ['PANDAS_AGENT_MODEL']),
        df,
        verbose=True,
        agent_type=AgentType.OPENAI_FUNCTIONS,
        allow_dangerous_code=True,
    )

    instruct_header = "Answer the following query directly by executing the necessary python code. Give a succinct explanation of the steps you took and how you know the answer is correct: "

    operation = agent.invoke(instruct_header + query)

    input = operation['input']
    output = operation['output']

    print('***** PANDAS AGENT Input *****', type(input), '\n', input)
    print('-----------------------------------------')
    print('***** PANDAS AGENT Output *****:', type(output), '\n', output)

    return output


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
