# langchain-tableau

[![PyPI version](https://badge.fury.io/py/langchain-tableau.svg)](https://badge.fury.io/py/langchain-tableau)
[![GitHub Repo](https://img.shields.io/badge/GitHub-Repository-blue?logo=github)](https://github.com/Tab-SE/tableau_langchain)

This package provides Langchain integrations for Tableau, enabling you to build Agentic tools using Tableau's capabilities within the [Langchain](https://www.langchain.com/) and [LangGraph](https://langchain-ai.github.io/langgraph/tutorials/introduction/) frameworks.

Use these tools to bridge the gap between your organization's Tableau data assets and the natural language queries of your users, empowering them to get answers directly from data through conversational AI agents.

![Tableau Logo](https://raw.githubusercontent.com/Tab-SE/tableau_langchain/main/experimental/notebooks/assets/tableau_logo_text.png)

## Installation

```bash
pip install langchain-tableau
```

## Quick Start
Here's a basic example of using the `simple_datasource_qa` tool to query a Tableau Published Datasource with a Langgraph agent:

```python
# --- Core Langchain/LangGraph Imports ---
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent

# --- langchain-tableau Imports ---
from langchain_tableau.tools.simple_datasource_qa import initialize_simple_datasource_qa

# 1. Initialize your preferred LLM
llm = ChatOpenAI(model='gpt-4o-mini', temperature=0) # Example using OpenAI

# 2. Initialize the Tableau Datasource Query tool
# Replace placeholders with your Tableau environment details
analyze_datasource = initialize_simple_datasource_qa(
    domain='[https://your-tableau-cloud-or-server.com](https://your-tableau-cloud-or-server.com)',
    site='YourTableauSiteName', # The site content URL, not the display name
    jwt_client_id='YOUR_CONNECTED_APP_CLIENT_ID',
    jwt_secret_id='YOUR_CONNECTED_APP_SECRET_ID',
    jwt_secret='YOUR_CONNECTED_APP_SECRET_VALUE',
    tableau_api_version='3.22', # Or your target REST API version
    tableau_user='user@example.com', # User context for the query
    datasource_luid='YOUR_DATASOURCE_LUID', # LUID of the Published Datasource
    tooling_llm_model='gpt-4o-mini' # LLM used internally by the tool
)

# 3. Create a list of tools for your agent
tools = [ analyze_datasource ]

# 4. Build the Agent
# This example uses a prebuilt ReAct agent from LangGraph
tableauAgent = create_react_agent(llm, tools)

# 5. Run the Agent with a question
question = 'Which states sell the most? Are those the same states with the most profits?'
messages = tableauAgent.invoke({"messages": [("human", question)]})

# Process and display the agent's response
print(messages['messages'][-1].content)
```

## Available Tools

This package currently offers the following production-ready tools:

1.  **`simple_datasource_qa`**:
    * Allows users to query a Tableau Published Datasource using natural language.
    * Leverages the analytical power of Tableau's VizQL Data Service engine for aggregation, filtering (and soon, calculations!).
    * Ensures security by interacting via Tableau's API layer, preventing direct SQL injection risks. Authentication is handled via Tableau Connected Apps (JWT).

## Learn More & Contribute

* **Full Documentation & Examples:** For detailed usage, advanced examples (including Jupyter Notebooks), contribution guidelines, and information about the experimental sandbox where new features are developed, please visit our [**GitHub Repository**](https://github.com/Tab-SE/tableau_langchain).
* **Live Demos:** See agents using Tableau in action at [EmbedTableau.com](https://www.embedtableau.com/) ([GitHub](https://github.com/Tab-SE/embedding_playbook)).

We welcome contributions! Whether it's improving existing tools, adding new ones, or enhancing documentation, please check out the [Contribution Guidelines](https://github.com/Tab-SE/tableau_langchain/blob/main/.github/CONTRIBUTING.md) on GitHub.

Let's increase the flow of data and help people get answers!
