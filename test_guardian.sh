#!/bin/bash

# Test Guardian Automation Kit deployment
# This script tests the deployed SQL function and Edge Function

set -e

echo "🧪 Guardian Automation Kit - Test Script"
echo "========================================"

# Check for Edge URL
if [ -z "$1" ]; then
    if [ -f .env ]; then
        source .env
        EDGE_URL="$GUARDIAN_EDGE_URL"
    fi
fi

if [ -z "$EDGE_URL" ]; then
    EDGE_URL="$1"
fi

if [ -z "$EDGE_URL" ]; then
    echo "❌ Edge Function URL not provided"
    echo "Usage: ./test_guardian.sh <EDGE_FUNCTION_URL>"
    echo "Or set GUARDIAN_EDGE_URL in .env file"
    exit 1
fi

echo "Testing Edge Function: $EDGE_URL"
echo ""

# Test 1: Basic health check (24 hours)
echo "Test 1: Basic health check (24 hours)"
echo "--------------------------------------"
RESPONSE_24=$(curl -s "$EDGE_URL?hours=24")

if [ $? -eq 0 ]; then
    echo "✅ Request successful"
    echo "Response:"
    echo "$RESPONSE_24" | jq '.'
    
    # Validate response structure
    if echo "$RESPONSE_24" | jq -e '.timestamp' > /dev/null 2>&1; then
        echo "✅ Response has timestamp"
    else
        echo "❌ Response missing timestamp"
    fi
    
    if echo "$RESPONSE_24" | jq -e '.metrics' > /dev/null 2>&1; then
        echo "✅ Response has metrics"
    else
        echo "❌ Response missing metrics"
    fi
    
    if echo "$RESPONSE_24" | jq -e '.scar_status' > /dev/null 2>&1; then
        echo "✅ Response has scar_status"
    else
        echo "❌ Response missing scar_status"
    fi
else
    echo "❌ Request failed"
    exit 1
fi

echo ""

# Test 2: Extended lookback (72 hours)
echo "Test 2: Extended lookback (72 hours)"
echo "-------------------------------------"
RESPONSE_72=$(curl -s "$EDGE_URL?hours=72")

if [ $? -eq 0 ]; then
    echo "✅ Request successful"
    WINDOW=$(echo "$RESPONSE_72" | jq -r '.window_hours')
    echo "Window hours: $WINDOW"
    
    if [ "$WINDOW" == "72" ]; then
        echo "✅ Correct lookback window"
    else
        echo "⚠️  Unexpected window: $WINDOW (expected 72)"
    fi
else
    echo "❌ Request failed"
fi

echo ""

# Test 3: Response time
echo "Test 3: Response time"
echo "---------------------"
START=$(date +%s%N)
curl -s "$EDGE_URL?hours=24" > /dev/null
END=$(date +%s%N)
DURATION=$((($END - $START) / 1000000))

echo "Response time: ${DURATION}ms"

if [ $DURATION -lt 5000 ]; then
    echo "✅ Response time acceptable (< 5s)"
else
    echo "⚠️  Response time slow (> 5s)"
fi

echo ""

# Test 4: Error handling (invalid parameter)
echo "Test 4: Error handling"
echo "----------------------"
RESPONSE_INVALID=$(curl -s "$EDGE_URL?hours=invalid")

if echo "$RESPONSE_INVALID" | jq -e '.timestamp' > /dev/null 2>&1; then
    echo "✅ Function handles invalid input gracefully"
else
    echo "⚠️  Function may have error handling issues"
fi

echo ""

# Summary
echo "========================================"
echo "✅ All tests completed!"
echo ""
echo "Guardian Status Summary:"
echo "$RESPONSE_24" | jq '{
  status: .scar_status,
  score: .scar_score,
  vault_nodes: .metrics[0].value,
  recent_events: .metrics[1].value,
  alerts: .metrics[4].value
}'

echo ""
echo "Next steps:"
echo "1. Monitor the function regularly"
echo "2. Set up automated health checks"
echo "3. Configure Discord notifications"
echo "4. Review metrics and adjust thresholds if needed"
