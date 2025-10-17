#!/usr/bin/env python3
"""
Test script for language blocking functionality
"""
import requests
import sys

BASE_URL = "http://localhost:5000"

# Test cases: (description, query_text, should_block)
test_cases = [
    ("English query", "What is the total sales?", False),
    ("Spanish query", "¿Cuál es el total de ventas?", True),
    ("Chinese query", "总销售额是多少？", True),
    ("Russian query", "Какова общая сумма продаж?", True),
    ("Arabic query", "ما هو إجمالي المبيعات؟", True),
    ("French query", "Quel est le total des ventes?", True),
    ("Mixed with numbers", "Show me sales for Q4 2023", False),
    ("Short English", "sales", False),
]

print("\n" + "="*60)
print("Language Blocking Test")
print("="*60 + "\n")

# Note: You'll need a valid API key from your .env
API_KEY = "maNaB2Od6bHYSulEANX2Cjrux6yzC84zqcEWPf_VHi4"  # Use one of your generated keys

passed = 0
failed = 0

for description, query, should_block in test_cases:
    try:
        response = requests.post(
            f"{BASE_URL}/search",
            headers={"X-API-Key": API_KEY},
            data={"query": query},
            timeout=5
        )

        blocked = response.status_code == 403 and 'language' in response.text.lower()

        # Check if behavior matches expectation
        if blocked == should_block:
            status = "✅ PASS"
            passed += 1
        else:
            status = "❌ FAIL"
            failed += 1

        block_status = "BLOCKED" if blocked else "ALLOWED"
        expected = "should block" if should_block else "should allow"

        print(f"{status} - {description}")
        print(f"  Query: {query[:50]}")
        print(f"  Result: {block_status} (HTTP {response.status_code})")
        print(f"  Expected: {expected}")
        print()

    except requests.exceptions.ConnectionError:
        print(f"❌ ERROR - Cannot connect to {BASE_URL}")
        print("   Make sure the Flask app is running!")
        sys.exit(1)
    except Exception as e:
        print(f"❌ ERROR - {description}: {e}")
        failed += 1

print("="*60)
print(f"Results: {passed} passed, {failed} failed")
print("="*60 + "\n")

if failed > 0:
    sys.exit(1)

