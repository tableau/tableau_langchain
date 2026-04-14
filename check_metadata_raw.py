#!/usr/bin/env python3
"""Check raw metadata structure"""
import sys
import os
import json

sys.path.insert(0, os.path.dirname(__file__))

from dotenv import load_dotenv
load_dotenv()

from experimental.utilities.mcp_tools_dynamic import MCPToolDiscovery

def check_raw_metadata(ds_name, ds_id):
    """Get raw metadata"""
    print(f"\n{'='*80}")
    print(f"Datasource: {ds_name}")
    print(f"{'='*80}")

    try:
        mcp = MCPToolDiscovery(os.getenv('TABLEAU_MCP_URL'))
        metadata = mcp.call_tool('get-datasource-metadata', {'datasourceLuid': ds_id})

        print(f"\nRaw metadata type: {type(metadata)}")
        print(f"\nMetadata keys: {list(metadata.keys()) if isinstance(metadata, dict) else 'N/A'}")

        if isinstance(metadata, dict) and 'fields' in metadata:
            fields = metadata['fields']
            print(f"\nTotal fields: {len(fields)}")

            # Show first 3 fields with full structure
            print(f"\nFirst 3 fields (full structure):")
            for i, field in enumerate(fields[:3]):
                print(f"\nField {i+1}:")
                print(json.dumps(field, indent=2))

        else:
            print(f"\nRaw metadata: {json.dumps(metadata, indent=2)[:500]}...")

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_raw_metadata("PharmaSales", "10dbb420-4b25-4ff9-984c-db52a66322fd")
    check_raw_metadata("WealthandAssetManagement", "f4f9467e-4daa-4256-9698-a703be25fafa")
