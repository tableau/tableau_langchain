from dotenv import load_dotenv

from state import graph_state
from utils import _set_env, stream_graph_updates


def main():
    """
    TABLEAU HEADLESS BI AGENT

    This AI Agent provides data querying and analytics on-demand from trusted data sources
    in Tableau via the secure interface of Headless BI.
    """
    # environment variables available to current process and sub processes
    load_dotenv()

    # checks for values in .env, else prompts user before initializing
    _set_env('OPENAI_API_KEY')
    _set_env('TABLEAU_DOMAIN')
    _set_env('SITE_NAME')
    _set_env('DATA_SOURCE')
    _set_env('TAVILY_API_KEY')
    _set_env('PINECONE_API_KEY')
    _set_env('PINECONE_ENVIRONMENT')
    _set_env('PINECONE_INDEX_NAME')



    # LangGraph Agents rely on graphs to describe state
    graph = graph_state()

    # User input loop
    while True:
        try:
            user_input = input("User: ")
            if user_input.lower() in ["quit", "exit", "q", "stop"]:
                print("Exiting Tableau Headless BI Agent...")
                print("Goodbye!")
                break

            stream_graph_updates(user_input, graph)
        except:
            # fallback if input() is not available
            user_input = "average discount, total sales, profits by region"
            print("User: " + user_input)
            stream_graph_updates(user_input, graph)
            break

if __name__ == "__main__":
    main()
