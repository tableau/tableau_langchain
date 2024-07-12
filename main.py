import argparse
import json
import uvicorn
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import SystemMessage
from langchain_core.output_parsers import StrOutputParser

from modules import metadata, utter, headless, serve
from agents import analyst
from prompts import nlq_to_vds

def create_chain(env_vars):
    datasource_metadata = metadata.read(env_vars)
    nlq_to_vds.prompt['data_model'] = datasource_metadata
    headless_bi_prompt_string = json.dumps(nlq_to_vds.prompt)

    llm = ChatOpenAI(model="gpt-4")

    active_prompt_template = ChatPromptTemplate.from_messages([
        SystemMessage(content=headless_bi_prompt_string),
        ("user", "{utterance}")
    ])

    output_parser = StrOutputParser()
    chain = active_prompt_template | llm | output_parser
    return chain

def run_interactive_mode(chain, env_vars):
    active_utterance = utter.get_utterance()
    while active_utterance != 'stop':
        output = chain.invoke(active_utterance)
        payload = utter.get_payload(output)
        df = headless.query(env_vars, payload)

        instruct_header = "Answer the following query directly by executing the necessary python code. Give a succinct explanation of the steps you took and how you know the answer is correct: "
        vds_analyst = analyst.vds_analyst(df)
        vds_analyst.invoke(instruct_header + active_utterance)
        active_utterance = utter.get_utterance()

def run_api_mode(chain, host, port=8000):
    app = serve.langtab_agent(chain)
    uvicorn.run(app, host=host, port=port)

def main():
    parser = argparse.ArgumentParser(description="Run the NLQ2VDS agent in interactive or API mode.")
    parser.add_argument("--mode", choices=["interactive", "api"], default="interactive", help="Run mode: interactive or api")
    parser.add_argument("--host", default="localhost", help="Host for API mode")
    parser.add_argument("--port", type=int, default=8000, help="Port for API mode")
    args = parser.parse_args()

    env_vars = load_environment_variables()
    chain = create_chain(env_vars)

    if args.mode == "interactive":
        run_interactive_mode(chain, env_vars)
    else:
        run_api_mode(chain, args.host, args.port)

def load_environment_variables():
    from dotenv import load_dotenv
    import os
    load_dotenv()
    return os.environ

if __name__ == "__main__":
    main()

# def main(env_vars):
#     import json
#     import uvicorn

#     from langchain_openai import ChatOpenAI
#     from langchain_core.prompts import ChatPromptTemplate
#     from langchain_core.messages import SystemMessage
#     from langchain_core.output_parsers import StrOutputParser

#     from modules import metadata, utter, headless, serve
#     from agents import analyst
#     from prompts import nlq_to_vds

#     # defined in modules/read
#     datasource_metadata = metadata.read(env_vars)
#     # add datasource metadata of the connected datasource to the system prompt
#     nlq_to_vds.prompt['data_model'] = datasource_metadata
#     # load and instantiate system prompt
#     headless_bi_prompt_string = json.dumps(nlq_to_vds.prompt)

#     active_utterance = utter.get_utterance()

#     # Chat Model used in chain
#     llm = ChatOpenAI(model="gpt-4")

#     # Langchain prompt template
#     active_prompt_template = ChatPromptTemplate.from_messages([
#         SystemMessage(content=headless_bi_prompt_string),
#         ("user", "{utterance}")])

#     prompt_value = active_prompt_template.invoke(
#         {
#             "utterance": active_utterance
#         }
#     )

#     # Langchain parser
#     output_parser = StrOutputParser()

#     while (active_utterance != 'stop'):
#         # Langchain chain
#         chain = active_prompt_template | llm | output_parser
#         # Invokes chain
#         output = chain.invoke(active_utterance)

#         payload = utter.get_payload(output)

#         # defined in modules/send
#         df = headless.query(env_vars, payload)

#         instruct_header = "answer the following query directly by executing the necessary python code. Give a succinct explanation of the steps you took and how you know the answer is correct: "

#         analyst.vds_analyst.invoke(instruct_header + active_utterance)
#         active_utterance = utter.get_utterance()

#     app = serve.langtab_agent(chain)

#     uvicorn.run(app, host="localhost", port=8000)

# if __name__ == "__main__":
#     import os
#     from dotenv import load_dotenv

#     load_dotenv()
#     env_vars = os.environ

#     main(env_vars)
