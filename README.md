# langtab
Integrating langchain with VDS

# About the cookbook
This cookbook was created by Joe Constantino on June 25, 2024. Shout out to Patrick Green for doing the initial work to prove how you can query Headless BI from a notebook.

This cookbook can be configured to query a Tableau Published data source in natural language using the Headless BI REST endpoint. It uses langchain libraries and the langchain development framework to generate a headless BI request payload from a natural language input query. It then executes a chain to generate an answer to the user's input query.
