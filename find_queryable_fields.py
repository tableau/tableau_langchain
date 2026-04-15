#!/usr/bin/env python3
"""Find queryable fields for the original questions"""
import sys
import os
import json

sys.path.insert(0, os.path.dirname(__file__))

from dotenv import load_dotenv
load_dotenv()

from experimental.utilities.mcp_tools_dynamic import MCPToolDiscovery

def find_fields_for_questions():
    """Check if InsuranceClaims has fields for the original questions"""

    print("="*80)
    print("FINDING QUERYABLE FIELDS FOR ORIGINAL QUESTIONS")
    print("="*80)

    mcp = MCPToolDiscovery(os.getenv('TABLEAU_MCP_URL'))
    metadata = mcp.call_tool('get-datasource-metadata', {
        'datasourceLuid': '264d2aeb-e754-4723-a529-1a7519fd8f0b'
    })

    # Extract all field names
    all_fields = []
    if 'fieldGroups' in metadata:
        for group in metadata['fieldGroups']:
            if 'fields' in group:
                for field in group['fields']:
                    field_info = {
                        'name': field.get('name', ''),
                        'dataType': field.get('dataType', ''),
                        'role': field.get('role', ''),
                        'columnClass': field.get('columnClass', '')
                    }
                    all_fields.append(field_info)

    print(f"\nTotal fields found: {len(all_fields)}")

    # Question 1: "What are the top three reasons for claim denials, and how do they vary by provider?"
    print("\n" + "="*80)
    print("QUESTION 1: Top reasons for claim denials by provider")
    print("="*80)
    print("\nSearching for fields containing:")
    print("  - 'denial' or 'deny' or 'reject'")
    print("  - 'reason' or 'cause'")
    print("  - 'provider' or 'agent' or 'group'")

    denial_fields = [f for f in all_fields if any(term in f['name'].lower() for term in ['denial', 'deny', 'reject', 'declined'])]
    reason_fields = [f for f in all_fields if any(term in f['name'].lower() for term in ['reason', 'cause', 'status', 'type'])]
    provider_fields = [f for f in all_fields if any(term in f['name'].lower() for term in ['provider', 'agent', 'group', 'policy'])]

    print(f"\n📊 Denial-related fields: {len(denial_fields)}")
    for f in denial_fields[:10]:
        print(f"   - {f['name']} ({f['role']})")

    print(f"\n📊 Reason/Status fields: {len(reason_fields)}")
    for f in reason_fields[:10]:
        print(f"   - {f['name']} ({f['role']})")

    print(f"\n📊 Provider/Agent fields: {len(provider_fields)}")
    for f in provider_fields[:10]:
        print(f"   - {f['name']} ({f['role']})")

    # Verdict
    print("\n" + "-"*80)
    if len(denial_fields) == 0:
        print("❌ CANNOT ANSWER: No 'denial' fields found!")
        print("   Alternative: Query 'Claim Process Status' or 'Is Reimbursed Flag'")
    else:
        print("✅ CAN ANSWER: Found denial fields")

    # Question 2: "How does the average processing time for claims correlate with the type of plan and denial rates?"
    print("\n" + "="*80)
    print("QUESTION 2: Processing time correlation with plan type and denial rates")
    print("="*80)
    print("\nSearching for fields containing:")
    print("  - 'processing' or 'days' or 'time' or 'duration'")
    print("  - 'plan' or 'policy'")
    print("  - 'rate' or 'percentage'")

    time_fields = [f for f in all_fields if any(term in f['name'].lower() for term in ['processing', 'days', 'time', 'duration', 'close'])]
    plan_fields = [f for f in all_fields if any(term in f['name'].lower() for term in ['plan', 'policy type'])]
    rate_fields = [f for f in all_fields if any(term in f['name'].lower() for term in ['rate', '%', 'percentage'])]

    print(f"\n📊 Time/Duration fields: {len(time_fields)}")
    for f in time_fields[:15]:
        print(f"   - {f['name']} ({f['role']})")

    print(f"\n📊 Plan/Policy fields: {len(plan_fields)}")
    for f in plan_fields[:10]:
        print(f"   - {f['name']} ({f['role']})")

    print(f"\n📊 Rate/Percentage fields: {len(rate_fields)}")
    for f in rate_fields[:10]:
        print(f"   - {f['name']} ({f['role']})")

    # Verdict
    print("\n" + "-"*80)
    if len(time_fields) > 0 and len(plan_fields) > 0:
        print("✅ CAN POTENTIALLY ANSWER")
        print("   Recommended fields:")
        print("     - Time: 'Days to Close' or 'Average Days to Close'")
        print("     - Plan: 'Policy Type'")
        print("     - Consider: May not have 'denial rate' specifically")
    else:
        print("❌ CANNOT FULLY ANSWER")

    # Summary
    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80)
    print("""
The InsuranceClaims datasource has:
  ✅ Claims data (open, closed, reimbursed)
  ✅ Time metrics (Days to Close, processing duration)
  ✅ Policy types
  ✅ Agent/Group dimensions
  ❌ NO explicit "denial" or "denial reason" fields
  ❌ NO "provider" field (has "Agent" instead)

RECOMMENDED QUESTIONS FOR INSURANCECLAIMS:
  1. What's the average processing time (Days to Close) by Policy Type?
  2. How does the reimbursement rate vary by Agent Group?
  3. What are the trends in Claims Closed vs Open Claims over time?
""")

if __name__ == "__main__":
    find_fields_for_questions()
