vds_schema = {
    "FieldBase": {
        "type": "object",
        "description": "Common properties of a Field. A Field represents a column of data in a published datasource",
        "required": [ "fieldCaption" ],
        "properties": {
            "fieldCaption": {
                "type": "string",
                "description": "Either the name of a specific Field in the data source, or, in the case of a calculation, a user-supplied name for the calculation."
            },
            "fieldAlias": {
                "type": "string",
                "description": "An alternative name to give the field. Will only be used in Object format output."
            },
            "maxDecimalPlaces": {
                "type": "integer",
                "description": "The maximum number of decimal places. Any trailing 0s will be dropped. The maxDecimalPlaces value must be greater or equal to 0."
            },
            "sortDirection": {
                "$ref": "#/components/schemas/SortDirection"
            },
            "sortPriority": {
                "type": "integer",
                "description": "To enable sorting on a specific Field provide a sortPriority for that field, and that field will be sorted. The sortPriority provides a ranking of how to sort Fields when multiple Fields are being sorted. The highest priority (lowest number) Field is sorted first. If only 1 Field is being sorted, then any value may be used for sortPriority. SortPriority should be an integer greater than 0."
            }
        }
    },
    "Field": {
        "oneOf": [
            {
                "allOf": [
                    {
                        "$ref": "#/components/schemas/FieldBase"
                    }
                ],
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "fieldCaption": {},
                    "fieldAlias": {},
                    "maxDecimalPlaces": {},
                    "sortDirection": {},
                    "sortPriority": {}
                }
            },
            {
                "allOf": [
                    {
                        "$ref": "#/components/schemas/FieldBase"
                    }
                ],
                "type": "object",
                "required": [
                    "function"
                ],
                "additionalProperties": False,
                "properties": {
                    "function": {
                        "$ref": "#/components/schemas/Function"
                    },
                    "fieldCaption": {},
                    "fieldAlias": {},
                    "maxDecimalPlaces": {},
                    "sortDirection": {},
                    "sortPriority": {}
                }
            },
            {
                "allOf": [
                    {
                        "$ref": "#/components/schemas/FieldBase"
                    }
                ],
                "type": "object",
                "required": [
                    "calculation"
                ],
                "additionalProperties": False,
                "properties": {
                    "calculation": {
                        "type": "string",
                        "description": "A Tableau calculation which will be returned as a Field in the Query"
                    },
                    "fieldCaption": {},
                    "fieldAlias": {},
                    "maxDecimalPlaces": {},
                    "sortDirection": {},
                    "sortPriority": {}
                }
            }
        ]
    },
    "FieldMetadata": {
        "type": "object",
        "description": "Describes a field in the datasource that can be used to create queries.",
        "properties": {
            "fieldName": {
                "type": "string"
            },
            "fieldCaption": {
                "type": "string"
            },
            "dataType": {
                "type": "string",
                "enum": [
                    "INTEGER",
                    "REAL",
                    "STRING",
                    "DATETIME",
                    "BOOLEAN",
                    "DATE",
                    "SPATIAL",
                    "UNKNOWN"
                ]
            },
            "logicalTableId": {
                "type": "string"
            }
        }
    },
    "Filter": {
        "type": "object",
        "description": "A Filter to be used in the Query to filter on the datasource",
        "required": ["field", "filterType"],
        "properties": {
            "field": {
                "$ref": "#/components/schemas/FilterField"
            },
            "filterType": {
                "type": "string",
                "enum": [
                    "QUANTITATIVE_DATE",
                    "QUANTITATIVE_NUMERICAL",
                    "SET",
                    "MATCH",
                    "DATE",
                    "TOP"
                ]
            },
            "context": {
                "type": "boolean",
                "description": "Make the given filter a Context Filter, meaning that it's an independent filter. Any other filters that you set are defined as dependent filters because they process only the data that passes through the context filter",
                "default": False
            }
        },
        "discriminator": {
            "propertyName": "filterType",
            "mapping": {
                "QUANTITATIVE_DATE": "#/components/schemas/QuantitativeDateFilter",
                "QUANTITATIVE_NUMERICAL": "#/components/schemas/QuantitativeNumericalFilter",
                "SET": "#/components/schemas/SetFilter",
                "MATCH": "#/components/schemas/MatchFilter",
                "DATE": "#/components/schemas/RelativeDateFilter",
                "TOP": "#/components/schemas/TopNFilter"
            }
        }
    },
    "FilterField": {
        "oneOf": [
            {
                "required": ["fieldCaption"],
                "additionalProperties": False,
                "properties": {
                    "fieldCaption": {
                        "type": "string",
                        "description": "The caption of the field to filter on"
                    }
                }
            },
            {
                "required": ["fieldCaption", "function"],
                "additionalProperties": False,
                "properties": {
                    "fieldCaption": {
                        "type": "string",
                        "description": "The caption of the field to filter on"
                    },
                    "function": {
                        "$ref": "#/components/schemas/Function"
                    }
                }
            },
            {
                "required": ["calculation"],
                "additionalProperties": False,
                "properties": {
                    "calculation": {
                        "type": "string",
                        "description": "A Tableau calculation which will be used to Filter on"
                    }
                }
            }
        ]
    },
    "Function": {
        "type": "string",
        "description": "The standard set of Tableau aggregations which can be applied to a Field",
        "enum": [
            "SUM",
            "AVG",
            "MEDIAN",
            "COUNT",
            "COUNTD",
            "MIN",
            "MAX",
            "STDEV",
            "VAR",
            "COLLECT",
            "YEAR",
            "QUARTER",
            "MONTH",
            "WEEK",
            "DAY",
            "TRUNC_YEAR",
            "TRUNC_QUARTER",
            "TRUNC_MONTH",
            "TRUNC_WEEK",
            "TRUNC_DAY"
        ]
    },
    "MatchFilter": {
        "allOf": [
            {
                "$ref": "#/components/schemas/Filter"
            },
            {
                "type": "object",
                "description": "A Filter that can be used to match against String Fields",
                "properties": {
                    "contains": {
                        "type": "string",
                        "description": "Matches when a Field contains this value"
                    },
                    "startsWith": {
                        "type": "string",
                        "description": "Matches when a Field starts with this value"
                    },
                    "endsWith": {
                        "type": "string",
                        "description": "Matches when a Field ends with this value"
                    },
                    "exclude": {
                        "type": "boolean",
                        "description": "When true, the inverse of the matching logic will be used",
                        "default": False
                    }
                }
            }
        ]
    },
    "QuantitativeFilterBase": {
        "allOf": [
            {
                "$ref": "#/components/schemas/Filter"
            },
            {
                "type": "object",
                "required": ["quantitativeFilterType"],
                "properties": {
                    "quantitativeFilterType": {
                        "type": "string",
                        "enum": [ "RANGE", "MIN", "MAX", "ONLY_NULL", "ONLY_NON_NULL" ]
                    },
                    "includeNulls": {
                        "type": "boolean",
                        "description": "Only applies to RANGE, MIN, and MAX Filters. Should nulls be returned or not. If not provided the default is to not include null values"
                    }
                }
            }
        ]
    },
    "QuantitativeNumericalFilter": {
        "allOf": [
            {
                "$ref": "#/components/schemas/QuantitativeFilterBase"
            }
        ],
        "type": "object",
        "description": "A Filter that can be used to find the minimumn, maximumn or range of numerical values of a Field",
        "properties": {
            "min": {
                "type": "number",
                "description": "A numerical value, either integer or floating point indicating the minimum value to filter upon. Required if using quantitativeFilterType RANGE or if using quantitativeFilterType MIN"
            },
            "max": {
                "type": "number",
                "description": "A numerical value, either integer or floating point indicating the maximum value to filter upon. Required if using quantitativeFilterType RANGE or if using quantitativeFilterType MIN"
            }
        }
    },
    "QuantitativeDateFilter": {
        "allOf": [
            {
                "$ref": "#/components/schemas/QuantitativeFilterBase"
            }
        ],
        "type": "object",
        "description": "A Filter that can be used to find the minimum, maximum or range of date values of a Field",
        "properties": {
            "minDate": {
                "type": "string",
                "format": "date",
                "description": "An RFC 3339 date indicating the earliest date to filter upon. Required if using quantitativeFilterType RANGE or if using quantitativeFilterType MIN"
            },
            "maxDate": {
                "type": "string",
                "format": "date",
                "description": "An RFC 3339 date indicating the latest date to filter upon. Required if using quantitativeFilterType RANGE or if using quantitativeFilterType MIN"
            }
        }
    },
    "Query": {
        "description": "The Query is the fundamental interface to Headless BI. It holds the specific semantics to perform against the Data Source. A Query consists of an array of Fields to query against, and an optional array of filters to apply to the query",
        "required": [
            "fields"
        ],
        "type": "object",
        "properties": {
            "fields": {
                "description": "An array of Fields that define the query",
                "type": "array",
                "items": {
                    "$ref": "#/components/schemas/Field"
                }
            },
            "filters": {
                "description": "An optional array of Filters to apply to the query",
                "type": "array",
                "items": {
                    "$ref": "#/components/schemas/Filter"
                }
            }
        },
        "additionalProperties": False
    },
    "SetFilter": {
        "allOf": [
            {
                "$ref": "#/components/schemas/Filter"
            }
        ],
        "type": "object",
        "description": "A Filter that can be used to filter on a specific set of values of a Field",
        "required": [
            "values"
        ],
        "properties": {
            "values": {
                "type": "array",
                "items": {},
                "description": "An array of values to filter on"
            },
            "exclude": {
                "type": "boolean",
                "default": False
            }
        }
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
                "description": "A Filter that can be used to filter on dates using a specific anchor and fields that specify a relative date range to that anchor",
                "required": ["periodType", "dateRangeType"],
                "properties": {
                    "periodType": {
                        "type": "string",
                        "description": "The units of time in the relative date range",
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
                    "dateRangeType": {
                        "type": "string",
                        "description": "The direction in the relative date range",
                        "enum": [
                            "CURRENT",
                            "LAST",
                            "LASTN",
                            "NEXT",
                            "NEXTN",
                            "TODATE"
                        ]
                    },
                    "rangeN": {
                        "type": "integer",
                        "description": "When dateRangeType is LASTN or NEXTN, this is the N value (how many years, months, etc.)."
                    },
                    "anchorDate": {
                        "type": "string",
                        "format": "date",
                        "description": "When this field is not provided, defaults to today."
                    },
                    "includeNulls": {
                        "type": "boolean",
                        "description": "Should nulls be returned or not. If not provided the default is to not include null values"
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
                "description": "A Filter that can be used to find the top or bottom number of Fields relative to the values in the fieldToMeasure",
                "required": ["howMany, fieldToMeasure"],
                "properties": {
                    "direction": {
                        "type": "string",
                        "enum": [
                                "TOP",
                                "BOTTOM"
                            ],
                        "default": "TOP",
                        "description": "Top (Ascending) or Bottom (Descending) N"
                    },
                    "howMany": {
                        "type": "integer",
                        "description": "The number of values from the Top or the Bottom of the given fieldToMeasure"
                    },
                    "fieldToMeasure": {
                        "$ref": "#/components/schemas/FilterField"
                    }
                }
            }
        ]
    }
}

vds_fewshot = [
    {
        "user_input": "Average discount, total sales, number of orders and profits by region sorted by profit",
        "best_practices": "",
        "JSON": {
            "fields": [
                {"fieldCaption": "Region"},
                {"fieldCaption": "Discount", "function": "AVG", "maxDecimalPlaces": 2},
                {"fieldCaption": "Sales", "function": "SUM", "maxDecimalPlaces": 2},
                {"fieldCaption": "Order ID", "function": "COUNT", "columnAlias": "Number of Orders"},
                {"fieldCaption": "Profit", "function": "SUM", "maxDecimalPlaces": 2, "sortPriority": 1, "sortDirection": "DESC"}
            ]
        }
    },
    {
        "user_input": "What are the top 5 sub-categories by sales with a minimum of $200,000 in the last 6 months, excluding Technology?",
        "best_practices": "",
        "JSON": {
            "fields": [
                { "fieldCaption": "Category" },
                { "fieldCaption": "Sub-Category" },
                { "fieldCaption": "Sales", "function": "SUM", "maxDecimalPlaces": 2, "sortPriority": 1, "sortDirection": "DESC" }
            ],
            "filters": [
                {
                    "field": {
                        "fieldCaption": "Category"
                    },
                    "filterType": "SET",
                    "values": ["Technology"],
                    "exclude": "true",
                    "context": "true"
                },
                {
                    "field": {
                        "fieldCaption": "Category"
                    },
                    "filterType": "TOP",
                    "direction": "TOP",
                    "howMany": 5,
                    "fieldToMeasure": {
                        "fieldCaption": "Sales",
                        "function": "SUM"
                    }
                },
                {
                    "field": { "fieldCaption": "Order Date" },
                    "filterType": "DATE",
                    "periodtype": "MONTHS",
                    "dateRangeType": "LASTN",
                    "rangeN": 6
                },
                {
                    "field": {
                        "fieldCaption": "Sales"
                    },
                    "filterType": "QUANTITATIVE_NUMERICAL",
                    "quantitativeFilterType": "MIN",
                    "min": 200000
                }
            ]
        }
    }
]

vds_instructions = f"""
Task: Your job is to write the main body of a request to Tableau’s VizQL Data Service (VDS) API
to obtain data to answer user questions

Actions:
- Query all useful or interesting fields, including those somewhat related to the topics mentioned
  by the user, even if additional transformations or calculations are needed
- Always perform aggregations (or functions) according to explicit or implied user needs to avoid returning too many rows of data
- Sort fields as often as possible to highlight data of interest in the query even if not explicitly stated by the user
- Add filters to narrow down the data set according to user specifications and to avoid unnecessary large volumes of data
- Write Tableau calculations to answer user questions with original analysis that does not exist in the target data source, use this
to create fields that do not exist that will be useful to answer the question

Restrictions:
- DO NOT HALLUCINATE FIELD NAMES OR FILTER VALUES
- Only use fields listed in the `data_model` key
- For categorical or STR filters use the values listed in the `data_model` key
- Do not write redundant calculations if the field already exists and can be aggregated via a function

The VDS query is a JSON object and to write it you must follow these steps:

1. Find the necessary `fieldCaptions` to write the query by checking the `data_model` key

2. Structure the overall payload or request body according to this spec:
    Query: \n {vds_schema.get('Query', 'No Query schema provided')}

3. Add fields to `Query` that help answer the user question
    This spec describes 3 different fields, one with row level data, one with functions (aggregating data) and one with calculations
    Field: \n{vds_schema.get('Field', 'No Field schema provided')}

    Each field has a base set of properties.
    FieldBase: \n{vds_schema.get('FieldBase', 'No FieldBase schema provided')}

4. Add functions or aggregations to fields to match the granularity needed by the user per this spec:
    Function: \n{vds_schema.get('Function', 'No Function schema provided')}

    Aggregations should be added to `Field`s as a best practice unless row-level data is requested
    Field: \n{vds_schema.get('Field', 'No Field schema provided')}

5. Add sorting instructions to fields:
    SortDirection: \n{vds_schema.get('SortDirection', 'No SortDirection schema provided')}

    This should be added to the proper `Field` not the `Query` as a separate object
    Field: \n{vds_schema.get('Field', 'No Field schema provided')}

6. Identify potential filtering fields by checking the `data_model` key

7. Select the right kind of filters to add to `vds_payload` to satisfy the needs of the user query
considering the problem the user wants to solve:
- MatchFilter: {vds_schema.get('MatchFilter', 'No MatchFilter schema provided')}
- QuantitativeFilterBase: {vds_schema.get('QuantitativeFilterBase', 'No QuantitativeFilterBase schema provided')}
- QuantitativeNumericalFilter: {vds_schema.get('QuantitativeNumericalFilter', 'No QuantitativeNumericalFilter schema provided')}
- QuantitativeDateFilter: {vds_schema.get('QuantitativeDateFilter', 'No QuantitativeDateFilter schema provided')}
- SetFilter: {vds_schema.get('SetFilter', 'No SetFilter schema provided')}
- RelativeDateFilter: {vds_schema.get('RelativeDateFilter', 'No RelativeDateFilter schema provided')}
- TopNFilter: {vds_schema.get('TopNFilter', 'No TopNFilter schema provided')}

8. Write filters according to this spec:
    FilterField: {vds_schema.get('FilterField', 'No FilterField schema provided')}

    Filters should be added to `Query` as a best practice to avoid unnecessarily large volumes of data
    Query: \n {vds_schema.get('Query', 'No Query schema provided')}

Output:
Your output must contain two sections, this is the template you must use:

Query Plan:
Where you describe your reasoning: why you queried these fields, why you aggregated the data and why filters were applied to it.
How does this satisfy the user query?

JSON_payload:
Where you include VDS payload you wrote to satisfy the user query according to the query plan and the instructions provided in the prompt
"""


vds_prompt = {
    "instructions": vds_instructions,
    "vds_schema": vds_schema,
    "data_model": {}
}
