import os

from dotenv import load_dotenv

from langgraph.prebuilt import create_react_agent
from langgraph.store.memory import InMemoryStore

from experimental.utilities.models import select_model
from experimental.agents.keynote.tooling import tools
from experimental.agents.keynote.prompt import AGENT_SYSTEM_PROMPT


"""
ANALYTICS AGENT

This Agent uses the Langgraph prebuilt `create_react_agent` to handle conversations about Tableau data. This agent
is specifcally set up to work with a vehicle manufacturing procurement dataset.

"""
# environment variables available to current process and sub processes
load_dotenv()

# configure running model for the agent
llm = select_model(
    provider=os.environ["MODEL_PROVIDER"],
    model_name=os.environ["AGENT_MODEL"],
    temperature=0.2
)

# initialize a memory store
memory = InMemoryStore()

# set agent debugging state
if os.getenv('DEBUG') == '1':
    debugging = True
else:
    debugging = False

# define the agent graph
analytics_agent = create_react_agent(
    model=llm,
    tools=tools,
    debug=debugging,
    prompt=AGENT_SYSTEM_PROMPT
)
