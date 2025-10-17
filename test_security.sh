#!/bin/bash
# Quick security test script
# Tests the API security features

echo "========================================"
echo "Security Test Suite"
echo "========================================"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

BASE_URL="http://localhost:5000"

echo "Testing health endpoint (no auth required)..."
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" $BASE_URL/health)
if [ $HTTP_CODE -eq 200 ]; then
    echo -e "${GREEN}✓${NC} Health check: PASSED (200)"
else
    echo -e "${RED}✗${NC} Health check: FAILED ($HTTP_CODE)"
fi
echo ""

echo "Testing search without API key (should fail)..."
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" -X POST $BASE_URL/search -F "query=test")
if [ $HTTP_CODE -eq 401 ] || [ $HTTP_CODE -eq 403 ]; then
    echo -e "${GREEN}✓${NC} No API key: BLOCKED ($HTTP_CODE) ✓"
else
    echo -e "${RED}✗${NC} No API key: NOT BLOCKED ($HTTP_CODE) - SECURITY ISSUE!"
fi
echo ""

echo "Testing with invalid API key (should fail)..."
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" -X POST $BASE_URL/search -H "X-API-Key: invalid-key-12345" -F "query=test")
if [ $HTTP_CODE -eq 401 ] || [ $HTTP_CODE -eq 403 ]; then
    echo -e "${GREEN}✓${NC} Invalid API key: BLOCKED ($HTTP_CODE) ✓"
else
    echo -e "${RED}✗${NC} Invalid API key: NOT BLOCKED ($HTTP_CODE) - SECURITY ISSUE!"
fi
echo ""

echo "Testing rate limiting (rapid requests)..."
echo "Sending 15 rapid requests (limit is 10/min)..."
SUCCESS=0
RATE_LIMITED=0

for i in {1..15}; do
    HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" -X POST $BASE_URL/search -H "X-API-Key: test-key" -F "query=test" 2>/dev/null)
    if [ $HTTP_CODE -eq 429 ]; then
        RATE_LIMITED=$((RATE_LIMITED + 1))
    elif [ $HTTP_CODE -eq 200 ] || [ $HTTP_CODE -eq 400 ]; then
        SUCCESS=$((SUCCESS + 1))
    fi
    sleep 0.1
done

echo "  Successful requests: $SUCCESS"
echo "  Rate limited: $RATE_LIMITED"

if [ $RATE_LIMITED -gt 0 ]; then
    echo -e "${GREEN}✓${NC} Rate limiting: WORKING ✓"
else
    echo -e "${YELLOW}⚠${NC}  Rate limiting: Not triggered (may need valid API key in .env)"
fi
echo ""

echo "Testing admin stats endpoint..."
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" $BASE_URL/admin/stats)
if [ $HTTP_CODE -eq 401 ] || [ $HTTP_CODE -eq 403 ]; then
    echo -e "${GREEN}✓${NC} Admin stats: PROTECTED ($HTTP_CODE) ✓"
else
    echo -e "${YELLOW}⚠${NC}  Admin stats: Response code $HTTP_CODE"
fi
echo ""

echo "========================================"
echo "Security Test Summary"
echo "========================================"
echo ""
echo "Next steps:"
echo "1. Check api_usage.log for detailed logs"
echo "2. Run: python experimental/utilities/monitor_usage.py"
echo "3. Review SECURITY_SETUP.md for production deployment"
echo ""
echo "To test with a valid API key:"
echo "  1. Set ALLOWED_API_KEYS in .env"
echo "  2. curl -X POST $BASE_URL/search \\"
echo "       -H 'X-API-Key: your-key-here' \\"
echo "       -F 'query=test query'"
echo ""

