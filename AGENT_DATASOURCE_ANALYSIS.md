# Agent Datasource Analysis - April 14, 2026

## Executive Summary

**Problem:** Agents are failing sample questions because their prompts reference WRONG datasources or incomplete field information.

**Root Cause:** Agent prompts were written without comprehensive analysis of actual MCP server datasources and their field metadata.

**Solution:** Update each agent's prompt with correct datasource IDs and field mappings based on actual MCP metadata.

---

## Available Datasources in MCP Server

### Healthcare/HLS Datasources (Makana Agent)

1. **HLSPayerClaimDenials** ⭐ PRIMARY for claim denial questions
   - ID: `1127df56-f412-4b5c-b8d4-90583773c6b7`
   - Project: `Pulse_Demo_HLS | Payer Claim Denials_202509160043`
   - **Key Fields:**
     - **Dimensions:** Denial Reason, Denial?, Provider Name, Plan Type, Diagnostic, Reception Date
     - **Measures:** ID (use COUNTD for claim counts), Days of Backlog, Processing Time
   - **Perfect for:** "What are the top three reasons for claim denials, and how do they vary by provider?"

2. **PharmaSales** ⭐ PRIMARY for pharma sales questions
   - ID: `10dbb420-4b25-4ff9-984c-db52a66322fd`
   - Project: `Pulse_Demo_HLS | Pharma Sales_202509160044`
   - **Key Fields:**
     - **Dimensions:** Product, Market, Region, Territory, Rep Name, Quarter, Year, Month, PostalCode
     - **Measures:** TRx ($), NRx ($), Market Share (%), Sales Growth (%)
   - **Perfect for:** Product sales analysis, market share, rep performance

3. **InsuranceClaims** ⚠️ SECONDARY (Different domain - property/casualty claims)
   - ID: `264d2aeb-e754-4723-a529-1a7519fd8f0b`
   - Project: `Pulse_Demo_FINS | Insurance Claims_202509160036`
   - **Key Fields:**
     - **Dimensions:** Claim Reason, Is Reimbursed Flag, Claim Process Status, Policy Type, Agent Group, Agent
     - **Measures:** Claim Number (COUNTD), Claim Paid Amount (SUM), Days to Close (AVG)
   - **Use for:** Property/casualty insurance claims (flooding, fire, etc.) - NOT healthcare payer denials

### Wealth Management Datasources (Cumulus Agent)

1. **WealthandAssetManagement** ⭐ PRIMARY
   - ID: `f4f9467e-4daa-4256-9698-a703be25fafa`
   - Project: `Pulse_Demo_FINS | Wealth Management_202509160042`
   - **Key Fields:**
     - **Dimensions:** Client ID, Market Segment, Advisor ID, Advisor Name, Product Type, Risk Profile, Account Status, Client Tenure Bucket, Region, Branch
     - **Measures:** Net AUM, Gross AUM, Net Flows, Advisory Fees, NPS Score, Client Retention Rate, Portfolio Return (%), Number of Accounts, Average Account Size
   - **Perfect for:** AUM analysis, advisor performance, client retention, NPS scores

2. **RetailBanking-LoanPerformance** ⚠️ SECONDARY
   - ID: `a6d24d21-90a0-4fd3-892b-ce33b35d801e`
   - Project: `Pulse_Demo_FINS | Retail Banking_202509160039`
   - **Limited metadata** - not recommended for primary use

3. **BankIncomeStatement** ⚠️ SECONDARY
   - ID: `a4a03a82-f4d8-422c-b478-9c33fbe42b3d`
   - Project: `Pulse_Demo_FINS | Bank Income Statement_202509160039`
   - **Limited metadata** - not recommended for primary use

### Retail Datasources (Superstore Agent)

1. **Superstore Datasource** ⭐ PRIMARY
   - ID: `d8c8b547-19a9-4850-9b3e-83afdcc691c5`
   - Project: `Samples`
   - **Proven working** - use for Superstore questions

---

## Issue Breakdown by Agent

### Makana Agent ❌ WRONG DATASOURCE

**Current Prompt:** Lists `InsuranceClaims` and `PharmaSales`

**Sample Question:** "What are the top three reasons for claim denials, and how do they vary by provider?"

**Problem:**
- Uses `InsuranceClaims` datasource which has:
  - ❌ "Claim Reason" (property damage: Flooding, Fire, Hail) - NOT healthcare denial reasons
  - ❌ "Agent Group" (Back Office, Front Office) - NOT healthcare providers
  - ❌ "Is Reimbursed Flag" (Y/N) - NOT specific denial indicator

**Solution:** Should use `HLSPayerClaimDenials` datasource which has:
  - ✅ "Denial Reason" (ICD Codes missing, Prior authorization, Member not eligible)
  - ✅ "Provider Name" (Johns Hopkins Hospital, San Francisco Clinic, etc.)
  - ✅ "Denial?" flag specifically for denials

**Test Query Result:**
```
Query: Denial Reason + Provider Name + ID (COUNTD)
Result: 30 rows returned
Top denial reasons:
1. ICD Codes missing/unreadable/invalid | Johns Hopkins Hospital | 5,181 denials
2. ICD Codes missing/unreadable/invalid | San Francisco Clinic | 5,179 denials
3. Prior authorization not applicable | San Francisco Clinic | 4,325 denials
```

**Verdict:** ✅ QUERY WORKS PERFECTLY on HLSPayerClaimDenials!

### Cumulus Agent ⚠️ POTENTIALLY WRONG FIELDS

**Current Prompt:** Lists `WealthandAssetManagement` as primary

**Sample Question:** "Which advisors have the highest client retention rates?"

**Problem:**
- Test result shows failure: "Contains excuse phrase: 'not available', Too slow: 24.24s"
- Likely using wrong field names or aggregation

**Needs Investigation:**
- Verify actual field name for "Client Retention Rate"
- Check if it's a pre-aggregated measure (no function) or needs AVG
- Verify "Advisor Name" vs "Advisor ID" field name

### Superstore Agent ✅ WORKING

**Status:** Sample questions passing
**No changes needed**

---

## Recommended Field Mappings

### Makana Agent - HLSPayerClaimDenials

| User Question Term | Actual Field Name | Aggregation | Notes |
|-------------------|------------------|-------------|-------|
| "denials" | ID | COUNTD | Count distinct claim IDs |
| "denial reasons" | Denial Reason | (dimension) | ICD Codes missing, Prior auth, etc. |
| "provider" | Provider Name | (dimension) | Hospital/clinic name |
| "plan type" | Plan Type | (dimension) | Insurance plan |
| "processing time" | Processing Time | AVG | Days to process |
| "denied claims" | Filter by Denial? = 'Y' | (filter) | Use Denial? flag |

**Sample Query:**
```json
{
  "datasourceLuid": "1127df56-f412-4b5c-b8d4-90583773c6b7",
  "query": {
    "fields": [
      {"fieldCaption": "Denial Reason"},
      {"fieldCaption": "Provider Name"},
      {"fieldCaption": "ID", "function": "COUNTD"}
    ]
  }
}
```

### Makana Agent - PharmaSales

| User Question Term | Actual Field Name | Aggregation | Notes |
|-------------------|------------------|-------------|-------|
| "product sales" | TRx ($) | SUM | Total prescription sales |
| "market share" | Market Share (%) | AVG | Percentage |
| "region" | Region | (dimension) | Geographic region |
| "rep performance" | Rep Name | (dimension) | Sales rep |
| "product" | Product | (dimension) | Product name |

**Sample Query:**
```json
{
  "datasourceLuid": "10dbb420-4b25-4ff9-984c-db52a66322fd",
  "query": {
    "fields": [
      {"fieldCaption": "Product"},
      {"fieldCaption": "TRx ($)", "function": "SUM"}
    ]
  }
}
```

### Makana Agent - InsuranceClaims (DEPRECATED FOR HEALTHCARE)

**⚠️ WARNING:** This is property/casualty insurance, NOT healthcare payer claims!

Only use for questions about property damage claims (flooding, fire, hail).

| Field | Type | Notes |
|-------|------|-------|
| Claim Reason | Dimension | Flooding, Fire, Hail, Lightning, etc. |
| Is Reimbursed Flag | Dimension | 'Y' = paid, 'N' = denied |
| Agent Group | Dimension | Back Office, Front Office (NOT providers) |
| Claim Number | Measure | Use COUNTD |
| Days to Close | Measure | Use AVG |

---

## Action Items

### 1. Update Makana Prompt ⚠️ CRITICAL

**Change:**
```diff
- 2. InsuranceClaims (ID: 264d2aeb-e754-4723-a529-1a7519fd8f0b)
-    Available Fields:
-    - Dimensions: Claim Reason, Is Reimbursed Flag, Claim Process Status, Claim Status, Policy Type, Agent, Agent Group, City, Event Date, Close Date, Open Date
-    - Measures to COUNT: Claim Number (use COUNTD), Claim Paid Amount (use SUM), Damages Amount (use SUM), Deductible (use SUM)
+ 2. HLSPayerClaimDenials (ID: 1127df56-f412-4b5c-b8d4-90583773c6b7)
+    Available Fields:
+    - Dimensions: Denial Reason, Denial?, Provider Name, Plan Type, Diagnostic, Reception Date
+    - Measures: ID (use COUNTD for claim counts), Days of Backlog, Processing Time (use AVG)
+    Example Queries:
+      * Top denial reasons by provider: Denial Reason + Provider Name + ID [COUNTD]
+      * Denials by plan type: Plan Type + ID [COUNTD] WHERE Denial? = 'Y'
```

**Update terminology mapping:**
```diff
TERMINOLOGY MAPPING (CRITICAL FOR CLAIM DENIALS):
When user asks about:           Use these fields and approach:
- - "denials" or "denied claims"  → Query: Is Reimbursed Flag + Claim Number [COUNTD], filter/show where Is Reimbursed Flag = 'N'
- - "denial reasons"              → Include: Claim Reason (dimension) + Is Reimbursed Flag
- - "provider"                    → Use: Agent Group or Agent (dimension)
+ - "denials" or "denied claims"  → Query HLSPayerClaimDenials: ID [COUNTD] + Denial? filter
+ - "denial reasons"              → Include: Denial Reason (dimension) from HLSPayerClaimDenials
+ - "provider"                    → Use: Provider Name (dimension) from HLSPayerClaimDenials
- "processing time"             → Use: Days to Close [AVG] if available, or calculate from Close Date - Open Date
- - "plan type"                   → Use: Policy Type (dimension)
- - Count of claims               → Use: Claim Number [COUNTD]
+ "processing time"             → Use: Processing Time [AVG] from HLSPayerClaimDenials
+ - "plan type"                   → Use: Plan Type (dimension) from HLSPayerClaimDenials
+ - Count of claims               → Use: ID [COUNTD] from HLSPayerClaimDenials
```

### 2. Investigate Cumulus Field Names ⚠️ NEEDED

Run metadata check on WealthandAssetManagement:
- Verify "Client Retention Rate" exact field name
- Verify "Advisor Name" vs "Advisor ID"
- Check if retention rate is pre-aggregated or needs AVG

### 3. Update Test Questions (Optional)

Consider updating test questions to clearly distinguish:
- Healthcare payer denials (HLSPayerClaimDenials)
- Property/casualty claims (InsuranceClaims)

**Current Makana Questions:**
1. ⚠️ "What are the top three reasons for claim denials, and how do they vary by provider?" - Should use HLSPayerClaimDenials
2. ⚠️ "How does the average processing time for claims correlate with the type of plan and denial rates?" - Should use HLSPayerClaimDenials
3. ✅ "How do sales trends for specific products vary over time..." - Uses PharmaSales (correct)

---

## Verification Steps

### Makana Agent Verification

After updating prompt, test these queries:

**Query 1: Top denial reasons by provider**
```bash
python -c "
from experimental.utilities.mcp_tools_dynamic import MCPToolDiscovery
import os
mcp = MCPToolDiscovery(os.getenv('TABLEAU_MCP_URL'))
result = mcp.call_tool('query-datasource', {
    'datasourceLuid': '1127df56-f412-4b5c-b8d4-90583773c6b7',
    'query': {
        'fields': [
            {'fieldCaption': 'Denial Reason'},
            {'fieldCaption': 'Provider Name'},
            {'fieldCaption': 'ID', 'function': 'COUNTD'}
        ]
    }
})
print(f\"Rows: {len(result['data'])}\")
"
```
Expected: ✅ 30 rows returned

**Query 2: Processing time by plan type**
```bash
python -c "
from experimental.utilities.mcp_tools_dynamic import MCPToolDiscovery
import os
mcp = MCPToolDiscovery(os.getenv('TABLEAU_MCP_URL'))
result = mcp.call_tool('query-datasource', {
    'datasourceLuid': '1127df56-f412-4b5c-b8d4-90583773c6b7',
    'query': {
        'fields': [
            {'fieldCaption': 'Plan Type'},
            {'fieldCaption': 'Processing Time', 'function': 'AVG'}
        ]
    }
})
print(f\"Rows: {len(result['data'])}\")
"
```
Expected: ✅ Should return data

---

## Summary

**Critical Issue:** Makana agent prompt uses `InsuranceClaims` (property insurance) when it should use `HLSPayerClaimDenials` (healthcare payer denials) for claim denial questions.

**Fix:** Update Makana prompt to:
1. Replace InsuranceClaims with HLSPayerClaimDenials for denial questions
2. Update field mappings: "Denial Reason", "Provider Name", "ID" (COUNTD)
3. Keep PharmaSales for pharma sales questions
4. Optionally keep InsuranceClaims but document it's for property/casualty, not healthcare

**Next Steps:**
1. Update experimental/agents/makana/prompt.py
2. Investigate Cumulus field names
3. Run test suite to verify fixes
