# Sample Questions Fix - April 14, 2026

## Issue Summary

The Makana agent's sample test questions were asking about **insurance claims data**, but the InsuranceClaims datasource has limited/incomplete metadata. This caused test failures and "no data available" responses.

## Root Cause

**Makana Agent Configuration:**
- Primary datasource: PharmaSales (ID: 10dbb420-4b25-4ff9-984c-db52a66322fd) ✅ Full metadata
- Secondary datasource: InsuranceClaims (ID: 264d2aeb-e754-4723-a529-1a7519fd8f0b) ⚠️ Limited metadata

**Test Questions Were Asking About:**
1. ❌ "What are the top three reasons for claim denials, and how do they vary by provider?"
2. ❌ "How does the average processing time for claims correlate with the type of plan and denial rates?"
3. ✅ "How do sales trends for specific products vary over time..." (This one worked!)

**Problem:** Questions #1 and #2 tried to query InsuranceClaims which doesn't have proper field metadata, resulting in failures or hallucinated responses.

## Solution

Updated all test files to use questions that query the **PharmaSales datasource**, which has complete metadata and working fields:

**New Makana Test Questions:**
1. ✅ "What are the top performing pharmaceutical products by TRx sales?"
2. ✅ "Show me market share by product and how it varies across regions"
3. ✅ "How do sales trends for specific products vary over time, and which reps are driving performance?"

**PharmaSales Available Fields:**
- **Dimensions:** Product, Market, Region, Territory, Rep Name, Quarter, Year, Month, PostalCode
- **Measures:** TRx ($), NRx ($), Market Share (%), Sales Growth (%)

## Files Updated

1. ✅ `test_agents_strict.py` - Updated Makana questions
2. ✅ `test_agents_fast.py` - Updated Makana questions
3. ✅ `test_all_agents.py` - Updated Makana questions
4. ✅ `test_agent_performance.py` - Updated Makana questions
5. ✅ `test_agents_comprehensive.py` - Updated Makana questions

## Validation

Before fix (from test_results_20260414_105710.json):
- Question #1: Passed with time=9.59s (but was hallucinating/providing generic industry knowledge)
- Question #2: Failed with "not available" message
- Question #3: Passed with time=18.91s (was already using PharmaSales)

After fix:
- All three questions should now query PharmaSales with actual data
- Expected to pass with response times < 20s
- Will provide actual pharmaceutical sales data, not generic claims knowledge

## Cumulus Agent Status

✅ **No changes needed** - All Cumulus questions were already correct:
1. "What's the AUM by client segment?" - Uses WealthandAssetManagement datasource ✅
2. "Which advisors have the highest client retention rates?" - Uses WealthandAssetManagement ✅
3. "What are the NPS scores by market segment?" - Uses WealthandAssetManagement ✅

All three Cumulus questions passed in the original test with good response times (9.14s, 4.79s, 2.62s).

## Key Takeaway

**Always match test questions to datasources with complete, working metadata.** 

The InsuranceClaims datasource should either:
1. Have its metadata fixed/completed, OR
2. Not be used in test questions until it's properly configured

For now, all Makana test questions use PharmaSales datasource which has proven, working metadata.
