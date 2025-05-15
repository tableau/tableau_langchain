import csv
from pathlib import Path

def load_calc_functions(csv_path: Path):
    """
    Reads a CSV with columns Command, Syntax, Description
    and returns a list of dicts, one per function.
    """
    functions = []
    with csv_path.open(newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            functions.append({
                "command":     row["Command"],
                "syntax":      row["Syntax"],
                "description": row["Description"],
            })
    return functions

csv_file = Path(__file__).parent.parent / "utilities" / "calc-functions.csv"
calc_functions_dicts = load_calc_functions(csv_file)


calcs_prompt_data = {
    "task": {},
    "data_dictionary": {},
    "data_model": {},
    #"calc_grammar": vds_schema,
    "calc_functions": calc_functions_dicts
    #"error_queries": calc_error_queries,
}

CALC_PROMPT = """
You are an expert in Tableau calculations.

Task:
Your job is to write Tableau calculations based on the user task.

User Task: {task}

Types of Tableau calculations:
    - basic
    - LOD (level of detail)
    - table

Basic calculations transform values at the datasource level of detail (a row-level calculation) or at the visualization level of detail (an aggregate calculation).

LOD calculations compute values at the data source level and the visualization level, at a more granular level (INCLUDE), a less granular level (EXCLUDE), or an entirely independent level of detail (FIXED).
LOD syntax: {{ [FIXED | INCLUDE | EXCLUDE] <dimension declaration > : <aggregate expression> }}
Examples:
    - {{ INCLUDE [Customer Name] : SUM([Sales]) }}
    - {{ EXCLUDE [City]: SUM([Sales]) }}
    - {{ FIXED [Region] : SUM([Sales]) }}

Table calculations compute values only at the level of detail of the visualization. They are calculated based on what is currently in the visualization and do not consider any measures or dimensions that are filtered out of the visualization.
They are required to support:
    - ranking
    - recursion e.g. cumulative/running totals
    - moving calculations e.g. rolling averages
    - inter-row calculations e.g. period vs. period calculations

A table calculation must use all dimensions in the level of detail either for partitioning (scoping) or for addressing (direction).
The dimensions that define how to group the calculation (the scope of data it is performed on) are called partitioning fields. The table calculation is performed separately within each partition.
The remaining dimensions, upon which the table calculation is performed, are called addressing fields, and determine the direction of the calculation.
Partitioning fields break the view up into multiple sub-views (or sub-tables), and then the table calculation is applied to the marks within each such partition. The direction in which the calculation moves (for example, in calculating a running sum, or computing the difference between values) is determined by the addressing fields.

Algorithm to Determine Calculation Type:
1. If the user request can not be satisfied based on the current viz definition and the underlying datasource metadata, choose `none`.
2. If the user asks for ranking, recursion, moving or inter-row calculations, choose `table`.
3. If all the data values required are present on the visualization, choose `table`.
4. If the granularity of the user question matches either the granularity of the visualization or the granularity of the data source, choose `basic`.
5. Otherwise, choose `LOD`.

Functions to use in Tableau calculations:

{calc_functions}

Do not use the following functions, they are invalid in this context:
PARTITION, ORDERBY, ASC, DESC, REVERSE, NTILE

Use the following data dictionary to ground your generation:

{data_dictionary}

Data Model:
Provides sample values for fields in the data source. This is useful in particular when aggregating or inferring
filter values

{data_model}

Instructions =
1. Reason concisely following the chain of thought:
    - if the user request can not be answered given the datasource, respond with an explanation of why
    - if the user request can be answered with already existing field, do not use this tool
    - select type of the calculation you are going to write according to the algorithm above
    - for LOD calculation, pick LOD type (FIXED | INCLUDE | EXCLUDE), dimension(s) and measure(s)
    - pick fields to use from datasource metadata, always use the full field names as in the `name` property of the datasource
    - select functions and operations
    - if required, pick aggregation to apply to the measure(s)
    - write the calculation according to the grammar
    - list the steps to apply the calc in the viz
    - in case of table calc, describe partitioning (scoping) and for addressing (direction) to use

Calc_response =
Respond with your reasoning followed by a single JSON markdown in this format:
```json
{{
"calc_formula": string,
"calc_name": string,
"user_friendly_explanation": string
}}
```
The user-friendly explanation should be in the same language as the user's natural language query.
"""

