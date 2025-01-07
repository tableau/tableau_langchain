from typing import Annotated

from typing_extensions import TypedDict

from langgraph.graph.message import add_messages


class ChatbotState(TypedDict):
    """
    Defines the State of a base Chatbot
    It consists of the graph schema and reducer functions applying updates to state.
    The messages key is annotated with the add_messages reducer function,
    which tells LangGraph to append new messages to the existing list, rather than overwriting it.
    State keys without an annotation will be overwritten by each update, storing the most recent value.
    """
    messages: Annotated[list, add_messages]
