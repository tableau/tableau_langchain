examples = {
    "superstore": {
        "columns": {},
        "filters": {},
        "calculations": {},
        "example1": {
        "query": "Show me sales by segment",
        "JSON": {
            "columns": [
                {"columnName": "Segment"},
                {"columnName": "Sales", "function": "SUM", "maxDecimalPlaces": 2}
            ]
        }
        },
        "example2": {
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
        },
        "example3": {
            "query": "",
            "JSON": ""
        }
    }
}
