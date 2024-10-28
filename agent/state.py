import os

from typing import Annotated

from typing_extensions import TypedDict

from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain_openai import ChatOpenAI

from utils import _visualize_graph


class State(TypedDict):
    """
    Defines the State of the Agent Graph
    It consists of the graph schema and reducer functions applying updates to state.
    The messages key is annotated with the add_messages reducer function,
    which tells LangGraph to append new messages to the existing list, rather than overwriting it.
    State keys without an annotation will be overwritten by each update, storing the most recent value.
    """
    messages: Annotated[list, add_messages]



def chatbot(state: State):
    """
    Graph Node
    Takes the current State as input and returns a dictionary containing an updated messages list
    under the key "messages". This is the basic pattern for all LangGraph node functions.
    """
    llm = ChatOpenAI(
        model=os.environ["AGENT_MODEL"],
        api_key=os.environ["OPENAI_API_KEY"],
        temperature=0,
        verbose=True,
        max_tokens=None,
        timeout=None,
        max_retries=2,
        # allow_dangerous_code=True,
    )

    return {"messages": [llm.invoke(state["messages"])]}


def graph_state():
    graph_builder = StateGraph(State)
    # The first argument is the unique node name
    # The second argument is the function or object that will be called whenever
    # the node is used.
    graph_builder.add_node("chatbot", chatbot)
    # tells our graph where to start its work each time we run it.
    graph_builder.add_edge(START, "chatbot")
    # instructs the graph "any time this node is run, you can exit."
    graph_builder.add_edge("chatbot", END)
    # creates a "CompiledGraph" we can invoke on our state
    graph = graph_builder.compile()
    # outputs a mermaid diagram of the graph in png format
    _visualize_graph(graph)

    return graph
