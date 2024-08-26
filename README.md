# langtab
This projects is an initial proof of concept to introduce Tableau specific tooling to the langchain open source project. It leverages existing langchain libraries and Tableau's VizQL Data Service to generate VizQL queries from natural language questions and commands. It lays the foundation for targeted contributions to the langchain project in order to support the Tableau data dev community in building intelligent data apps and experiences on the Tableau platform. You can read more about the context for this project and planned future work here: https://docs.google.com/document/d/1eQbBqEYGL2xotTjsXTbzlNkBq_aiFow9iwN7RYA17T4/edit?usp=sharing

# Getting Started
The easiest way to get started with running the headlesscopilot query pipeline is to try it in the jupyter notebook

# Getting started with the headlesscopilot REST API
1. Perform the JSON serialization fix? /usr/local/Caskroom/mambaforge/base/envs/langtab/lib/python3.12/site-packages/langserve/serialization.py 
2. Activate the langtab conda environment - conda activate langtab
3. run python main.py --mode api and open: http://localhost:8000/headlesscopilot/playground/
Alternatively you can type python main.py to run the API from terminal 