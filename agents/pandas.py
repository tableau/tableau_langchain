import os
from langchain_openai import ChatOpenAI
from langchain.agents.agent_types import AgentType
from langchain_experimental.agents.agent_toolkits import create_pandas_dataframe_agent


def pandas_agent(df):
    pandas_model = os.environ['PANDAS_AGENT_MODEL']
    agent = create_pandas_dataframe_agent(
        ChatOpenAI(temperature=0, model=pandas_model),
        df,
        verbose=True,
        agent_type=AgentType.OPENAI_FUNCTIONS,
        allow_dangerous_code=True,
    )

    return agent
