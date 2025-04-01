# Contributing

The Tableau developer community (aka DataDev) is more than welcome to contribute to this project by enhancing either the `experimental` or `pkg` folders.

# About This Project

This repository is a monorepo with two components. The main goal is to publish and support a Langchain [integration](https://python.langchain.com/docs/contributing/how_to/integrations/). This produces a need to have a development sandbox to try these solutions before publishing them for open-source use.

## Published Solutions
The `pgk` folder contains production code shipped to the [PyPi registry](https://pypi.org/project/langchain-tableau/). These are
the currently available resources:

1. `simple_datasource_qa.py`
     - Query a Published Datasource in natural language
     - Leverage the analytical engine provided by Tableau's VizQL Data Service
       - Supports aggregating, filtering and soon: calcs!
       - Scales securely by way of the API interface preventing SQL injection

## Experimental Sandbox
The `experimental` folder organizes agents, tools, utilities and notebooks for development and testing of solutions that may eventually be published ([see Published Agent Tools](#published-agent-tools)) for community use. This folder is essentially a sandbox for Tableau AI.
