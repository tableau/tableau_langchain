FROM langchain/langgraph-api:3.12



RUN PYTHONDONTWRITEBYTECODE=1 pip install --no-cache-dir -c /api/constraints.txt pyproject.toml

# -- Adding local package . --
ADD . /deps/tableau_langchain
# -- End of local package . --

# -- Installing all local dependencies --
RUN PYTHONDONTWRITEBYTECODE=1 pip install --no-cache-dir -c /api/constraints.txt -e /deps/*
# -- End of local dependencies install --

# Define multiple graphs: endpoint_name: path/to/module.py:graph_variable
ENV LANGSERVE_GRAPHS='{ \
    "superstore": "/deps/tableau_langchain/experimental/agents/demos/superstore/agent.py:analytics_agent", \
    # "another": "/deps/tableau_langchain/path/to/another_agent.py:some_other_graph_app" \
}'
#  ^--- Start JSON object      ^--- First key-value pair        ^--- Comma separator      ^--- Second key-value pair    ^--- End JSON object

WORKDIR /deps/tableau_langchain
