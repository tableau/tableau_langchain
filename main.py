import argparse, uvicorn

from dotenv import load_dotenv

from modules import chain_config, utter, serve

# runs interactively in the terminal
def run_interactive_mode(chain):
    active_utterance = utter.get_utterance()
    while active_utterance != 'stop':
        chain.invoke(active_utterance)
        active_utterance = utter.get_utterance()

# runs as a service via Langserve
def run_api_mode(chain, host, port=8000):
    app = serve.langtab_agent(chain)
    uvicorn.run(app, host=host, port=port)


def main():
    # environment variables available to current process and sub processes
    load_dotenv()
    # runs the application in different modes: interactive & api
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
