async def main(env_vars):
    import json
    import uvicorn

    from langchain_openai import ChatOpenAI
    from langchain_core.prompts import ChatPromptTemplate
    from langchain_core.messages import SystemMessage
    from langchain_core.output_parsers import StrOutputParser

    from modules import metadata, prompt, utter, headless, serve
    from agents import analyst

    # defined in modules/read
    datasource_metadata = metadata.read(env_vars)
    # add datasource metadata of the connected datasource to the system prompt
    prompt['system']['data_model'] = datasource_metadata
    # load and instantiate system prompt
    headless_bi_prompt_string = json.dumps(prompt.system)

    active_utterance = utter.get_utterance()

    # Chat Model used in chain
    llm = ChatOpenAI(model="gpt-4o")

    # Langchain prompt template
    active_prompt_template = ChatPromptTemplate.from_messages([
        SystemMessage(content=headless_bi_prompt_string),
        ("user", "{utterance}")])

    prompt_value = active_prompt_template.invoke(
        {
            "utterance": active_utterance
        }
    )

    # Langchain parser
    output_parser = StrOutputParser()

    while (active_utterance != 'stop'):
        # Langchain chain
        chain = active_prompt_template | llm | output_parser
        # Invokes chain
        output = chain.invoke(active_utterance)

        payload = utter.get_payload()

        # defined in modules/send
        df = headless.query(env_vars, payload)

        instruct_header = "answer the following query directly by executing the necessary python code. Give a succinct explanation of the steps you took and how you know the answer is correct: "

        analyst.vds_analyst.invoke(instruct_header + active_utterance)
        active_utterance = utter.get_utterance()

    app = serve.langtab_agent(chain)

    uvicorn.run(app, host="localhost", port=8000)

if __name__ == "__main__":
    import os
    import asyncio
    from dotenv import load_dotenv

    load_dotenv()
    env_vars = os.environ

    asyncio.run(main(env_vars))
