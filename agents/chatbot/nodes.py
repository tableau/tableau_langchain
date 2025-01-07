import os

from langgraph.prebuilt import ToolNode
from langchain_openai import ChatOpenAI

from agents.chatbot.state import ChatbotState
from agents.chatbot.tooling import equip_tooling


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

    message = llm.invoke(state["messages"])
    content = message.content

    if content:
        print('Chatbot: \n', message.content)

    return {"messages": [message]}

def tools():
    tool_node = ToolNode(tools=equip_tooling())
    return tool_node
