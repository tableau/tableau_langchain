import argparse, uvicorn

from dotenv import load_dotenv

from modules import chain_config, serve

# runs interactively in the terminal
def run_interactive_mode(chain):
    active_utterance = get_utterance()
    while active_utterance != 'stop':
        interaction = chain.invoke(active_utterance)
        print("******", interaction, "******")
        active_utterance = get_utterance()

# runs as a service via Langserve
def run_api_mode(chain, host, port=8000):
    app = serve.query_data(chain)
    uvicorn.run(app, host=host, port=port)

# prompts the user to continue asking questions
def get_utterance():
    query = input('What would you like to know about your data? Reply with "stop" if you are done.\n')
    return query

def main():
    # environment variables available to current process and sub processes
    load_dotenv()
    # runs the application in different modes: interactive (default) & api with optional arguments
    parser = argparse.ArgumentParser(description="Run the NLQ2VDS agent in interactive or API mode.")
    parser.add_argument("--mode", choices=["interactive", "api"], default="interactive", help="Run mode: interactive or api")
    parser.add_argument("--host", default="localhost", help="Host for API mode")
    parser.add_argument("--port", type=int, default=8000, help="Port for API mode")
    args = parser.parse_args()

    chain = chain_config.create_chain()

    if args.mode == "interactive":
        run_interactive_mode(chain)
    else:
        run_api_mode(chain, args.host, args.port)

if __name__ == "__main__":
    main()
