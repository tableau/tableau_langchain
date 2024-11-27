headlessbi_instructions = """
You are an expert at writing API request bodies for Tableau’s HeadlessBI API.
The HBI query is a JSON object that contains 2 fundamental components.
    1. columns [required] - an array of columns that define the desired output of the query
    2. filters [optional] - an array of filters to apply to the query. They can include fields that are not in the columns array.
Your task is to retrieve data relevant to a user’s natural language query.

Query as much data as might be useful; it's ok if you pull in superfluous columns,
You will be successful if you bring back all the data that could help to answer the question, even if additional transformation and actions are needed.

You can find the columnNames by checking the values of each key in the available_fields dictionary.
The keys in the available_fields dictionary are the caption names for each column.
The caption names are more likely to correspond to the user’s input, but you have to use the columnName when generating JSON.
Keep your output very structured. Use the following structure:
Reasoning:

JSON_payload:
Make sure you use this structure so that it's simple to parse the output.
Return query results verbatim so the pandas agent can analyze them.
"""

headlessbi_restrictions = """
DO NOT HALLUCINATE FIELD NAMES.
Don't try to do too much with the json query.
Only use columns based on what is listed in the available_fields dictionary.
Do not filter or reduce any data found in query results so the next link can determine future steps.
"""

headlessbi_few_shot = {
    "superstore": {
        "columns": {
            1: {
                "query": "Show me sales by segment",
                "JSON": {
                    "columns": [
                    {"columnName": "Segment"},
                    {"columnName": "Sales", "function": "SUM", "maxDecimalPlaces": 2}
                ]
                },
            },
            2: {
                "query": "What are the total sales and profit for each product category?",
                "JSON": {
                    "columns": [
                        {"columnName": "Category"},
                        {"columnName": "Sales", "function": "SUM", "maxDecimalPlaces": 2},
                        {"columnName": "Profit", "function": "SUM", "maxDecimalPlaces": 2}
                    ]
                },
            },
            3: {
                "query": "Display the number of orders by ship mode",
                "JSON": {
                    "columns": [
                        {"columnName": "Ship Mode"},
                        {"columnName": "Order ID", "function": "COUNT", "columnAlias": "Number of Orders"}
                    ]
                },
            },
            4: {
                "query": "Show me the average sales per customer by segment",
                "JSON": {
                    "columns": [
                        {"columnName": "Segment"},
                        {"columnName": "Sales", "function": "AVG", "maxDecimalPlaces": 2, "columnAlias": "Average Sales per Customer"}
                    ]
                },
            },
            5: {
                "query": "What are the total sales for each state or province?",
                "JSON": {
                    "columns": [
                        {"columnName": "State/Province"},
                        {"columnName": "Sales", "function": "SUM", "maxDecimalPlaces": 2}
                    ]
                },
            },
        },
        "filters": {
            1: {
                "query": "Show me sales for the top 10 cities",
                "JSON": {
                    "columns": [
                        {"columnName": "City"},
                        {"columnName": "Sales", "function": "SUM", "maxDecimalPlaces": 2}
                    ],
                    "filters": [
                        {
                            "columnName": "Sales",
                            "filterType": "TOP",
                            "direction": "TOP",
                            "howMany": 10,
                            "fieldToMeasure": {"columnName": "Sales", "function": "SUM"}
                        }
                    ]
                }
            },
            2: {
                "query": "What are the sales for furniture products in the last 6 months?",
                "JSON": {
                    "columns": [
                        {"columnName": "Product Name"},
                        {"columnName": "Sales", "function": "SUM", "maxDecimalPlaces": 2}
                    ],
                    "filters": [
                        {
                            "columnName": "Category",
                            "filterType": "SET",
                            "values": ["Furniture"],
                            "exclude": False
                        },
                        {
                            "columnName": "Order Date",
                            "filterType": "DATE",
                            "units": "MONTHS",
                            "pastCount": 6
                        }
                    ]
                }
            },
            3: {
                "query": "List customers who have made purchases over $1000 in the Consumer segment",
                "JSON": {
                    "columns": [
                        {"columnName": "Customer Name"},
                        {"columnName": "Sales", "function": "SUM", "maxDecimalPlaces": 2}
                    ],
                    "filters": [
                        {
                            "columnName": "Sales",
                            "filterType": "QUANTITATIVE",
                            "quantitativeFilterType": "MIN",
                            "min": 1000
                        },
                        {
                            "columnName": "Segment",
                            "filterType": "SET",
                            "values": ["Consumer"],
                            "exclude": False
                        }
                    ]
                }
            },
            4: {
                "query": "Show me the orders that were returned in the West region",
                "JSON": {
                    "columns": [
                        {"columnName": "Order ID"},
                        {"columnName": "Product Name"},
                        {"columnName": "Sales", "function": "SUM", "maxDecimalPlaces": 2}
                    ],
                    "filters": [
                        {
                            "columnName": "Returned",
                            "filterType": "SET",
                            "values": [True],
                            "exclude": False
                        },
                        {
                            "columnName": "Region",
                            "filterType": "SET",
                            "values": ["West"],
                            "exclude": False
                        }
                    ]
                }
            },
            5: {
                "query": "What are the top 5 sub-categories by sales, excluding the Technology category?",
                "JSON": {
                    "columns": [
                        {"columnName": "Sub-Category"},
                        {"columnName": "Sales", "function": "SUM", "maxDecimalPlaces": 2}
                    ],
                    "filters": [
                        {
                            "columnName": "Category",
                            "filterType": "SET",
                            "values": ["Technology"],
                            "exclude": True,
                        },
                        {
                            "columnName": "Sales",
                            "filterType": "TOP",
                            "direction": "TOP",
                            "howMany": 5,
                            "fieldToMeasure": {"columnName": "Sales", "function": "SUM"}
                        }
                    ]
                }
            },
            6: {
                "query": "Top selling sub-categories with a minimum of $200,000",
                "JSON": {
                    "columns": [
                        {"columnName": "Sub-Category"},
                        {"columnName": "Sales", "function": "SUM", "sortPriority": 1, "sortDirection": "DESC"}
                    ],
                    "filters": [
                        {"columnName": "Sales", "filterType": "QUANTITATIVE", "quantitativeFilterType": "MIN", "min": 200000}
                    ]
                }
            }
        },
        "calculations": {},
    }
}

headlessbi_prompt = {
    "instructions": headlessbi_instructions,
    "restrictions": headlessbi_restrictions,
    "user_query": "",
    "available_fields": {},
    "data_model": [],
    "vds_schema": None,
    "few_shot_examples": headlessbi_few_shot,
}
