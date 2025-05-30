# Tableau Langchain

[![Community Supported](https://img.shields.io/badge/Support%20Level-Community%20Supported-457387.svg)](https://www.tableau.com/support-levels-it-and-developer-tools)
[![PyPI version](https://badge.fury.io/py/langchain-tableau.svg)](https://badge.fury.io/py/langchain-tableau)
[![GitHub Repo](https://img.shields.io/badge/GitHub-Repository-blue?logo=github)](https://github.com/Tab-SE/tableau_langchain)

This project builds Agentic tools from Tableau capabilities for use within the [Langchain](https://www.langchain.com/) and [LangGraph](https://langchain-ai.github.io/langgraph/tutorials/introduction/) frameworks. Solutions such as Tools, Utilities, and Chains are published to the PyPi registry under [langchain-tableau](https://pypi.org/project/langchain-tableau/) following conventions for [integrations](https://python.langchain.com/docs/contributing/how_to/integrations/) to Langchain.

> [!IMPORTANT]
> On May 27 2025 this project was moved from the Tableau Solution Engineering GitHub organization to the main Tableau OSS one:
> * from: https://github.com/Tab-SE/tableau_langchain
> * to: https://github.com/tableau/tableau_langchain
>
> Everything should be moved over intact and everyone should still have the same access.
>
> All links to the previous location should automatically redirect to the new location. If you have a copy of this project cloned locally, we recommend updating to point to the new location:
>
> ```sh
> git remote set-url origin https://github.com/tableau/tableau_langchain
> ```


![tableau logo](experimental/notebooks/assets/tableau_logo_text.png)

```bash
pip install langchain-tableau
```

We'd like you to explore how Agentic tools can drive alignment between your organization's data and the day-to-day needs of your users. Consider contributing to this project or creating your own work on a different framework, ultimately we seek to increase the flow of data and help people get answers from it.

To see live demos of Agents using Tableau, visit:
- [EmbedTableau.com](https://www.embedtableau.com/) | [Github Repository](https://github.com/Tab-SE/embedding_playbook)

</br>

# Table of Contents
- [Tableau Langchain](#tableau-langchain)
- [Table of Contents](#table-of-contents)
- [Getting Started](#getting-started)
  - [Published Solutions](#published-solutions)
  - [Experimental Sandbox](#experimental-sandbox)
- [About This Project](#about-this-project)
  - [Published Solutions](#published-solutions-1)
  - [Experimental Sandbox](#experimental-sandbox-1)
  - [Security](#security)
- [Contributing](#contributing)

![area chart](experimental/notebooks/assets/vizart/area_chart_banner.png)

# Getting Started

The easiest way to start with `tableau_langchain` is to try the Jupyter Notebooks in the `experimental/notebooks/` folder. These examples will guide you through different use cases and scenarios with increasing complexity.

## Published Solutions

To use the solutions available at [langchain-tableau](https://pypi.org/project/langchain-tableau/) in notebooks and your code, do the following:

1. Install `langchain-tableau`

   ```bash
   pip install langchain-tableau
   ```
2. Import `langchain-tableau` and use it with your Agent (in a Python file or Jupyter Notebook)

   ```python
    # langchain and langgraph package imports
    from langchain_openai import ChatOpenAI
    from langgraph.prebuilt import create_react_agent
    # langchain_tableau imports
    from langchain_tableau.tools.simple_datasource_qa import initialize_simple_datasource_qa

    # initialize an LLM
    llm = ChatOpenAI(model='gpt-4o-mini', temperature=0)

    # initalize `simple_datasource_qa` for querying a Tableau Published Datasource through VDS
    analyze_datasource = initialize_simple_datasource_qa(
        domain='https://your-tableau-cloud-or-server.com',
        site='Tableau site name',
        jwt_client_id='from an enabled Tableau Connected App',
        jwt_secret_id='from an enabled Tableau Connected App',
        jwt_secret='from an enabled Tableau Connected App',
        tableau_api_version='Tableau REST API version',
        tableau_user='user to query the Agent with',
        datasource_luid='unique data source ID can be obtained via REST or Metadata APIs',
        tooling_llm_model='model to use for the data query tool'
    )

    # Add the tool to the array of tools used by the Agent
    tools = [ analyze_datasource ]

    # Build the Agent using the minimum components (LLM + Tools)
    tableauAgent = create_react_agent(llm, tools)

    # Run the Agent
    messages = tableauAgent.invoke({"messages": [("human",'which states sell the most? Are those the same states with the most profits?')]})
   ```

</br>

## Experimental Sandbox

To develop and test solutions for the `langchain-tableau` package, this repository contains an `experimental/` folder organizing Agents, Tools, Utilities and other files that allow contributors to improve the solutions made available to the open-source community.

To use the sandbox, do the following:

1. Clone the repository

    ```bash
    git clone https://github.com/Tab-SE/tableau_langchain.git
    ```

2. Create a Python environment to isolate project dependencies (optional)

   Note: This example uses `conda` (`environment.yml` file provided). If you use `conda` skip to step #4 since dependencies will already be installed. Other environment management systems should also work (`poetry`,  `venv`, `mamba` etc.)

    ```bash
    conda env create -f environment.yml
    conda activate tableau_langchain
    ```

3. Install project dependencies (use this to install anytime with or without isolated Python environments)

    Note: dependencies are listed in the `pyproject.toml` file

    ```bash
    pip install .
    ```

    You must also install the `langgraph-cli` developer dependency to run the Langgraph Server (see [langgraph-cli](https://langchain-ai.github.io/langgraph/cloud/reference/cli))

    ```bash
    pip install langgraph-cli
    ```

    If you wish to run the Langgraph Server in local development mode, you will need the `inmem` extra (see [langgraph dev](https://langchain-ai.github.io/langgraph/cloud/reference/cli/#dev) command)

    ```bash
    pip install -U "langgraph-cli[inmem]"
    ```

4. Declare Environment Variables

    Start by duplicating the template file:

    ```bash
    cp .env.template .env
    ```

    Replace the values in the `.env` file with your own. These values are secure and never published to Github

5. Run an Agent in the terminal

    ```bash
    python main.py
    ```

6. Run the Langgraph Server API (see [langgraph-cli](https://langchain-ai.github.io/langgraph/cloud/reference/cli/#commands))

    Note: Docker Desktop must also be running

    Local Development
    ```bash
    langgraph dev
    ```

    Docker Container
    ```bash
    langgraph build
    langgraph up
    ```

![dual axis area chart](experimental/notebooks/assets/vizart/up_down_area.png)

# About This Project

This repository is a monorepo with two components. The main goal is to publish and support a Langchain [integration](https://python.langchain.com/docs/contributing/how_to/integrations/). This produces a need to have a development sandbox to try these solutions before publishing them for open-source use.

The code base has two top-level folders: `experimental/` and `pkg/`. Experimental is where active development takes place. Use this folder to build and test new tools, chains, and agents, or extend the resources that are already there. The `pkg/` folder packages up well-tested resources for inclusion in our public PyPi package: `langchain-tableau`. If you have a contribution to `pkg/`, first make sure it’s been tested in experimental, and then submit your PR via GitHub.

The `main` branch will always be the latest stable branch.

## Published Solutions
The `pgk` folder contains production code shipped to the [PyPi registry](https://pypi.org/project/langchain-tableau/).
These are available resources:

1. `simple_datasource_qa.py`
     - Query a Published Datasource in natural language
     - Leverage the analytical engine provided by Tableau's VizQL Data Service
       - Supports aggregating, filtering, and soon: calcs!
       - Scales securely by way of the API interface, preventing SQL injection

## Experimental Sandbox
The `experimental` folder organizes agents, tools, utilities, and notebooks for developing and solution testing that may eventually be published ([see Published Agent Tools](#published-agent-tools)) for community use. This folder is a sandbox for Tableau AI.

## Security

Tableau resources are accessed via supported authentication methods such as Connected Apps. Secrets, keys and other credentials used to access Tableau should not be published to Github and instead stored securely via `.env` files. See step #4 in the [Getting Started](#getting-started) section.

Learn more by reading our [Security](.github/SECURITY.md) article.

# Contributing

The Tableau developer community (aka DataDev) is more than welcome to contribute to this project by enhancing either the `experimental` or `pkg` folders.

This is the founding team for the project. Please consider contributing in your own way to further what's possible when you combine Tableau with AI Agents.

* Stephen Price [@stephenlprice](https://github.com/stephenlprice) - Architect
* Joe Constantino [@joeconstantino](https://github.com/joeconstantino) - Product Manager
* Joseph Fluckiger [@josephflu](https://github.com/josephflu) - Lead Developer
* Will Sutton [@wjsutton](https://github.com/wjsutton) - Developer
* Cristian Saavedra [@cristiansaavedra](https://github.com/cristiansaavedra) - Developer
* Antoine Issaly [@antoineissaly](https://github.com/antoineissaly) - Developer

If you wish to contribute to this project, please refer to our [Contribution Guidelines](CONTRIBUTING.md).
Also, check out the [Code of Conduct](CODE_OF_CONDUCT.md).

![datadev](experimental/notebooks/assets/datadev.png)
