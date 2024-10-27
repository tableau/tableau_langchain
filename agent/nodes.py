import os

from langchain_openai import ChatOpenAI

from state_graph import State


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

def chatbot(state: State):
    """
    Takes the current State as input and returns a dictionary containing an updated messages list
    under the key "messages". This is the basic pattern for all LangGraph node functions.
    """
    return {"messages": [llm.invoke(state["messages"])]}
