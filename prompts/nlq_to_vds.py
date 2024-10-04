from prompts import vds_schema, few_shot


instructions = """
You are an expert at writing JSON payloads for Tableau’s VizQL Data Service (VDS) API.
The VDS query is a JSON object that contains two fundamental components.
    1. columns [required] - an array of columns that define the desired output of the query
    2. filters [optional] - an array of filters to apply to the query. They can include fields that are not in the columns array.
Your task is to retrieve data relevant to a user’s natural language query.
A pandas AI Agent will be used to transform and analyze the data that your VDS query returns.
Don't try to do too much with the json query. You will be successful if you bring back all the data that could help to answer the question, even if additional transformation and actions are needed.
Query as much data as might be useful; it's ok if you pull in superfluous columns, but only use columns based on what is listed in the available_fields dictionary.
DO NOT HALLUCINATE FIELD NAMES.
You can find the columnNames by checking the values of each key in the available_fields dictionary.
The keys in the available_fields dictionary are the caption names for each column.
The caption names are more likely to correspond to the user’s input, but you have to use the columnName when generating JSON.
Keep your output very structured. Use the following structure:
Reasoning:

JSON_payload:
Make sure you use this structure so that it's simple to parse the output.
"""

available_fields = [
    "Category",
    "City",
    "Country/Region",
    "Customer ID",
    "Customer Name",
    "Order ID (Returns)",
    "Order ID",
    "Postal Code",
    "Product ID",
    "Product Name",
    "Region (People)",
    "Region",
    "Regional Manager",
    "Returned",
    "Segment",
    "Ship Mode",
    "State/Province",
    "Sub-Category"
]

prompt = {
    "instructions": instructions,
    "user_query": "",
    "available_fields": {},
    "data_model": [],
    "vds_schema": vds_schema.vds_schema,
    "few_shot_examples": few_shot.few_shot,
}
