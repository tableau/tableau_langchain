#!/usr/bin/env python3
"""Find base (non-calculated) fields in InsuranceClaims"""
import sys
import os
import json

sys.path.insert(0, os.path.dirname(__file__))

from dotenv import load_dotenv
load_dotenv()

from experimental.utilities.mcp_tools_dynamic import MCPToolDiscovery

def find_base_fields():
    mcp = MCPToolDiscovery(os.getenv('TABLEAU_MCP_URL'))
    metadata = mcp.call_tool('get-datasource-metadata', {
        'datasourceLuid': '264d2aeb-e754-4723-a529-1a7519fd8f0b'
    })

    print("="*80)
    print("FINDING BASE (COLUMN) FIELDS - Not calculated fields")
    print("="*80)

    if 'fieldGroups' in metadata:
        for group_idx, group in enumerate(metadata['fieldGroups']):
            if 'fields' in group:
                print(f"\n--- Field Group {group_idx + 1} ---")

                # Find COLUMN class fields (not CALCULATION)
                base_fields = [f for f in group['fields'] if f.get('columnClass') == 'COLUMN']

                print(f"\nBase fields (COLUMN class): {len(base_fields)}")

                dimensions = []
                measures = []

                for field in base_fields:
                    field_name = field.get('name', 'Unknown')
                    data_type = field.get('dataType', 'Unknown')
                    role = field.get('role', 'Unknown')

                    if role == 'DIMENSION':
                        dimensions.append(field_name)
                    elif role == 'MEASURE':
                        measures.append(field_name)

                print(f"\n📊 Base Dimensions ({len(dimensions)}):")
                for d in dimensions:
                    print(f"  - {d}")

                print(f"\n📈 Base Measures ({len(measures)}):")
                for m in measures:
                    print(f"  - {m}")

if __name__ == "__main__":
    find_base_fields()
