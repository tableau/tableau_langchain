vds_schema = {
    "Column": {
        "type": "object",
        "anyOf": [
            {
                "required": [
                    "columnName"
                ]
            },
            {
                "required": [
                    "columnName",
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
            "columnName": {
                "type": "string",
                "description": "The name of the column which must be supplied."
            },
            "columnAlias": {
                "type": "string",
                "description": "An alternate name to give the column. Will only be used in Object format output."
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
                "description": "To enable sorting on a specific Column provide a sortPriority for that Column, and that Column will be sorted. The sortPriority provides a ranking of how to sort Columns when multiple Columns are being sorted. The highest priority (lowest number) Column is sorted first. If only 1 Column is being sorted, then any value may be used for sortPriority. SortPriority should be an integer greater than 0."
            },
            "function": {
                "allOf": [
                    {
                        "$ref": "#/components/schemas/Function"
                    },
                    {
                        "description": "Provide a Function for a Column to generate an aggregation against that Columns' values. For example providing the SUM Function will cause an aggregated SUM to be calculated for that Column."
                    }
                ]
            }
        }
    },
    "ColumnMetadata": {
        "type": "object",
        "description": "Describes a column in the datasource that can be used to create queries.",
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
            "columnContainsNulls": {
                "type": "boolean"
            },
            "objectGraphId": {
                "type": "string"
            }
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
        "description": "The Query is the fundamental interface to VDS. It holds the specific semantics to perform against the Data Source. A Query consists of an array of Columns to query against, an optional array of filters to apply to the query, and an optional Metadata field to modify the query behavior.",
        "required": [
            "columns"
        ],
        "type": "object",
        "properties": {
            "columns": {
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
