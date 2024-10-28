# Tableau Langchain
#### Tableau tools for Agentic use cases with Langchain

This project builds Agentic tools from Tableau capabilities for use within the [Langchain](https://www.langchain.com/) and [LangGraph](https://langchain-ai.github.io/langgraph/tutorials/introduction/) frameworks.

- `query_data.py`
  - Query a Published Datasource in natural language
  - Leverage the analytical engine provided by Tableau Headless BI
    - Only the data you need
    - Supports aggregations, filters and soon: calcs!
  - Scales securely by way of the Headless BI HTTP interface preventing SQL injection
- `search_datasource.py`
  - Search for relevant Published Datasources in natural language
  - Leverage thorough datasource metadata to find the right source of information
  - Datasources are curated by Stewards in Tableau
  - Clear semantics and models built for enterprise users sharpens the output of LLM queries

</br>

Tableau [Headless BI](https://www.tableau.com/blog/vizql-data-service-beyond-visualizations) supports a variety of use cases from UIs, to automation and in particular AI Agents. By providing a simplified JSON and HTTP interface to Tableau's underlying query engine, datasources that have passed the vetting process for clarity and usefulness in answering business questions become available to Agentic systems that can register said datasources as tools for reference and analysis. From data Q&A, to decision-making, report synthesis, data analysis and agentic automation the use cases are vast.

We welcome you to explore how Agentic tools can drive alignment between your organization's data and the day to day needs of your users. Consider contributing to this project or creating your own work on a different framework, ultimately we want increase the flow of data and help people get answers from data.


## Getting Started
The easiest way to get started with running the headlesscopilot query pipeline is to try it in the jupyter notebook

### Deploy to Heroku
Use this [![Deploy](https://www.herokucdn.com/deploy/button.svg)](https://www.heroku.com/deploy)
button to build and launch this app within Heroku.  You will be prompted to set your environment (config) variables within Heroku, and then it will build and deploy the app for you.  Once the app is running, you can navigate to the app page in Heroku and find the Settings tab.  You can see the domain created for this app under the Domains section.  In order to access the API, you can make a POST request like this:

## Terminal Mode

These tools run on Python and its requirements are described in the `environment.yml` file which can be read by either [Conda](https://anaconda.org/anaconda/conda) or [Mamba](https://github.com/mamba-org/mamba) to install packages. For help installing either of them, ask [Perplexity](https://www.perplexity.ai/) for help and mention your operating system.

1 - Clone the repository
```
git clone https://github.com/Tab-SE/tableau_langchain.git
```

2 - Create a Python environment to run the code

2.1 - Using Anaconda or Miniconda
```
conda env create -f environment.yml
```

2.2 - Using Mamba
```
mamba env create -f environment.yml
```

3 - Activate your environment

3.1 - Using Anaconda or Miniconda

```
conda activate tableau_langchain
```

3.2 - Using Mamba
```
mamba activate tableau_langchain
```

4 - Duplicate file **.env.template** as **.env** and modify the values.
```
cp .env.template .env
```

5 - Run the chain in the terminal

5.1 - To run the chain interactively in the terminal
```
cd chains
python main.py
```

5.2 - To run the chain as an API service

```
cd chains
python main.py --mode api
```

6 - Type a question to the AI to see how it operates!
