examples = {
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
