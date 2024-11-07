few_shot = {
    "superstore": {
        "columns": {
            1: {
                "query": "Show me sales by segment",
                "JSON": {
                    "fields": [
                    {"fieldCaption": "Segment"},
                    {"fieldCaption": "Sales", "function": "SUM", "maxDecimalPlaces": 2}
                ]
                },
            },
            2: {
                "query": "What are the total sales and profit for each product category?",
                "JSON": {
                    "fields": [
                        {"fieldCaption": "Category"},
                        {"fieldCaption": "Sales", "function": "SUM", "maxDecimalPlaces": 2},
                        {"fieldCaption": "Profit", "function": "SUM", "maxDecimalPlaces": 2}
                    ]
                },
            },
            3: {
                "query": "Display the number of orders by ship mode",
                "JSON": {
                    "fields": [
                        {"fieldCaption": "Ship Mode"},
                        {"fieldCaption": "Order ID", "function": "COUNT", "columnAlias": "Number of Orders"}
                    ]
                },
            },
            4: {
                "query": "Show me the average sales per customer by segment",
                "JSON": {
                    "fields": [
                        {"fieldCaption": "Segment"},
                        {"fieldCaption": "Sales", "function": "AVG", "maxDecimalPlaces": 2, "columnAlias": "Average Sales per Customer"}
                    ]
                },
            },
            5: {
                "query": "What are the total sales for each state or province?",
                "JSON": {
                    "fields": [
                        {"fieldCaption": "State/Province"},
                        {"fieldCaption": "Sales", "function": "SUM", "maxDecimalPlaces": 2}
                    ]
                },
            },
        },
        "filters": {
            1: {
                "query": "Show me sales for the top 10 cities",
                "JSON": {
                    "fields": [
                        {"fieldCaption": "City"},
                        {"fieldCaption": "Sales", "function": "SUM", "maxDecimalPlaces": 2}
                    ],
                    "filters": [
                        {
                            "fieldCaption": "Sales",
                            "filterType": "TOP",
                            "direction": "TOP",
                            "howMany": 10,
                            "fieldToMeasure": {"fieldCaption": "Sales", "function": "SUM"}
                        }
                    ]
                }
            },
            2: {
                "query": "What are the sales for furniture products in the last 6 months?",
                "JSON": {
                    "fields": [
                        {"fieldCaption": "Product Name"},
                        {"fieldCaption": "Sales", "function": "SUM", "maxDecimalPlaces": 2}
                    ],
                    "filters": [
                        {
                            "fieldCaption": "Category",
                            "filterType": "SET",
                            "values": ["Furniture"],
                            "exclude": False
                        },
                        {
                            "fieldCaption": "Order Date",
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
                    "fields": [
                        {"fieldCaption": "Customer Name"},
                        {"fieldCaption": "Sales", "function": "SUM", "maxDecimalPlaces": 2}
                    ],
                    "filters": [
                        {
                            "fieldCaptione": "Sales",
                            "filterType": "QUANTITATIVE",
                            "quantitativeFilterType": "MIN",
                            "min": 1000
                        },
                        {
                            "fieldCaption": "Segment",
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
                    "fields": [
                        {"fieldCaption": "Order ID"},
                        {"fieldCaption": "Product Name"},
                        {"fieldCaption": "Sales", "function": "SUM", "maxDecimalPlaces": 2}
                    ],
                    "filters": [
                        {
                            "fieldCaption": "Returned",
                            "filterType": "SET",
                            "values": [True],
                            "exclude": False
                        },
                        {
                            "fieldCaption": "Region",
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
                    "fields": [
                        {"fieldCaption": "Sub-Category"},
                        {"fieldCaption": "Sales", "function": "SUM", "maxDecimalPlaces": 2}
                    ],
                    "filters": [
                        {
                            "fieldCaption": "Category",
                            "filterType": "SET",
                            "values": ["Technology"],
                            "exclude": True,
                        },
                        {
                            "fieldCaption": "Sales",
                            "filterType": "TOP",
                            "direction": "TOP",
                            "howMany": 5,
                            "fieldToMeasure": {"fieldCaption": "Sales", "function": "SUM"}
                        }
                    ]
                }
            },
            6: {
                "query": "Top selling sub-categories with a minimum of $200,000",
                "JSON": {
                    "fields": [
                        {"fieldCaption": "Sub-Category"},
                        {"fieldCaption": "Sales", "function": "SUM", "sortPriority": 1, "sortDirection": "DESC"}
                    ],
                    "filters": [
                        {"fieldCaption": "Sales", "filterType": "QUANTITATIVE", "quantitativeFilterType": "MIN", "min": 200000}
                    ]
                }
            }
        },
        "calculations": {},
    }
}

instructions = """
You are an expert at writing API request bodies for Tableau’s HeadlessBI API.
The HBI query is a JSON object that contains 2 fundamental components.
    1. fields [required] - an array of fields that define the desired output of the query
    2. filters [optional] - an array of filters to apply to the query. They can include fields that are not in the fields array.
Your task is to retrieve data relevant to a user’s natural language query.

Query as much data as might be useful; it's ok if you pull in superfluous fields,
You will be successful if you bring back all the data that could help to answer the question, even if additional transformation and actions are needed.

You can find the fieldCaptions by checking the data_model field.
Keep your output very structured. Use the following structure:
Reasoning:

JSON_payload:
Make sure you use this structure so that it's simple to parse the output.
Return query results verbatim so the pandas agent can analyze them.
"""

restrictions = """
DO NOT HALLUCINATE FIELD NAMES.
Don't try to do too much with the json query.
Only use fields based on what is listed in the data_model
Do not filter or reduce any data found in query results so the next link can determine future steps.
"""

vds_schema = {
    "fields": {
        "type": "object",
        "anyOf": [
            {
                "required": [
                    "fieldCaption"
                ]
            },
            {
                "required": [
                    "fieldCaption",
                    "function"
                ]
            },
            {
                "required": [
                    "columnName",
                    "calculation"
                ]
            }
        ],
        "properties": {
            "fieldCaption": {
                "type": "string",
                "description": "The name of the column which must be supplied."
            },
            "maxDecimalPlaces": {
                "type": "integer",
                "description": "The maximum number of decimal places. Any trailing 0s will be dropped. The maxDecimalPlaces value must be greater or equal to 0."
            },
            "sortDirection": {
                "allOf": [
                    {
                        "$ref": "#/components/schemas/SortDirection"
                    },
                    {
                        "description": "The direction of the sort, either ascending or descending. If not supplied the default is ascending"
                    }
                ]
            },
            "sortPriority": {
                "type": "integer",
                "description": "To enable sorting on a specific Column provide a sortPriority for that field, and that field will be sorted. The sortPriority provides a ranking of how to sort fields when multiple fields are being sorted. The highest priority (lowest number) field is sorted first. If only 1 field is being sorted, then any value may be used for sortPriority. SortPriority should be an integer greater than 0."
            },
            "function": {
                "allOf": [
                    {
                        "$ref": "#/components/schemas/Function"
                    },
                    {
                        "description": "Provide a Function for a field to generate an aggregation against that fields' values. For example providing the SUM Function will cause an aggregated SUM to be calculated for that field."
                    }
                ]
            }
        }
    },
    "dataType": {
        "type": "object",
        "description": "Describes a field in the datasource that can be used to create queries.",
        "properties": {
            "columnName": {
                "type": "string"
            },
            "caption": {
                "type": "string"
            },
            "dataType": {
                "type": "string",
                "enum": [
                    "UNSPECIFIED",
                    "INTEGER",
                    "REAL",
                    "STRING",
                    "DATETIME",
                    "BOOLEAN",
                    "DATE",
                    "SPATIAL",
                    "UNKNOWN",
                    "UNRECOGNIZED"
                ]
            },
        }
    },
    "DateObject": {
        "type": "object",
        "required": [
            "day",
            "month",
            "year"
        ],
        "properties": {
            "day": {
                "type": "integer"
            },
            "month": {
                "type": "integer"
            },
            "year": {
                "type": "integer"
            }
        }
    },
    "Filter": {
        "type": "object",
        "required": [
            "filterType"
        ],
        "properties": {
            "columnName": {
                "type": "string"
            },
            "column": {
                "allOf": [
                    {
                        "$ref": "#/components/schemas/FilterColumn"
                    }
                ]
            },
            "filterType": {
                "type": "string",
                "enum": [
                    "QUANTITATIVE",
                    "SET",
                    "DATE",
                    "TOP"
                ]
            },
            "context": {
                "type": "boolean",
                "default": "false"
            }
        },
        "discriminator": {
            "propertyName": "filterType",
            "mapping": {
                "QUANTITATIVE": "#/components/schemas/QuantitativeFilter",
                "SET": "#/components/schemas/SetFilter",
                "DATE": "#/components/schemas/RelativeDateFilter",
                "TOP": "#/components/schemas/TopNFilter"
            }
        }
    },
    "FilterColumn": {
        "type": "object",
        "oneOf": [
            {
                "required": [
                    "columnName",
                    "function"
                ]
            },
            {
                "required": [
                    "calculation"
                ]
            }
        ],
        "properties": {
            "columnName": {
                "type": "string"
            },
            "function": {
                "allOf": [
                    {
                        "$ref": "#/components/schemas/Function"
                    }
                ]
            },
            "calculation": {
                "type": "string"
            }
        }
    },
    "Function": {
        "type": "string",
        "description": "The standard set of Tableau aggregations.",
        "enum": [
            "SUM",
            "AVG",
            "MEDIAN",
            "COUNT",
            "COUNT_DIST",
            "MIN",
            "MAX",
            "STD_DEV",
            "VARIANCE",
            "CLCT",
            "DATE_YEAR",
            "DATE_QTR",
            "DATE_MONTH",
            "DATE_WEEK",
            "DATE_DAY",
            "DATE_TRUNC_YEAR",
            "DATE_TRUNC_QTR",
            "DATE_TRUNC_MONTH",
            "DATE_TRUNC_WEEK",
            "DATE_TRUNC_DAY"
        ]
    },
    "MetadataOutput": {
        "type": "object",
        "properties": {
            "data": {
                "type": "array",
                "items": {
                    "$ref": "#/components/schemas/ColumnMetadata"
                }
            }
        }
    },
    "QuantitativeFilter": {
        "allOf": [
            {
                "$ref": "#/components/schemas/Filter"
            },
            {
                "type": "object",
                "required": [
                    "quantitativeFilterType"
                ],
                "properties": {
                    "quantitativeFilterType": {
                        "type": "string",
                        "enum": [
                            "RANGE",
                            "MIN",
                            "MAX",
                            "SPECIAL"
                        ]
                    },
                    "min": {
                        "type": "number",
                        "description": "A numerical value, either integer or floating point indicating the minimum value to filter upon. Required for RANGE and MIN"
                    },
                    "max": {
                        "type": "number",
                        "description": "A numerical value, either integer or floating point indicating the maximum value to filter upon. Required for RANGE and MAX"
                    },
                    "minDate": {
                        "$ref": "#/components/schemas/DateObject"
                    },
                    "maxDate": {
                        "$ref": "#/components/schemas/DateObject"
                    },
                    "quantitativeFilterIncludedValues": {
                        "allOf": [
                            {
                                "$ref": "#/components/schemas/QuantitativeFilterIncludedValues"
                            }
                        ]
                    }
                }
            }
        ]
    },
    "QuantitativeFilterIncludedValues": {
        "type": "string",
        "enum": [
            "ALL",
            "NON_NULL",
            "NULL",
            "IN_RANGE",
            "IN_RANGE_OR_NULL",
            "NONE"
        ]
    },
    "Query": {
        "description": "The Query is the fundamental interface to VDS. It holds the specific semantics to perform against the Data Source. A Query consists of an array of fields to query against, an optional array of filters to apply to the query, and an optional Metadata field to modify the query behavior.",
        "required": [
            "fields"
        ],
        "type": "object",
        "properties": {
            "fields": {
                "description": "An array of Columns that define the query",
                "type": "array",
                "items": {
                    "$ref": "#/components/schemas/Column"
                }
            },
            "filters": {
                "description": "An optional array of Filters to apply to the query",
                "type": "array",
                "items": {
                    "$ref": "#/components/schemas/Filter"
                }
            }
        }
    },
    "QueryOutput": {
        "type": "object",
        "properties": {
            "data": {
                "type": "array",
                "items": {}
            }
        }
    },
    "ReturnFormat": {
        "type": "string",
        "enum": [
            "OBJECTS",
            "ARRAYS"
        ]
    },
    "SetFilter": {
        "allOf": [
            {
                "$ref": "#/components/schemas/Filter"
            },
            {
                "type": "object",
                "required": [
                    "values",
                    "exclude"
                ],
                "properties": {
                    "values": {
                        "type": "array",
                        "items": {}
                    },
                    "exclude": {
                        "type": "boolean"
                    }
                }
            }
        ]
    },
    "SortDirection": {
        "type": "string",
        "description": "The direction of the sort, either ascending or descending. If not supplied the default is ascending",
        "enum": [
            "ASC",
            "DESC"
        ]
    },
    "RelativeDateFilter": {
        "allOf": [
            {
                "$ref": "#/components/schemas/Filter"
            },
            {
                "type": "object",
                "required": [
                    "units"
                ],
                "properties": {
                    "units": {
                        "type": "string",
                        "enum": [
                            "MINUTES",
                            "HOURS",
                            "DAYS",
                            "WEEKS",
                            "MONTHS",
                            "QUARTERS",
                            "YEARS"
                        ]
                    },
                    "pastCount": {
                        "type": "integer"
                    },
                    "futureCount": {
                        "type": "integer"
                    },
                    "anchor": {
                        "allOf": [
                            {
                                "$ref": "#/components/schemas/DateObject"
                            }
                        ]
                    },
                    "includeNulls": {
                        "type": "boolean"
                    }
                }
            }
        ]
    },
    "TopNFilter": {
        "allOf": [
            {
                "$ref": "#/components/schemas/Filter"
            },
            {
                "type": "object",
                "required": [
                    "direction, howMany, fieldToMeasure"
                ],
                "properties": {
                    "direction": {
                        "enum": [
                            "TOP",
                            "BOTTOM"
                        ],
                        "description": "Top (Ascending) or Bottom (Descending) N"
                    },
                    "howMany": {
                        "type": "integer",
                        "description": "The number of values from the Top or the Bottom of the given fieldToMeasure"
                    },
                    "fieldToMeasure": {
                        "allOf": [
                            {
                                "$ref": "#/components/schemas/FilterColumn"
                            }
                        ]
                    }
                }
            }
        ]
    }
}

prompt = {
    "instructions": instructions,
    "restrictions": restrictions,
    # "user_query": "",
    "data_model": {},
    "vds_schema": vds_schema,
    "few_shot_examples": few_shot,
}