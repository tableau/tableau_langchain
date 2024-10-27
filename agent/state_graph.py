from typing import Annotated

from typing_extensions import TypedDict

from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages

from nodes import chatbot


class State(TypedDict):
    """
    Defines the State of the Agent Graph
    It consists of the graph schema and reducer functions applying updates to state.
    The messages key is annotated with the add_messages reducer function,
    which tells LangGraph to append new messages to the existing list, rather than overwriting it.
    State keys without an annotation will be overwritten by each update, storing the most recent value.
    """
    messages: Annotated[list, add_messages]


graph_builder = StateGraph(State)

# The first argument is the unique node name
# The second argument is the function or object that will be called whenever
# the node is used.
graph_builder.add_node("chatbot", chatbot)
