import operator

from typing import Annotated

from typing_extensions import TypedDict

from langchain_core.agents import AgentAction
from langchain_core.messages import BaseMessage


class ResearchAgentState(TypedDict):
    """
    Defines the State of the Tableau Langchain Agent
    It consists of the graph schema and reducer functions applying updates to state.

    input: the user's most recent query. Generally, this is a data or analytics related question

    chat_history: supports multiple coherent conversation by using previous interactions to contextualize
    the current query by storing it in agent state

    intermediate_steps: records all steps taken by the agent to generate a final answer.
    Steps can include "search knowledge base", "query data source", "search the web", etc.
    These records form a coherent path of actions to anwser user queries
    """
    input: str
    chat_history: list[BaseMessage]
    intermediate_steps: Annotated[list[tuple[AgentAction, str]], operator.add]
