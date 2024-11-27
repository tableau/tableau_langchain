from fastapi import FastAPI

from langserve import add_routes

def query_data(chain):
    # define the server app
    app = FastAPI(
    title="Tableau AI Data Query",
    version="1.0",
    description="A tool for querying data sources via Tableau Headless BI on-demand using natural language",
    )
    # use langserve to serve up the endpoint
    add_routes(
        app,
        chain,
        path="/query_data",
    )

    return app
