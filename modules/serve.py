from fastapi import FastAPI
from langserve import add_routes

async def langtab_agent(chain):
    # define the server app
    app = FastAPI(
    title="LangTab Headless BI",
    version="1.0",
    description="An early demonstration of a LangChain agent querying Tableau's Headless BI service",
    )
    # use langserve to serve up the agent
    add_routes(
        app,
        chain,
        path="/headlesscopilot",
    )

    return app
