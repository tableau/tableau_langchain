# LangTab

Integrating Tableau's [VizQL Data Service](https://www.tableau.com/blog/vizql-data-service-beyond-visualizations) with [LangChain](https://www.langchain.com/) to support Headless BI use cases via AI Agents. In other words, this project enables organizations who publish data sources to Tableau to query these sources of information via AI agents who can also perform ad-hoc analysis on demand.

This proposes a beautiful and practical marriage. One where the power of Tableau's platform for analytics aligns the human effort to understand an organization's data with the awesome capabilities of Large Language Models (LLMs) to deliver these insights to the end user. An alignment that provides tangible results that scale thanks to the support of the best analytics tooling in the world.

We welcome you to explore how LangTab can drive alignment between your organization's data and the day to day needs of your users.

## Solution

This codebase is able to run in your terminal, providing a quick and direct way to experience the Agent. It is also able to run as an API or service thanks to [LangServe](https://python.langchain.com/v0.2/docs/langserve/). It is in this latter capacity that you can integrate the Agent with custom workflows or apps.

> [!WARNING]
> There is an issue with LangServe that the developers of this repository have already addressed but it needs to be merged with the codebase itself to make the solution easy to distribute.
> Until then, running the Agent in API mode will not work or result in a response, the only part that works is the Agent performing the intended analysis.
> A PR will soon come to this page to track this improvement.

## Getting Started
The easiest way to get started with running the headlesscopilot query pipeline is to try it in the jupyter notebook

### Getting started with the headlesscopilot REST API
1. Perform the JSON serialization fix? /usr/local/Caskroom/mambaforge/base/envs/langtab/lib/python3.12/site-packages/langserve/serialization.py 
2. Activate the langtab conda environment - conda activate langtab
3. run python main.py --mode api and open: http://localhost:8000/headlesscopilot/playground/
Alternatively you can type python main.py to run the API from terminal 

## Terminal Mode

LangTab runs on Python and its requirements are described in the `environment.yml` file which can be read by either [Conda](https://anaconda.org/anaconda/conda) or [Mamba](https://github.com/mamba-org/mamba) to install packages. For help installing either of them, ask [Perplexity](https://www.perplexity.ai/) for help and mention your operating system.

1 - Clone the repository
```
git clone https://github.com/Tab-SE/langtab.git
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
conda activate langtab
```

3.2 - Using Mamba
```
mamba activate langtab
```

4 - Duplicate file **.env.template** as **.env** and modify the values.
```
cp .env.template .env
```

5 - Run the chain in the terminal

5.1 - To run the chain interactively in the terminal
```
python main.py
```

5.2 - To run the chain as an API service 

```
python main.py --mode api
```



6 - Type a question to the AI to see how it operates!

## About LangTab
LangTab was developed by Stephen Price [@stephenlprice](https://github.com/stephenlprice) and Joe Constantino [@joeconstantino](https://github.com/joeconstantino). Shout out to Patrick Green for doing the initial work to prove how you can query Headless BI from a notebook.
