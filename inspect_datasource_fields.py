#!/usr/bin/env python3
"""Inspect actual fields in InsuranceClaims datasource"""
import sys
import os
import json

sys.path.insert(0, os.path.dirname(__file__))

from dotenv import load_dotenv
load_dotenv()

from experimental.utilities.mcp_tools_dynamic import MCPToolDiscovery

def inspect_datasource(ds_name, ds_id):
    """Get full metadata for a datasource"""
    print(f"\n{'='*80}")
    print(f"Datasource: {ds_name}")
    print(f"ID: {ds_id}")
    print(f"{'='*80}")

    try:
        mcp = MCPToolDiscovery(os.getenv('TABLEAU_MCP_URL'))

        # Get metadata
        metadata = mcp.call_tool('get-datasource-metadata', {'datasourceLuid': ds_id})

        # Print full structure
        print("\nFull metadata structure:")
        print(json.dumps(metadata, indent=2)[:5000])  # First 5000 chars

        # Try to extract fields
        if isinstance(metadata, dict):
            if 'fieldGroups' in metadata:
                print(f"\n\nFound {len(metadata['fieldGroups'])} field groups")
                for group_idx, group in enumerate(metadata['fieldGroups']):
                    print(f"\n--- Field Group {group_idx + 1} ---")
                    if 'fields' in group:
                        print(f"Fields in this group: {len(group['fields'])}")

                        # Categorize fields
                        dimensions = []
                        measures = []

                        for field in group['fields']:
                            field_name = field.get('name', 'Unknown')
                            data_type = field.get('dataType', 'Unknown')
                            column_class = field.get('columnClass', 'Unknown')

                            # Guess if dimension or measure based on data type
                            if data_type in ['REAL', 'INTEGER'] and 'CALCULATION' in column_class.upper():
                                measures.append(field_name)
                            elif data_type in ['STRING', 'DATE', 'DATETIME']:
                                dimensions.append(field_name)
                            elif data_type in ['REAL', 'INTEGER']:
                                measures.append(field_name)

                        print(f"\n📊 Likely Dimensions ({len(dimensions)}):")
                        for d in dimensions[:20]:
                            print(f"  - {d}")

                        print(f"\n📈 Likely Measures ({len(measures)}):")
                        for m in measures[:20]:
                            print(f"  - {m}")

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    # Check InsuranceClaims first
    inspect_datasource(
        "InsuranceClaims",
        "264d2aeb-e754-4723-a529-1a7519fd8f0b"
    )
