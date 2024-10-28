few_shot = {
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
