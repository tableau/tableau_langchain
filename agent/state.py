import os
import operator

from typing import Annotated

from typing_extensions import TypedDict

from langgraph.graph import StateGraph
from langgraph.graph.message import add_messages
from langchain_core.agents import AgentAction
from langchain_core.messages import BaseMessage
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import ToolNode, tools_condition

from tools import equip_tooling
from utils import  _visualize_graph

class AgentState(TypedDict):
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


class ChatbotState(TypedDict):
    """
    Defines the State of a base Chatbot
    It consists of the graph schema and reducer functions applying updates to state.
    The messages key is annotated with the add_messages reducer function,
    which tells LangGraph to append new messages to the existing list, rather than overwriting it.
    State keys without an annotation will be overwritten by each update, storing the most recent value.
    """
    messages: Annotated[list, add_messages]


def chatbot(state: ChatbotState):
    """
    Graph Node
    Takes the current State as input and returns a dictionary containing an updated messages list
    under the key "messages". This is the basic pattern for all LangGraph node functions.
    """
    llm_config = ChatOpenAI(
        model=os.environ["AGENT_MODEL"],
        api_key=os.environ["OPENAI_API_KEY"],
        temperature=0,
        verbose=True,
        max_tokens=None,
        timeout=None,
        max_retries=2,
        # allow_dangerous_code=True,
    )

    tools = equip_tooling()

    llm = llm_config.bind_tools(tools)

    return {"messages": [llm.invoke(state["messages"])]}


def graph_state():
    # Select which state definition to use
    State = ChatbotState

    graph_builder = StateGraph(State)
    # The first argument is the unique node name
    # The second argument is the function or object that will be called whenever the node is used.
    graph_builder.add_node("chatbot", chatbot)

    tools = equip_tooling()
    tool_node = ToolNode(tools=tools)
    graph_builder.add_node("tools", tool_node)

    graph_builder.add_conditional_edges(
        "chatbot",
        tools_condition,
    )
    # Any time a tool is called, we return to the chatbot to decide the next step
    graph_builder.add_edge("tools", "chatbot")
    graph_builder.set_entry_point("chatbot")

    # creates a "CompiledGraph" we can invoke on our state
    graph = graph_builder.compile()
    # outputs a mermaid diagram of the graph in png format
    _visualize_graph(graph)

    return graph
