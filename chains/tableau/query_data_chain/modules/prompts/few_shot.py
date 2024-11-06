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
