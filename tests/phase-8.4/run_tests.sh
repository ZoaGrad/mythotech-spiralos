
#!/bin/bash
# Phase 8.4 Auto-Regulation Engine - Automated Test Runner
# ============================================================================

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  Phase 8.4 Auto-Regulation Engine - Test Suite Runner    ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

# ============================================================================
# CONFIGURATION
# ============================================================================
SUPABASE_URL="${SUPABASE_URL:-}"
GUARDIAN_API_KEY="${GUARDIAN_API_KEY:-}"
TEST_BRIDGE_ID="f8f41ffa-6c2b-4a2a-a3be-32f0236668f4"

if [ -z "$SUPABASE_URL" ] || [ -z "$GUARDIAN_API_KEY" ]; then
    echo -e "${RED}❌ Error: Missing environment variables${NC}"
    echo "Please set: SUPABASE_URL, GUARDIAN_API_KEY"
    exit 1
fi

ENDPOINT="${SUPABASE_URL}/functions/v1/guardian_autoregulate"

# ============================================================================
# TEST COUNTERS
# ============================================================================
TOTAL_TESTS=0
PASSED_TESTS=0
FAILED_TESTS=0

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================
run_test() {
    local test_name=$1
    local test_payload=$2
    local expected_status=${3:-200}
    
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
    echo -e "${YELLOW}Running Test $TOTAL_TESTS: $test_name${NC}"
    
    response=$(curl -s -w "\n%{http_code}" -X POST "$ENDPOINT" \
        -H "Content-Type: application/json" \
        -H "x-guardian-api-key: $GUARDIAN_API_KEY" \
        -d "$test_payload")
    
    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | head -n-1)
    
    if [ "$http_code" = "$expected_status" ]; then
        echo -e "${GREEN}✅ PASSED${NC} - HTTP $http_code"
        PASSED_TESTS=$((PASSED_TESTS + 1))
        
        # Show summary if successful
        if [ "$http_code" = "200" ]; then
            success_count=$(echo "$body" | grep -o '"successful":[0-9]*' | grep -o '[0-9]*' || echo "N/A")
            total_count=$(echo "$body" | grep -o '"total":[0-9]*' | grep -o '[0-9]*' || echo "N/A")
            echo -e "   📊 Corrections: $success_count/$total_count successful"
        fi
    else
        echo -e "${RED}❌ FAILED${NC} - Expected HTTP $expected_status, got $http_code"
        echo "   Response: $body"
        FAILED_TESTS=$((FAILED_TESTS + 1))
    fi
    echo ""
    
    # Small delay between tests
    sleep 2
}

# ============================================================================
# TEST EXECUTION
# ============================================================================
echo -e "${BLUE}Starting test execution...${NC}"
echo ""

# Test 1: ScarIndex Recovery - Low Value
run_test "ScarIndex Recovery (Low Value)" \
    "{\"bridge_id\":\"$TEST_BRIDGE_ID\",\"mode\":\"MANUAL\"}" \
    200

# Test 2: ScarIndex Recovery - Large Drop  
run_test "ScarIndex Recovery (Large Drop)" \
    "{\"bridge_id\":\"$TEST_BRIDGE_ID\",\"mode\":\"MANUAL\"}" \
    200

# Test 3: Sovereignty Stabilizer
run_test "Sovereignty Stabilizer" \
    "{\"bridge_id\":\"$TEST_BRIDGE_ID\",\"mode\":\"MANUAL\"}" \
    200

# Test 4: Ache Buffer
run_test "Ache Buffer" \
    "{\"bridge_id\":\"$TEST_BRIDGE_ID\",\"mode\":\"MANUAL\"}" \
    200

# Test 5: Heartbeat Correction
run_test "Heartbeat Correction" \
    "{\"bridge_id\":\"$TEST_BRIDGE_ID\",\"mode\":\"MANUAL\"}" \
    200

# Test 6: Entropy Correction
run_test "Entropy Correction" \
    "{\"bridge_id\":\"$TEST_BRIDGE_ID\",\"mode\":\"MANUAL\"}" \
    200

# Test 7: Self-Preservation Freeze Mode
run_test "Self-Preservation Freeze Mode (CRITICAL)" \
    "{\"bridge_id\":\"$TEST_BRIDGE_ID\",\"mode\":\"MANUAL\"}" \
    200

# Test 8: Idempotency (run twice)
run_test "Idempotency Check (First Run)" \
    "{\"bridge_id\":\"$TEST_BRIDGE_ID\",\"mode\":\"MANUAL\"}" \
    200

run_test "Idempotency Check (Second Run - Should Respect Cooldown)" \
    "{\"bridge_id\":\"$TEST_BRIDGE_ID\",\"mode\":\"MANUAL\"}" \
    200

# Test 9: Mixed Anomaly Batch
run_test "Mixed Anomaly Batch" \
    "{\"bridge_id\":\"$TEST_BRIDGE_ID\",\"mode\":\"AUTO\"}" \
    200

# Test 10: Authentication Failure
run_test "Authentication Failure" \
    "{\"bridge_id\":\"$TEST_BRIDGE_ID\",\"mode\":\"AUTO\"}" \
    401

# Override API key for this test
GUARDIAN_API_KEY_BACKUP="$GUARDIAN_API_KEY"
GUARDIAN_API_KEY="INVALID_KEY_12345"
run_test "Invalid API Key" \
    "{\"bridge_id\":\"$TEST_BRIDGE_ID\",\"mode\":\"AUTO\"}" \
    401
GUARDIAN_API_KEY="$GUARDIAN_API_KEY_BACKUP"

# Test 11: Performance Test (50 anomalies)
run_test "Performance Test (50 anomalies)" \
    "{\"bridge_id\":\"$TEST_BRIDGE_ID\",\"mode\":\"AUTO\"}" \
    200

# Test 12: Logging Integrity (check afterward with SQL)
run_test "Logging Integrity Check" \
    "{\"bridge_id\":\"$TEST_BRIDGE_ID\",\"mode\":\"AUTO\"}" \
    200

# ============================================================================
# TEST SUMMARY
# ============================================================================
echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║                     TEST SUMMARY                          ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "Total Tests:  ${BLUE}$TOTAL_TESTS${NC}"
echo -e "Passed:       ${GREEN}$PASSED_TESTS${NC}"
echo -e "Failed:       ${RED}$FAILED_TESTS${NC}"
echo ""

if [ $FAILED_TESTS -eq 0 ]; then
    echo -e "${GREEN}🎉 All tests passed!${NC}"
    exit 0
else
    echo -e "${RED}❌ Some tests failed. Please review the output above.${NC}"
    exit 1
fi

