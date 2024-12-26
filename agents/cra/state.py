
from typing import TypedDict, Annotated, Sequence

from langchain_core.messages import BaseMessage

from langgraph.graph.message import add_messages
from langgraph.managed import IsLastStep


# define custom state for the cra agent
class CustomState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]
    is_last_step: IsLastStep # required to customize create_react_agent
    user_context: str
    application_context: str
    language: str
