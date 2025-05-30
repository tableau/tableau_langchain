
import os
import json

from IPython.display import Image, display


def _visualize_graph(graph):
    """
    Creates a mermaid visualization of the State Graph in .png format
    """

    # Attempt to generate and save PNG
    try:
        png_data = graph.get_graph().draw_mermaid_png()
        filename = "graph_visualization.png"
        with open(filename, "wb") as f:
            f.write(png_data)

        if os.path.exists(filename):
            file_size = os.path.getsize(filename)
            print(f"Agent Graph saved as '{filename}' | file size: {file_size} bytes")


            display(Image(png_data))
        else:
            print(f"Failed to create file '{filename}'")
    except Exception as e:
        print(f"Failed to generate PNG: {str(e)}")


async def stream_graph_updates(message: dict, graph):
    """
    This function streams responses from Agents to clients, such as chat interfaces, by processing
    user inputs and dynamically updating the conversation.

    The function takes a string input from the user and passes it to the state graph's streaming interface.
    It initiates a stream of events based on the provided user input, which is wrapped in a dictionary with
    a key "messages" containing a tuple of the user role and content.

    As each event is generated by the graph, the function iterates over the values returned. Within each event,
    it specifically looks for messages associated with the 'messages' key. The function extracts and prints the
    content of the last message in the sequence, which is assumed to be the assistant's most recent response.
    This enables a real-time conversation-like interaction where responses are generated and displayed immediately
    based on user input.

    if debugging is enabled (checked via an environment variable), it prints out the content of the last message
    for further inspection.

    Parameters:
    - message (dict): contains a string with the user_message and additional operating parameters
    - graph: a representation of the agents behavior and tool set

    Returns:
    - None. The function's primary side effect is to print the assistant's response to the console.
    """

    message_string = json.dumps(message['user_message'])

    tableau_credentials = message['agent_inputs']['tableau_credentials']
    datasource = message['agent_inputs']['datasource']

    # this is how client apps should format their requests to the Agent API
    input_stream = {
        "messages": [("user", message_string)],
        "tableau_credentials": tableau_credentials,
        "datasource": datasource
    }

    # gets value DEBUG value or sets it to empty string, condition applies if string is empty or 0
    if os.environ.get("DEBUG", "") in ["0", ""]:
        # streams events from the agent graph started by the client input containing user queries
        async for event in graph.astream(input_stream):
            agent_output = event.get('agent')
            if event.get('agent'):
                agent_message = agent_output["messages"][0].content
                if len(agent_message) > 0:
                    print("\nAgent:")
                    print(f"{agent_message} \n")

    elif (os.environ["DEBUG"] == "1"):
        # display tableau credentials to prove access to the environment
        print('*** tableau_credentials ***', message.get('tableau_credentials'))

        async for event in graph.astream(input_stream):
            print(f"*** EVENT *** type: {type(event)}")
            print(event)
