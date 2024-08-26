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

LangTab runs on Python and its requirements are described in the `environment.yml` file which can be read by either [Mamba](https://github.com/mamba-org/mamba) or [Conda](https://anaconda.org/anaconda/conda) to install packages. For help installing either of them, ask [Perplexity](https://www.perplexity.ai/) for help and mention your operating system.

1. Clone the repository
2. Create a Python environment to run the code

Mamba
```
mamba env create -f environment.yml
```

Conda
```
conda env create -f environment.yml
```

3. Activate your environment

Mamba
```
mamba activate myenv
```

Conda
```
conda activate myenv
```

4. Run the app in the terminal

Python
```
python main.py
```

5. Type a question to the AI to see how it operates

## About LangTab
LangTab was developed by Stephen Price [@stephenlprice](https://github.com/stephenlprice) and [@joeconstantino](https://github.com/joeconstantino). Shout out to Patrick Green for doing the initial work to prove how you can query Headless BI from a notebook.

This cookbook can be configured to query a Tableau Published data source in natural language using the Headless BI REST endpoint. It uses langchain libraries and the langchain development framework to generate a headless BI request payload from a natural language input query. It then executes a chain to generate an answer to the user's input query.
