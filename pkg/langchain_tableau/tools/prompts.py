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

sample_queries = [
    {
        "example": "a simple query",
        "query": {
            "fields": [
                {
                    "fieldCaption": "Category"
                },{
                    "fieldCaption": "Sales",
                    "function": "SUM"
                }
            ]
        }
    },
     # removing until we can support this with higher reliability
    # {
    #    "example": "a simple Tableau calculation",
    #    "query": {
    #         "fields": [
    #             {
    #                 "fieldCaption": "AOV",
    #                 "calculation": "SUM([Profit])/COUNTD([Order ID])"
    #             }
    #         ]
    #     }
    # },
    {
        "example": "applying a set filter",
        "query": {
            "fields": [
                {
                    "fieldCaption": "Ship Mode"
                },{
                    "fieldCaption": "Sales",
                    "function": "SUM"
                }
            ],
            "filters": [
                {
                    "field": {
                        "fieldCaption": "Ship Mode"
                    },
                    "filterType": "SET",
                    "values": [ "First Class", "Standard Class" ],
                    "exclude": "false"
                }
            ]
        }
    },
    {
        "example": "applying a quantitative filter",
        "query": {
            "fields": [
                {
                    "fieldCaption": "Ship Mode"
                },{
                    "fieldCaption": "Sales",
                    "function": "SUM"
                }
            ],
            "filters": [
                {
                    "field": {
                        "fieldCaption": "Sales",
                        "function": "SUM"
                    },
                    "filterType": "QUANTITATIVE_NUMERICAL",
                    "quantitativeFilterType": "RANGE",
                    "min": 266839,
                    "max": 1149562
                }
            ]
        }
    },
    {
        "example": "applying a quantitative date filter",
        "query": {
            "fields": [
                {
                    "fieldCaption": "Order Date",
                    "function": "YEAR"
                },
                {
                    "fieldCaption": "Order Date",
                    "function": "QUARTER"
                },
                {
                    "fieldCaption": "Sales",
                    "function": "SUM"
                }
            ],
            "filters": [
                {
                    "field":{
                        "fieldCaption": "Order Date"
                    },
                    "filterType": "QUANTITATIVE_DATE",
                    "quantitativeFilterType": "MIN",
                    "minDate": "2020-01-01"
                }
            ]
        }
    },
    {
        "example": "applying a date filter",
        "query": {
            "fields": [
                {
                    "fieldCaption": "Order Date",
                    "function": "YEAR",
                    "sortPriority": 1
                },
                {
                    "fieldCaption": "Order Date",
                    "function": "MONTH",
                    "sortPriority": 2
                },
                {
                    "fieldCaption": "Sales",
                    "function": "SUM"
                }
            ],
            "filters": [
                {
                    "filterType": "DATE",
                    "field": {
                        "fieldCaption": "Order Date"
                    },
                    "periodType": "MONTHS",
                    "dateRangeType": "CURRENT",
                    "anchorDate": "2021-01-01"
                }
            ]
        }
    },
    {
        "example": "applying a match filter",
        "query": {
            "fields": [
                {
                    "fieldCaption": "State/Province"
                },{
                    "fieldCaption": "Sales",
                    "function": "SUM"
                }
            ],
            "filters": [
                {
                    "field": {
                        "fieldCaption": "State/Province"
                    },
                    "filterType": "MATCH",
                    "startsWith": "A",
                    "endsWith": "a",
                    "contains": "o",
                    "exclude": "false"
                }
            ]
        }
    },
    {
        "example": "applying a top N filter",
        "query": {
            "fields": [
                {
                    "fieldCaption": "State/Province"
                },{
                    "fieldCaption": "Profit",
                    "function": "SUM"
                }
            ],
            "filters": [
                {
                    "field": {
                        "fieldCaption": "State/Province"
                    },
                    "filterType": "TOP",
                    "howMany": 10,
                    "fieldToMeasure": {
                        "fieldCaption": "Profit",
                        "function": "SUM"
                    },
                    "direction": "TOP"
                }
            ]
        }
    },
    {
        "example": "applying a multi-set filter",
        "query": {
            "fields": [
                {
                    "fieldCaption": "Ship Mode"
                },
                {
                    "fieldCaption": "Segment"
                }, {
                    "fieldCaption": "Sales",
                    "function": "SUM"
                }
            ],
            "filters": [
                {
                    "field": {
                        "fieldCaption": "Ship Mode"
                    },
                    "filterType": "SET",
                    "values": [ "First Class", "Standard Class" ],
                    "exclude": "false"
                }, {
                    "field": {
                        "fieldCaption": "Segment"
                    },
                    "filterType": "SET",
                    "values": [ "Consumer" ],
                    "exclude": "true"
                }
            ]
        }
    },
    {
        "example": "applying multiple quantitative filters",
        "query": {
            "fields": [
                {
                    "fieldCaption": "Ship Mode"
                },{
                    "fieldCaption": "Sales",
                    "function": "SUM"
                },{
                    "fieldCaption": "Profit",
                    "function": "SUM"
                }
            ],
            "filters": [
                {
                    "field": {
                        "fieldCaption": "Sales",
                        "function": "SUM"
                    },
                    "filterType": "QUANTITATIVE_NUMERICAL",
                    "quantitativeFilterType": "MIN",
                    "min": 266839
                },
                {
                    "field": {
                        "fieldCaption": "Profit",
                        "function": "SUM"
                    },
                    "filterType": "QUANTITATIVE_NUMERICAL",
                    "quantitativeFilterType": "MAX",
                    "max": 164098
                }
            ]
        }
    },
    {
        "example": "applying set and quantitative filters",
        "query": {
            "fields": [
                {
                    "fieldCaption": "Ship Mode"
                },{
                    "fieldCaption": "Sales",
                    "function": "SUM"
                }
            ],
            "filters": [
                {
                    "field": {
                        "fieldCaption": "Ship Mode"
                    },
                    "filterType": "SET",
                    "values": [ "First Class", "Standard Class" ],
                    "exclude": "true"
                }, {
                    "field": {
                        "fieldCaption": "Sales",
                        "function": "SUM"
                    },
                    "filterType": "QUANTITATIVE_NUMERICAL",
                    "quantitativeFilterType": "MIN",
                    "min": 400000
                }
            ]
        }
    },
    {
        "example": "applying a context filter",
        "query": {
            "fields": [
                {
                    "fieldCaption": "Sub-Category"
                },{
                    "fieldCaption": "Sales",
                    "function": "SUM"
                }
            ],
            "filters": [
                {
                    "field": {
                        "fieldCaption": "Sub-Category"
                    },
                    "filterType": "TOP",
                    "howMany": 10,
                    "fieldToMeasure": {
                        "fieldCaption": "Sales",
                        "function": "SUM"
                    },
                    "direction": "TOP"
                },
                {
                    "field": {
                        "fieldCaption": "Category"
                    },
                    "filterType": "SET",
                    "values": [ "Furniture"],
                    "exclude": "false",
                    "context": "true"
                }
            ]
        }
    },
    {
        "example": "applying date, set and quantitative filters",
        "query": {
            "fields": [
                {
                    "fieldCaption": "Order Date",
                    "function": "TRUNC_DAY",
                    "sortPriority": 1,
                    "sortDirection": "ASC"
                },
                {
                    "fieldCaption": "Sales",
                    "function": "SUM"
                },
                {
                    "fieldCaption": "Ship Mode"
                }
            ],
            "filters": [
                {
                    "field": {
                        "fieldCaption": "Sales",
                        "function": "SUM"
                    },
                    "filterType": "QUANTITATIVE_NUMERICAL",
                    "quantitativeFilterType": "RANGE",
                    "min": 10,
                    "max": 63
                },
                {
                    "filterType": "DATE",
                    "field": {
                        "fieldCaption": "Order Date"
                    },
                    "periodType": "MONTHS",
                    "dateRangeType": "NEXTN",
                    "rangeN": 3,
                    "anchorDate": "2021-01-01"
                },
                {
                    "field": {
                        "fieldCaption": "Ship Mode"
                    },
                    "filterType": "SET",
                    "values": [ "First Class"],
                    "exclude": "false"
                }
            ]
        }
    },
    {
        "example": "Filtering data to a specific date using DATE filter, dates shown with TRUNC_DAY for day level accuracy, anchorDate is optional and if left empty defaults to today",
        "query": {
            "fields": [
                {
                    "fieldCaption": "Sales",
                    "function": "SUM"
                },
                {
                    "fieldCaption": "Order Date",
                    "function": "TRUNC_DAY",
                    "sortPriority": 1,
                    "sortDirection": "ASC"
                }
            ],
            "filters": [
                {
                    "filterType": "DATE",
                    "field": {
                        "fieldCaption": "Date"
                    },
                    "periodType": "DAYS",
                    "dateRangeType": "CURRENT",
                    "anchorDate": "2021-01-01"
                }
            ]
        }
    },
    {
        "example": "Relative DATE filter to handle questions about last 2 weeks where rangeN is used, anchorDate is optional and if left empty defaults to today",
        "query": {
            "fields": [
                {
                    "fieldCaption": "Sales",
                    "function": "SUM"
                },
                {
                    "fieldCaption": "Orders",
                    "function": "SUM"
                },
                {
                    "fieldCaption": "Order Date",
                    "function": "TRUNC_DAY",
                    "sortPriority": 1,
                    "sortDirection": "ASC"
                },
            ],
            "filters": [
                {
                    "filterType": "DATE",
                    "field": {
                        "fieldCaption": "Order Date"
                    },
                    "periodType": "WEEKS",
                    "dateRangeType": "LASTN",
                    "rangeN": 2,
                    "anchorDate": "2025-02-22"
                }
            ]
        }
    },
    {
        "example": "Relative DATE filter to handle questions about last week, rangeN is not used here, anchorDate is optional and if left empty defaults to today",
        "query": {
            "fields": [
                {
                    "fieldCaption": "Sales",
                    "function": "SUM"
                },
                {
                    "fieldCaption": "Orders",
                    "function": "SUM"
                },
                {
                    "fieldCaption": "Order Date",
                    "function": "TRUNC_DAY",
                    "sortPriority": 1,
                    "sortDirection": "ASC"
                },
            ],
            "filters": [
                {
                    "filterType": "DATE",
                    "field": {
                        "fieldCaption": "Order Date"
                    },
                    "periodType": "WEEKS",
                    "dateRangeType": "LAST"
                }
            ]
        }
    }
]

error_queries = [
    {
        "observation": "ERROR when querying data for a specific date, you need to use RANGE with minDate and maxDate on the same field",
        "error": "Cannot have multiple Filters for the same Field, or the same Field with the same function",
        "error_query": {
            "fields": [
                {
                "fieldCaption": "Orders",
                "function": "SUM"
                }
            ],
            "filters": [
                {
                "field": {
                    "fieldCaption": "Date"
                },
                "filterType": "QUANTITATIVE_DATE",
                "quantitativeFilterType": "MIN",
                "minDate": "2025-01-20"
                },
                {
                "field": {
                    "fieldCaption": "Date"
                },
                "filterType": "QUANTITATIVE_DATE",
                "quantitativeFilterType": "MAX",
                "maxDate": "2025-01-20"
                }
            ]
        },
        "correction": {
            "fields": [
                {
                "fieldCaption": "Orders",
                "function": "SUM"
                }
            ],
            "filters": [
                {
                "field": {
                    "fieldCaption": "Date"
                },
                "filterType": "QUANTITATIVE_DATE",
                "quantitativeFilterType": "RANGE",
                "minDate": "2025-01-20",
                "maxDate": "2025-01-20"
                }
            ]
        }
    },
    {
        "observation": "ERROR when applying `sortDirection` to the entire payload, these properties only apply to fields",
        "error": "Error at 'query': Additional property 'sortDirection' is not allowed",
        "error_query": {
            "fields": [
                {
                    "fieldCaption":"Order Date",
                    "function":"YEAR"
                },
                {
                    "fieldCaption":"Orders",
                    "function":"SUM"
                }
            ],
            "filters":[],
            "sortDirection":"ASC",
            "sortPriority":1
        },
        "correction": {
            "fields": [
                {
                    "fieldCaption":"Order Date",
                    "function":"YEAR",
                    "sortDirection":"ASC",
                    "sortPriority":1
                },
                {
                    "fieldCaption":"Orders",
                    "function":"SUM"
                }
            ],
            "filters":[]
        }
    },
    {
        "observation": "ERROR caused by non-existant property",
        "error": "Error at 'query.filters.0.filterType': Value 'RELATIVE_DATE' is not defined in the schema",
        "error_query": {
            "fields": [
                {
                "fieldCaption": "Order Date",
                "function": "TRUNC_DAY",
                "sortDirection": "ASC",
                "sortPriority": 1
                },
                {
                "fieldCaption": "Profit",
                "function": "SUM"
                },
            ],
            "filters": [
                {
                "field": {
                    "fieldCaption": "Order Date"
                },
                "filterType": "RELATIVE_DATE",
                "periodType": "WEEKS",
                "dateRangeType": "LASTN",
                "rangeN": 5
                }
            ]
        },
        "correction": {
            "fields": [
                {
                "fieldCaption": "Order Date",
                "function": "TRUNC_DAY",
                "sortDirection": "ASC",
                "sortPriority": 1
                },
                {
                "fieldCaption": "Profit",
                "function": "SUM"
                },
            ],
            "filters": [
                {
                "field": {
                    "fieldCaption": "Order Date"
                },
                "filterType": "DATE",
                "periodType": "WEEKS",
                "dateRangeType": "LAST",
                }
            ]
        }
    }
]

vds_prompt_data = {
    "task": {},
    "meta": {},
    "data_dictionary": {},
    "data_model": {},
    "vds_schema": vds_schema,
    "sample_queries": sample_queries,
    "error_queries": error_queries,
    "previous_call_error": {},
    "previous_vds_payload": {}
}

vds_query = """
Task:
Your job is to write the main body of a request to the Tableau VizQL Data Service (VDS) API to
obtain data that answers the task given to you by the user:

User Task: {task}

Data Dictionary:
Use this to map the user's natural language questions to the fields of data available in the data source and
to be aware of any additional operations that may be needed to conceptualize the data correctly according to business
semantics or other logic such as applying filters, aggregations, dates, etc.

{data_dictionary}

Data Model:
Provides sample values for fields in the data source. This is useful in particular when aggregating or inferring
filter values

{data_model}

VDS Schema:
OpenAPI schema describing JSON payloads to the VDS API, use this to generate queries with correct syntax

{vds_schema}

Query:
The query must be written according to the `vds_schema.Query` key. Which describes two properties: fields (required)
and filters (optional)

Fields:
To satisfy the required "fields" property of `vds_schema.Query`, add fields according to the `vds_schema.Field` key,
which references `vds_schema.FieldBase`. Use the `data_dictionary` and `data_model` keys to query all useful or related
fields, including those not directly related to the topics mentioned by the user. Even if additional transformations or
calculations are needed, the additional fields may be useful. DO NOT HALLUCINATE FIELD NAMES

Aggregations:
Aggregations are a property of `vds_schema.Field` called "functions" and are described in `vds_schema.Functions`.
For INTEGER or REAL fields, you must always aggregate it with one of these: SUM, AVG, MEDIAN, COUNT, COUNTD, MIN or MAX.
For DATETIME or DATE fields, you must always aggregate it with one of these: YEAR, QUARTER, MONTH, WEEK, DAY, TRUNC_YEAR,
TRUNC_QUARTER, TRUNC_MONTH, TRUNC_WEEK or TRUNC_DAY. If you get an error from VDS that the response size is too large,
try further aggregating or filtering the data to avoid row-level results that are too granular and not insightful.

Sorting:
Sort fields as often as possible to highlight data of interest in the query even if not explicitly stated by the user. That
means that if they asked about a field in particular, find a way to sort it that makes sense. Sorting is composed of two
properties applied to `vds_schema.Field`: "sortDirection" described by `vds_schema.SortDirection` and "SortPriority" which
is sets the sort order for fields in the query. "SortPriority" is only needed for fields you wish to sort. DO NOT apply
sorting to the entire query or payload, this applies only to fields

Filtering:
Add filters to narrow down the data set according to user specifications and to avoid unnecessary large volumes of data.
Filters are the second and optional property of `vds_schema.Query` and should be written according to `vds_schema.Filter`.
The `vds_schema.Filter` spec references `vds_schema.FilterField`. When asked about values for a specific date, use
QuantitativeDateFilter with RANGE and always include both minDate and maxDate properties. When asked about last week,
previous month, current year, this quarter, previous 10 years, last 2 quarters use `RelativeDateFilter`

There are many types of filters. To choose the right kind of filters you must first use the `data_model` key to map the
target field to the kind of filters it supports. Use the "dataType" for each field (ex. "dataType": "STRING") and the
following list of filter types to make this determination:

- MatchFilter (defined at `vds_schema.MatchFilter`):
- QuantitativeFilterBase (defined at `vds_schema.QuantitativeFilterBase`):
- QuantitativeNumericalFilter (defined at `vds_schema.QuantitativeNumericalFilter`):
- QuantitativeDateFilter (defined at `vds_schema.QuantitativeDateFilter`): Always include minDate and maxDate properties for
specific dates
- SetFilter (defined at `vds_schema.SetFilter`):
- RelativeDateFilter (defined at `vds_schema.RelativeDateFilter`): Ideal for relative dates such as last week, previous month,
current year, this quarter, previous 10 years, last 2 quarters
- TopNFilter (defined at `vds_schema.TopNFilter`): Use this filter when the user asked a Top 10 or Top N question so that
you filter the data response to analyze

You may not have all filter members for fields of type "STRING" in the Data Model, only sample values. Therefore, you must
generate educated guesses for actual filter values and use any previous empty array errors to retry with better values

Sample Queries:
Reference these examples as best practices to execute tasks. These examples show distinct ways to interact with the VDS API
in order to obtain data in different shapes.

{sample_queries}

Error Queries:
These examples demonstrate common errors you have generated in the past, avoid these scenarios by using correct syntax instead

{error_queries}

Previous Tool Call Errors:
If this section has data, then the previous attempt resulted in an error described here:

{previous_call_error}

If the array was empty without syntax errors this indicates that a filter was applied with an incorrect value

The query you generated that caused the error is this:

{previous_vds_payload}

Output:
Your output must be minimal, containing only the VDS query in JSON format without any extra formatting for readability.
If the data source does not contain fields of data that can answer the user_input, return a message so the agent knows to
use a different tool
"""

vds_response = """
This is the output of a data query tool used to fetch information via Tableau's VizQL API
Your task is to synthesize all of this information to provide a clear, concise answer to the end user.

Data Source Name: {data_source_name}
Description: {data_source_description}
Maintainer: {data_source_maintainer}

This is the query written to Tableau's VizQL API:
{vds_query}

This is the resulting data from the query:
{data_table}

This was the user_input (question or task):
{user_input}

Based on the provided context, formulate a comprehensive and informative response to the user's query.
Your response should:
1. Describe the data source name, description and maintainer if this is the first interaction the user has with it
2. Use the resulting data to answer the user's question or task
3. Be short and concise, if the data table is too long only return the relevant rows or a small sample

Your synthesized response:
"""
