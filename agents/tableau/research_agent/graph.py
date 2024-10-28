from langgraph.graph import StateGraph
from langgraph.prebuilt import ToolNode, tools_condition

from agents.tableau.research_agent.tooling import equip_tooling
from agents.tableau.research_agent.utils import  _visualize_graph


def graph_state(state_definition, entry_point, node):
    # Select which state definition to use
    State = state_definition

    graph_builder = StateGraph(State)
    # The first argument is the unique node name
    # The second argument is the function or object that will be called whenever the node is used.
    graph_builder.add_node(entry_point, node)

    tools = equip_tooling()
    tool_node = ToolNode(tools=tools)
    graph_builder.add_node("tools", tool_node)

    graph_builder.add_conditional_edges(
        entry_point,
        tools_condition,
    )
    # Any time a tool is called, we return to the chatbot to decide the next step
    graph_builder.add_edge("tools", entry_point)
    graph_builder.set_entry_point(entry_point)

    # creates a "CompiledGraph" we can invoke on our state
    graph = graph_builder.compile()
    # outputs a mermaid diagram of the graph in png format
    _visualize_graph(graph)

    return graph
