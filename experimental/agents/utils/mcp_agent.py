import os
import json
from typing import Dict, Any, List, Optional, TypedDict, Annotated, Callable
import asyncio
from pydantic import BaseModel, Field

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import Runnable, RunnableConfig
from langchain_core.output_parsers import StrOutputParser

from langgraph.graph import StateGraph, END
# Using a custom ToolExecutor implementation since the import is problematic

class ToolExecutor:
    """Execute tools and return their output."""

    def __init__(self, tools):
        """Initialize with tools."""
        self.tools = {tool.name: tool for tool in tools}

    def __call__(self, state):
        """Execute a tool and return its output."""
        tool_name = state.get("tool")
        tool_input = state.get("tool_input", {})

        if not tool_name or tool_name not in self.tools:
            return {"messages": state.get("messages", []) + [AIMessage(content="I don't know how to use that tool.")]}

        tool = self.tools[tool_name]
        try:
            result = tool(**tool_input)
            return {"messages": state.get("messages", []) + [AIMessage(content=f"Tool result: {result}")]}
        except Exception as e:
            return {"messages": state.get("messages", []) + [AIMessage(content=f"Error using {tool_name}: {str(e)}")]}

from experimental.utilities.mcp_client import MCPClient
from experimental.utilities.mcp_chat import get_system_prompt

class AgentState(TypedDict):
    """State for the agent."""
    messages: List[Dict[str, Any]]
    user_message: str
    agent_inputs: Dict[str, Any]

class MCPAgentBuilder:
    """
    Builder for creating MCP-backed agents that use direct MCP tool calls.
    """

    def __init__(
        self,
        mcp_url: Optional[str] = None,
        system_prompt: Optional[str] = None,
        model_name: Optional[str] = None,
        agent_identity: Optional[str] = None
    ):
        """Initialize the agent builder."""
        self.mcp_url = mcp_url or os.getenv('TABLEAU_MCP_URL',
                                           'https://tableau-mcp-bierschenk-2df05b623f7a.herokuapp.com/tableau-mcp')
        self.mcp_client = MCPClient(self.mcp_url)
        self.system_prompt = system_prompt or get_system_prompt()
        self.model_name = model_name or os.getenv('TOOLING_MODEL', 'gpt-4o')
        self.agent_identity = agent_identity or ""

        # Add agent identity to system prompt if provided
        if self.agent_identity:
            self.system_prompt = f"{self.agent_identity}\n\n{self.system_prompt}"

    def build_agent_executor(self) -> Runnable:
        """Build the agent executor."""
        # Initialize MCP client
        self.mcp_client.connect()

        # Create tool executor for MCP tools
        tools = []
        for tool in self.mcp_client.tools_cache.get('tools', []):
            tools.append(MCPToolWrapper(
                name=tool.get('name', ''),
                description=tool.get('description', ''),
                mcp_client=self.mcp_client
            ))

        tool_executor = ToolExecutor(tools)

        # Define agent state graph
        workflow = StateGraph(AgentState)

        # Define nodes
        workflow.add_node("agent", self._create_agent())
        workflow.add_node("action", tool_executor)

        # Define edges with simple routing
        workflow.add_edge("agent", "action")
        workflow.add_edge("action", "agent")
        workflow.add_edge("agent", END)

        # Set entry point
        workflow.set_entry_point("agent")

        # Compile the graph
        return workflow.compile()

    def _create_agent(self) -> Callable:
        """Create the agent function."""
        # This is a placeholder for the actual LLM integration
        # In a real implementation, you would:
        # 1. Create a prompt template
        # 2. Create an LLM chain
        # 3. Parse the output for tool calls

        async def agent_fn(state: AgentState, config: Optional[RunnableConfig] = None) -> Dict:
            """Agent function that processes messages and decides next actions."""
            messages = state.get("messages", [])

            # For testing purposes, we'll simulate a simple response
            # In a real implementation, you would call the LLM here

            # Get the user's message
            user_message = state.get("user_message", "")

            # Create a simulated response
            response = f"I received your question: '{user_message}'. Here's what I found using Tableau MCP:"

            # For a datasource question, simulate listing datasources
            if "datasource" in user_message.lower():
                try:
                    datasources = self.mcp_client.call_tool("list-datasources", {})
                    if isinstance(datasources, dict) and 'data' in datasources:
                        datasources = datasources['data']

                    ds_names = [d.get('name', 'Unknown') if isinstance(d, dict) else str(d) for d in datasources]
                    response += f"\n\nAvailable datasources: {', '.join(ds_names)}"
                except Exception as e:
                    response += f"\n\nError listing datasources: {str(e)}"

            # Return the final response
            return {"messages": messages + [AIMessage(content=response)]}

        return agent_fn

class MCPToolWrapper:
    """Wrapper for MCP tools to use with LangGraph."""

    def __init__(self, name: str, description: str, mcp_client: MCPClient):
        """Initialize the tool wrapper."""
        self.name = name
        self.description = description
        self.mcp_client = mcp_client

    def __call__(self, **kwargs) -> str:
        """Call the MCP tool."""
        try:
            result = self.mcp_client.call_tool(self.name, kwargs)
            return json.dumps(result)
        except Exception as e:
            return f"Error calling {self.name}: {str(e)}"

def create_mcp_agent(
    agent_identity: Optional[str] = None,
    system_prompt: Optional[str] = None,
    mcp_url: Optional[str] = None
) -> Runnable:
    """Create an MCP agent with the given parameters."""
    builder = MCPAgentBuilder(
        mcp_url=mcp_url,
        system_prompt=system_prompt,
        agent_identity=agent_identity
    )
    return builder.build_agent_executor()
