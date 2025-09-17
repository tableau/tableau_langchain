import os
import json

from langchain_tableau.utilities.vizql_data_service import (
    list_datasources,
    list_fields,
    query_vds,
)


MCP_URL = os.getenv(
    "TABLEAU_MCP_URL",
    "https://tableau-mcp-bierschenk-2df05b623f7a.herokuapp.com/tableau-mcp",
)


def select_best_datasource(question: str) -> str | None:
    ds_list = list_datasources(url=MCP_URL) or []
    query_terms = {t.strip(".,:;!?").lower() for t in question.split() if len(t) > 2}
    best = (None, -1)
    for item in ds_list if isinstance(ds_list, list) else []:
        if not isinstance(item, dict):
            continue
        luid = item.get("id")
        if not isinstance(luid, str):
            continue
        fields = list_fields(url=MCP_URL, datasource_luid=luid)
        if isinstance(fields, dict) and "data" in fields:
            fields_list = fields["data"]
        else:
            fields_list = fields if isinstance(fields, list) else []
        names = set()
        for f in fields_list:
            if isinstance(f, dict):
                n = f.get("fieldCaption") or f.get("name")
            elif isinstance(f, str):
                n = f
            else:
                n = None
            if isinstance(n, str):
                for token in n.replace("/", " ").split():
                    if len(token) > 2:
                        names.add(token.lower())
        score = len(query_terms & names)
        if score > best[1]:
            best = (luid, score)
    return best[0]


def build_query(question: str, fields_meta: list[dict]) -> dict:
    # naive field picking
    name_map = [
        ("Sales", ["sales", "revenue", "amount", "value"]),
        ("Region", ["region", "area", "zone"]),
        ("Category", ["category", "type", "segment"]),
        ("Order Date", ["date", "month", "year"]),
    ]

    def find_field(candidates: list[str]) -> str | None:
        for cand in candidates:
            for f in fields_meta:
                if isinstance(f, dict):
                    n = f.get("fieldCaption") or f.get("name")
                elif isinstance(f, str):
                    n = f
                else:
                    n = None
                if isinstance(n, str) and cand.lower() in n.lower():
                    return n
        return None

    measure = find_field(["sales", "revenue", "amount", "value"]) or "Sales"
    dim = find_field(["region", "area", "zone"]) or find_field(["category", "type"]) or "Category"

    fields = []
    # Add a time bucket if pertinent terms exist
    if any(t in question.lower() for t in ["month", "year", "weekly", "date", "trend"]):
        fields.append({"fieldCaption": "Order Date", "function": "TRUNC_MONTH", "sortDirection": "ASC", "sortPriority": 1})
    fields.append({"fieldCaption": dim})
    fields.append({"fieldCaption": measure, "function": "SUM", "fieldAlias": f"Total {measure}"})

    query = {"fields": fields}
    return query


def run_case(question: str) -> dict:
    ds = select_best_datasource(question)
    if not ds:
        return {"question": question, "status": "no_datasource"}
    # fetch fields for query build
    fields = list_fields(url=MCP_URL, datasource_luid=ds)
    if isinstance(fields, dict) and "data" in fields:
        fields_list = fields["data"]
    else:
        fields_list = fields if isinstance(fields, list) else []
    q = build_query(question, fields_list)
    res = query_vds(api_key="", datasource_luid=ds, url=MCP_URL, query=q)
    ok = isinstance(res, dict) and bool(res.get("data"))
    return {
        "question": question,
        "datasource": ds,
        "query": q,
        "ok": ok,
        "rows": len(res.get("data", [])) if isinstance(res, dict) else 0,
    }


def main():
    questions = [
        "Retail: total sales by region",
        "Healthcare: claim amount by payer",
        "Finance: loan amount by region",
        "Pharma: sales by drug category",
        "Insurance: claim denials by reason",
        "Manufacturing: revenue by product category",
        "Energy: monthly sales trend",
        "Telecom: revenue by customer segment",
        "Public sector: spend by category",
        "Education: revenue by region",
    ]
    results = [run_case(q) for q in questions]
    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()


