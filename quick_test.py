#!/usr/bin/env python3
"""Quick diagnostic test for agents"""
import asyncio
import time
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from dotenv import load_dotenv
load_dotenv()

from experimental.agents.superstore.agent import analytics_agent

async def test_simple_question():
    """Test a single simple question"""
    print("Testing Superstore agent with: 'List the Datasources'")
    print("=" * 80)

    start = time.time()

    try:
        response = await analytics_agent.ainvoke({
            "messages": [{"role": "user", "content": "List the Datasources"}]
        })

        elapsed = time.time() - start

        print(f"\n✓ Response received in {elapsed:.2f}s")
        print("\nResponse:")
        print("-" * 80)

        if response and "messages" in response:
            for msg in response["messages"]:
                if hasattr(msg, 'content'):
                    print(msg.content)
                else:
                    print(msg)
        else:
            print(response)

        print("-" * 80)
        print(f"\n✅ Test completed successfully in {elapsed:.2f}s")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("Running quick diagnostic test...\n")
    asyncio.run(test_simple_question())
