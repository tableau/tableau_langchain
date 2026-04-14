#!/usr/bin/env python3
"""Check what fields are available in Makana and Cumulus datasources"""
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from dotenv import load_dotenv
load_dotenv()

from experimental.utilities.mcp_tools_dynamic import MCPToolDiscovery

def check_datasource_fields(ds_name, ds_id):
    """Get metadata for a datasource"""
    print(f"\n{'='*80}")
    print(f"Datasource: {ds_name}")
    print(f"ID: {ds_id}")
    print(f"{'='*80}")

    try:
        mcp = MCPToolDiscovery(os.getenv('TABLEAU_MCP_URL'))

        # Get metadata
        metadata = mcp.call_tool('get-datasource-metadata', {'datasourceLuid': ds_id})

        # Extract field names
        if isinstance(metadata, dict) and 'fields' in metadata:
            fields = metadata['fields']
            print(f"\nTotal fields: {len(fields)}")

            # Group by role
            dimensions = [f for f in fields if f.get('role') == 'dimension']
            measures = [f for f in fields if f.get('role') == 'measure']

            print(f"\n📊 Dimensions ({len(dimensions)}):")
            for field in dimensions[:15]:  # Show first 15
                field_name = field.get('fieldCaption', field.get('name', 'Unknown'))
                print(f"  - {field_name}")
            if len(dimensions) > 15:
                print(f"  ... and {len(dimensions) - 15} more")

            print(f"\n📈 Measures ({len(measures)}):")
            for field in measures[:15]:  # Show first 15
                field_name = field.get('fieldCaption', field.get('name', 'Unknown'))
                print(f"  - {field_name}")
            if len(measures) > 15:
                print(f"  ... and {len(measures) - 15} more")

        else:
            print(f"⚠️  Unexpected metadata format: {str(metadata)[:200]}")

    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    # Makana datasources
    print("\n" + "#" * 80)
    print("# MAKANA DATASOURCES")
    print("#" * 80)
    check_datasource_fields(
        "InsuranceClaims",
        "264d2aeb-e754-4723-a529-1a7519fd8f0b"
    )
    check_datasource_fields(
        "PharmaSales",
        "10dbb420-4b25-4ff9-984c-db52a66322fd"
    )

    # Cumulus datasources
    print("\n\n" + "#" * 80)
    print("# CUMULUS DATASOURCES")
    print("#" * 80)
    check_datasource_fields(
        "WealthandAssetManagement",
        "f4f9467e-4daa-4256-9698-a703be25fafa"
    )
    check_datasource_fields(
        "RetailBanking-LoanPerformance",
        "a6d24d21-90a0-4fd3-892b-ce33b35d801e"
    )
