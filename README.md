# Tableau Langchain
#### Tableau tools for Agentic use cases with Langchain

This project extends the Tableau Data Platform and defines agents, tools, and chains to help developers build agentic experiences that extend the power of Tableau. 

As of today, this project builds within the within the [Langchain](https://www.langchain.com/) and [LangGraph](https://langchain-ai.github.io/langgraph/tutorials/introduction/) frameworks, but in time, it will support additional open-source agentic frameworks. 

The Project has two top-level folders: experimental and pkg. Experimental is where active development takes place. Use this folder to build and test new tools, chains, and agents, or extend the resources that are already there. The pkg folder packages up well-tested resources for inclusion in our public PyPi package: langchain-tableau. If you have a contribution to pkg, first make sure it’s included in experimental, and then reach out to Stephen Price or Joe Constantino after you post an MR. 

Main will always be the latest stable branch. 


## Getting Started
The easiest way to get started is by running the Jupyter Notebook or the main.py file, which implements a ReAct agent with access to one tool - simple_datasource_qa.

As you get more comfortable, try working with additional tools and increasing the complexity of what the Agent can do. 
