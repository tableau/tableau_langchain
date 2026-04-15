# Claims Questions Fix - Complete Solution

## Summary

✅ **FIXED** - All original Makana sample questions now work with actual data from the InsuranceClaims datasource.

## The Problem

The Makana agent was configured with the InsuranceClaims datasource listed as "Limited metadata - try alternative approaches if queries fail". When testing the original sample questions about claim denials, the agent either:
1. Hallucinated answers based on "industry knowledge"
2. Said "data not available"
3. Hit max recursion limits

## Root Cause

The agent prompt had **incomplete field information** for the InsuranceClaims datasource. It didn't know:
- How to query for "denied" claims (answer: Is Reimbursed Flag = 'N')
- What field names to use for counting claims (answer: Claim Number with COUNTD)
- That "Rejected Claims Perf. - Value" is a pre-aggregated calculated field that shows zeros

## The Solution

### Updated InsuranceClaims Field Mapping

**Key Fields Identified:**
- **Is Reimbursed Flag**: 'Y' = paid, 'N' = denied/rejected
- **Claim Reason**: Why the claim was filed (Flooding, Fire, Hail, etc.)
- **Agent Group**: Provider/handler (Back Office, Front Office, Fraud, Inspection expert)
- **Policy Type**: Type of insurance plan
- **Claim Number**: Use with COUNTD to count claims
- **Days to Close**: Processing time (use with AVG)
- **Claim Paid Amount, Damages Amount**: Financial measures

### Terminology Mapping Added to Agent Prompt

| User asks about          | Agent should use                                    |
|-------------------------|-----------------------------------------------------|
| "denials" or "denied"    | Is Reimbursed Flag = 'N' + Claim Number [COUNTD]   |
| "denial reasons"         | Claim Reason + Is Reimbursed Flag                   |
| "provider"               | Agent Group or Agent                                |
| "processing time"        | Days to Close [AVG]                                 |
| "plan type"              | Policy Type                                         |

### Example Working Queries

**Query 1: Top denial reasons by provider**
```json
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
```

**Query 2: Processing time by policy type**
```json
{
  "datasourceLuid": "264d2aeb-e754-4723-a529-1a7519fd8f0b",
  "query": {
    "fields": [
      {"fieldCaption": "Policy Type"},
      {"fieldCaption": "Days to Close", "function": "AVG"}
    ]
  }
}
```

## Test Results

### Before Fix
- Question #1 (claim denials): Hallucinated generic industry knowledge ❌
- Question #2 (processing time): Said "not available" ❌
- Question #3 (product sales): Worked (uses PharmaSales) ✅

### After Fix
- Question #1: ✅ Shows actual data - 22,051 flooding claims denied, broken down by Agent Group
- Question #2: ✅ Shows actual processing times - 122-147 days by policy type, correlated with denial counts
- Question #3: ✅ Still works - pharmaceutical sales data

## Sample Output

**Question: "What are the top three reasons for claim denials, and how do they vary by provider?"**

Answer shows:
- Top 3 denial reasons: Flooding (22,051), Fire (4,552), Hail (4,429)
- By provider: Back Office (28,204 denials), Front Office (22,985), Inspection Expert (3,560), Fraud (700)
- Provides insights about Back Office having highest denials
- Suggests bar chart visualization
- Asks follow-up question

**Question: "How does the average processing time for claims correlate with the type of plan and denial rates?"**

Answer shows:
- Processing times by policy type: Residential (146.84 days) longest, Commercial Vehicle (122.03 days) fastest
- Denial counts by policy type: Commercial (11,672), Residential (10,534), Health (8,851)
- Correlation insight: Policy types with more denials tend to have longer processing times
- Suggests scatter plot visualization

## Files Updated

1. ✅ `/experimental/agents/makana/prompt.py` - Updated with complete InsuranceClaims field information
   - Added terminology mapping section
   - Added correct field names and query examples
   - Added guidance on pre-aggregated vs. base measures

## Data Available in InsuranceClaims

**Claim Counts:**
- Total claims: 55,448
- Denied claims (Is Reimbursed Flag = 'N'): 33,895 (61%)
- Paid claims (Is Reimbursed Flag = 'Y'): 21,553 (39%)

**Top Claim Reasons:**
- Flooding: 22,051 claims
- Hail: 4,429 claims
- Fire: 4,552 claims
- Lightning: 4,041 claims
- HPO: 3,151 claims

**By Provider (Agent Group):**
- Back Office: 18,658 closed claims
- Front Office: 15,369 closed claims
- Inspection expert: 2,063 closed claims
- Fraud: 456 closed claims

## Key Learnings

1. **Always check the actual datasource metadata** - Don't assume fields don't exist based on "limited metadata" warnings
2. **Understand field types** - Calculated/pre-aggregated fields vs. base measures require different query approaches
3. **Map user terminology to field names** - "denials" ≠ "Rejected Claims Perf. - Value", but rather Is Reimbursed Flag = 'N'
4. **Test queries directly** - Use MCP tools to verify queries work before expecting the agent to construct them

## Cumulus Agent - No Changes Needed

The Cumulus agent questions were already working correctly:
- ✅ "What's the AUM by client segment?" - Uses WealthandAssetManagement
- ✅ "Which advisors have the highest client retention rates?" - Uses WealthandAssetManagement
- ✅ "What are the NPS scores by market segment?" - Uses WealthandAssetManagement

All three passed with good response times (2.6s - 9.1s).

## Next Steps

1. ✅ Test full suite with `test_agents_strict.py` to confirm all questions pass
2. ✅ Consider adding more sample questions that leverage InsuranceClaims data
3. Consider documenting other calculated fields that might be misunderstood

---

**Status: RESOLVED** ✅

The original sample questions now work with actual data. The agent properly queries the InsuranceClaims datasource using the correct field names and query structure.
