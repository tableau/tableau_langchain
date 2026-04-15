# Agent Prompt Fixes - April 14, 2026

## Makana Agent - CRITICAL FIX

**Issue:** Using wrong datasource for claim denial questions

**File:** `experimental/agents/makana/prompt.py`

**Replace InsuranceClaims with HLSPayerClaimDenials:**

```python
# OLD (line 16-26):
2. InsuranceClaims (ID: 264d2aeb-e754-4723-a529-1a7519fd8f0b)
   Available Fields:
   - Dimensions: Claim Reason, Is Reimbursed Flag, Claim Process Status, Claim Status, Policy Type, Agent, Agent Group, City, Event Date, Close Date, Open Date
   - Measures to COUNT: Claim Number (use COUNTD), Claim Paid Amount (use SUM), Damages Amount (use SUM), Deductible (use SUM)
   - Measures to AVERAGE: Days to Close (use AVG - calculated from Close Date - Open Date)
   - Pre-aggregated Measures (NO function): Nb Closed Claims, Nb Open Claims
   Example Queries:
     * Count denied claims by reason: Claim Reason + Is Reimbursed Flag + Claim Number [COUNTD]
     * Processing time by plan: Policy Type + Days to Close [AVG] (if Days to Close field exists)
     * Claims by provider: Agent Group + Claim Number [COUNTD]
   CRITICAL: "Denied/Rejected claims" = WHERE Is Reimbursed Flag = 'N'

# NEW:
2. HLSPayerClaimDenials (ID: 1127df56-f412-4b5c-b8d4-90583773c6b7)
   Available Fields:
   - Dimensions: Denial Reason, Denial?, Provider Name, Plan Type, Diagnostic, Reception Date
   - Measures: ID (use COUNTD for claim counts), Days of Backlog, Processing Time (use AVG)
   Example Queries:
     * Top denial reasons by provider: Denial Reason + Provider Name + ID [COUNTD]
     * Processing time by plan type: Plan Type + Processing Time [AVG]
     * Denials count: ID [COUNTD] where Denial? = 'Y'
   CRITICAL: Use "Denial Reason" not "Claim Reason", "Provider Name" not "Agent Group"
```

**Update terminology mapping (line 35-42):**

```python
# OLD:
TERMINOLOGY MAPPING (CRITICAL FOR INSURANCECLAIMS):
When user asks about:           Use these fields and approach:
- "denials" or "denied claims"  → Query: Is Reimbursed Flag + Claim Number [COUNTD], filter/show where Is Reimbursed Flag = 'N'
- "denial reasons"              → Include: Claim Reason (dimension) + Is Reimbursed Flag
- "provider"                    → Use: Agent Group or Agent (dimension)
- "processing time"             → Use: Days to Close [AVG] if available, or calculate from Close Date - Open Date
- "plan type"                   → Use: Policy Type (dimension)
- Count of claims               → Use: Claim Number [COUNTD]

# NEW:
TERMINOLOGY MAPPING (CRITICAL FOR HLSPAYERCLAIMDENIALS):
When user asks about:           Use these fields and approach:
- "denials" or "denied claims"  → Query HLSPayerClaimDenials: ID [COUNTD], optionally filter Denial? = 'Y'
- "denial reasons"              → Include: Denial Reason (dimension) from HLSPayerClaimDenials
- "provider" or "hospital"      → Use: Provider Name (dimension) from HLSPayerClaimDenials
- "processing time"             → Use: Processing Time [AVG] from HLSPayerClaimDenials
- "plan type"                   → Use: Plan Type (dimension) from HLSPayerClaimDenials
- Count of claims               → Use: ID [COUNTD] from HLSPayerClaimDenials
```

**Update example queries (line 66-77, 95-99):**

```python
# OLD:
InsuranceClaims query for denials by reason and provider:
{
  "datasourceLuid": "264d2aeb-e754-4723-a529-1a7519fd8f0b",
  "query": {
    "fields": [
      {"fieldCaption": "Claim Reason"},
      {"fieldCaption": "Is Reimbursed Flag"},
      {"fieldCaption": "Agent Group"},
      {"fieldCaption": "Claim Number", "function": "COUNTD"}
    ]
  }
}

# NEW:
HLSPayerClaimDenials query for denials by reason and provider:
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

**Update datasource selection (line 28-31, 46-48, 97-99, 103-104):**

Replace all mentions of InsuranceClaims with HLSPayerClaimDenials for claim denial questions.

---

## Cumulus Agent - CRITICAL FIX

**Issue:** Wrong field names in prompt - fields don't exist in datasource

**File:** `experimental/agents/cumulus/prompt.py`

**Actual available fields:**
- ✅ Market Segment (dimension)
- ✅ Advisor (dimension) - NOT "Advisor Name" or "Advisor ID"
- ✅ AUM, Net AUM (measures)
- ✅ NPS Score (measure)
- ✅ Client Counter (measure)
- ✅ Attrit (measure) - can calculate retention as 1 - (Attrit / Client Counter)
- ❌ Client Retention Rate - DOES NOT EXIST
- ❌ Advisory Fees - DOES NOT EXIST
- ❌ Advisor Name - DOES NOT EXIST (use "Advisor" instead)

**Update field list (line 10-16):**

```python
# OLD:
1. WealthandAssetManagement (ID: f4f9467e-4daa-4256-9698-a703be25fafa) ⭐ PRIMARY
   Available Fields:
   - Dimensions: Client ID, Market Segment, Advisor ID, Advisor Name, Product Type, Risk Profile,
                 Account Status, Client Since Year, Client Tenure Bucket, Region, Branch
   - Measures: Net AUM, Gross AUM, Net Flows, Advisory Fees, NPS Score, Client Retention Rate,
               Portfolio Return (%), Number of Accounts, Average Account Size
   Example Queries: AUM by segment, advisor performance, NPS analysis, retention rates

# NEW:
1. WealthandAssetManagement (ID: f4f9467e-4daa-4256-9698-a703be25fafa) ⭐ PRIMARY
   Available Fields:
   - Dimensions: Client ID, Client, Market Segment, Advisor, Client Type, Engagement,
                 NPS Type, Attrit?, Retention Offer
   - Measures: AUM, Net AUM, AUM (Total), NPS Score, Client Counter, Attrit, Attrition (Total),
               Annual Income, Appreciation Amount, Appreciation Rate, Advisor Tenure in Industry
   Example Queries: 
     * AUM by segment: Market Segment + AUM [SUM]
     * Top advisors by AUM: Advisor + AUM [SUM]
     * NPS by segment: Market Segment + NPS Score [AVG]
     * Advisor retention: Advisor + Attrit [SUM] + Client Counter [SUM] (calculate retention rate)
```

**Update example queries (line 53-56):**

```python
# OLD:
Example queries:
- AUM by segment: query_datasource with Market Segment + Net AUM (SUM)
- NPS by segment: query_datasource with Market Segment + NPS Score (AVG)
- Advisor performance: query_datasource with Advisor Name + Net AUM (SUM) + Advisory Fees (SUM)

# NEW:
Example queries:
- AUM by segment: query_datasource with Market Segment + AUM (SUM)
- NPS by segment: query_datasource with Market Segment + NPS Score (AVG)
- Advisor performance: query_datasource with Advisor + AUM (SUM) + Client Counter (SUM)
- Advisor retention: query_datasource with Advisor + Attrit (SUM) + Client Counter (SUM), then calculate: (Client Counter - Attrit) / Client Counter
```

**Fix sample question #2:**

The question "Which advisors have the highest client retention rates?" needs special handling because there's no direct retention rate field.

Agent should:
1. Query: Advisor + Attrit [SUM] + Client Counter [SUM]
2. Calculate: Retention Rate = (Client Counter - Attrit) / Client Counter
3. Sort by retention rate descending

---

## Verification Commands

### Test Makana with HLSPayerClaimDenials:
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
print(f'✅ Rows: {len(result[\"data\"])}')
"
```

### Test Cumulus with correct fields:
```bash
python -c "
from experimental.utilities.mcp_tools_dynamic import MCPToolDiscovery
import os
mcp = MCPToolDiscovery(os.getenv('TABLEAU_MCP_URL'))
result = mcp.call_tool('query-datasource', {
    'datasourceLuid': 'f4f9467e-4daa-4256-9698-a703be25fafa',
    'query': {
        'fields': [
            {'fieldCaption': 'Advisor'},
            {'fieldCaption': 'Attrit', 'function': 'SUM'},
            {'fieldCaption': 'Client Counter', 'function': 'SUM'}
        ]
    }
})
print(f'✅ Rows: {len(result[\"data\"])}')
"
```
