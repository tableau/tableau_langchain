#!/usr/bin/env python3
"""
Test script for the enhanced Tableau MCP Tool.
This demonstrates how the tool can now handle various types of questions about Tableau resources.
"""

import os
import sys
sys.path.append('.')

from experimental.tools.tableau_mcp_tool import initialize_tableau_mcp_tool

def test_enhanced_mcp_tool():
    """Test the enhanced MCP tool with various questions."""

    # Initialize the tool
    tool = initialize_tableau_mcp_tool()

    # Test questions
    test_questions = [
        "What data sources are available?",
        "List all workbooks",
        "What pulse metrics are available?",
        "Show me views in workbook abc123",
        "What dashboards are in workbook xyz789?",
        "What can you help me with?",
    ]

    print("🧪 Testing Enhanced Tableau MCP Tool")
    print("=" * 50)

    for i, question in enumerate(test_questions, 1):
        print(f"\n{i}. Question: {question}")
        print("-" * 30)

        try:
            result = tool._run(question)
            print(result)
        except Exception as e:
            print(f"❌ Error: {e}")

        print()

if __name__ == "__main__":
    test_enhanced_mcp_tool()
