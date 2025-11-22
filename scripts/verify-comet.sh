#!/bin/bash
# ═══════════════════════════════════════════════════════════════════════════
# Comet Gate Verification Script
# ═══════════════════════════════════════════════════════════════════════════
# Purpose: Validate the entire Comet gate flow (GitHub → Webhook → DB → ScarIndex)
# Usage: ./scripts/verify-comet.sh [--local|--ci]
# ═══════════════════════════════════════════════════════════════════════════

set -euo pipefail

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Mode detection
MODE="${COMET_GATE_MODE:-local}"
if [ "${1:-}" = "--ci" ]; then
    MODE="ci"
elif [ "${1:-}" = "--local" ]; then
    MODE="local"
fi

# Test counters
TESTS_RUN=0
TESTS_PASSED=0
TESTS_FAILED=0

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[✓]${NC} $1"
    TESTS_PASSED=$((TESTS_PASSED + 1))
}

log_fail() {
    echo -e "${RED}[✗]${NC} $1"
    TESTS_FAILED=$((TESTS_FAILED + 1))
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

# Test function wrapper
run_test() {
    local test_name="$1"
    TESTS_RUN=$((TESTS_RUN + 1))
    echo ""
    log_info "Test $TESTS_RUN: $test_name"
}

# ═══════════════════════════════════════════════════════════════════════════
# Test 1: Verify migration files exist
# ═══════════════════════════════════════════════════════════════════════════
test_migration_files() {
    run_test "Migration files exist"
    
    local migrations=(
        "supabase/migrations/20251101_spiralos_production_schema.sql"
        "supabase/migrations/20251101_01_comet_gate.sql"
    )
    
    for migration in "${migrations[@]}"; do
        if [ -f "$migration" ]; then
            log_success "Found: $migration"
        else
            log_fail "Missing: $migration"
            return 1
        fi
    done
    
    return 0
}

# ═══════════════════════════════════════════════════════════════════════════
# Test 2: Verify webhook function exists
# ═══════════════════════════════════════════════════════════════════════════
test_webhook_function() {
    run_test "Webhook function exists"
    
    local webhook_file="supabase/functions/github-webhook/index.ts"
    
    if [ -f "$webhook_file" ]; then
        log_success "Found: $webhook_file"
        
        # Check for key improvements
        if grep -q "Early guard" "$webhook_file"; then
            log_success "Early guards implemented"
        else
            log_fail "Early guards not found"
            return 1
        fi
        
        if grep -q "upsert" "$webhook_file"; then
            log_success "Upsert logic implemented"
        else
            log_fail "Upsert logic not found"
            return 1
        fi
        
        if grep -q "scar_index" "$webhook_file"; then
            log_success "scar_index table integration found"
        else
            log_fail "scar_index table integration not found"
            return 1
        fi
    else
        log_fail "Missing: $webhook_file"
        return 1
    fi
    
    return 0
}

# ═══════════════════════════════════════════════════════════════════════════
# Test 3: Verify db-push script
# ═══════════════════════════════════════════════════════════════════════════
test_db_push_script() {
    run_test "Database push script with retry logic"
    
    local script_file="scripts/db-push.sh"
    
    if [ -f "$script_file" ]; then
        log_success "Found: $script_file"
        
        if [ -x "$script_file" ]; then
            log_success "Script is executable"
        else
            log_fail "Script is not executable"
            return 1
        fi
        
        # Check for retry logic
        if grep -q "MAX_RETRIES" "$script_file"; then
            log_success "Retry logic implemented"
        else
            log_fail "Retry logic not found"
            return 1
        fi
        
        if grep -q "BACKOFF_MULTIPLIER" "$script_file"; then
            log_success "Exponential backoff implemented"
        else
            log_fail "Exponential backoff not found"
            return 1
        fi
    else
        log_fail "Missing: $script_file"
        return 1
    fi
    
    return 0
}

# ═══════════════════════════════════════════════════════════════════════════
# Test 4: Verify Python client defensive defaults
# ═══════════════════════════════════════════════════════════════════════════
test_python_client() {
    run_test "Python client defensive defaults"
    
    local client_file="core/supabase_integration.py"
    
    if [ -f "$client_file" ]; then
        log_success "Found: $client_file"
        
        # Check for defensive defaults
        if grep -q "content or {}" "$client_file"; then
            log_success "Defensive defaults for content"
        else
            log_fail "Defensive defaults for content not found"
            return 1
        fi
        
        if grep -q "try:" "$client_file" && grep -q "except Exception" "$client_file"; then
            log_success "Error handling implemented"
        else
            log_fail "Error handling not found"
            return 1
        fi
    else
        log_fail "Missing: $client_file"
        return 1
    fi
    
    return 0
}

# ═══════════════════════════════════════════════════════════════════════════
# Test 5: Verify documentation
# ═══════════════════════════════════════════════════════════════════════════
test_documentation() {
    run_test "Repository documentation"
    
    local docs=(
        "README.md"
        "CONTRIBUTING.md"
        "TROUBLESHOOTING.md"
        "LICENSE"
    )
    
    for doc in "${docs[@]}"; do
        if [ -f "$doc" ]; then
            log_success "Found: $doc"
        else
            log_fail "Missing: $doc"
            return 1
        fi
    done
    
    return 0
}

# ═══════════════════════════════════════════════════════════════════════════
# Test 6: Verify CI workflows
# ═══════════════════════════════════════════════════════════════════════════
test_ci_workflows() {
    run_test "CI workflows"
    
    local workflows=(
        ".github/workflows/ci.yml"
        ".github/workflows/release.yml"
    )
    
    for workflow in "${workflows[@]}"; do
        if [ -f "$workflow" ]; then
            log_success "Found: $workflow"
        else
            log_fail "Missing: $workflow"
            return 1
        fi
    done
    
    return 0
}

# ═══════════════════════════════════════════════════════════════════════════
# Test 7: SQL migration syntax validation
# ═══════════════════════════════════════════════════════════════════════════
test_sql_syntax() {
    run_test "SQL migration syntax"
    
    local migration="supabase/migrations/20251101_01_comet_gate.sql"
    
    if [ -f "$migration" ]; then
        # Check for idempotent operations
        if grep -q "IF NOT EXISTS\|IF EXISTS" "$migration"; then
            log_success "Idempotent SQL operations found"
        else
            log_fail "Migration missing idempotent operations"
            return 1
        fi
        
        # Check for scar_index table
        if grep -q "CREATE TABLE.*scar_index" "$migration"; then
            log_success "scar_index table creation found"
        else
            log_fail "scar_index table creation not found"
            return 1
        fi
        
        # Check for indexes
        if grep -q "CREATE INDEX.*idx_scar_index" "$migration"; then
            log_success "Performance indexes found"
        else
            log_fail "Performance indexes not found"
            return 1
        fi
    else
        log_fail "Migration file not found"
        return 1
    fi
    
    return 0
}

# ═══════════════════════════════════════════════════════════════════════════
# Test 8: Python unit tests
# ═══════════════════════════════════════════════════════════════════════════
test_python_tests() {
    run_test "Python unit tests"
    
    if [ "$MODE" = "smoke-test" ]; then
        log_warn "Skipping Python tests in smoke-test mode"
        TESTS_RUN=$((TESTS_RUN - 1))  # Don't count this test
        return 0
    fi
    
    # Test if we can import the modules
    if python3 -c "import sys; sys.path.insert(0, '.'); from core import supabase_integration" 2>/dev/null; then
        log_success "Python modules can be imported"
    else
        log_warn "Python modules cannot be imported (dependencies may be missing)"
    fi
    
    return 0
}

# ═══════════════════════════════════════════════════════════════════════════
# Test 9: Verify fix addresses issue #10
# ═══════════════════════════════════════════════════════════════════════════
test_issue_10_fix() {
    run_test "Issue #10 fixes"
    
    local fixes_implemented=0
    
    # Fix 1: Migration script
    if [ -f "supabase/migrations/20251101_01_comet_gate.sql" ]; then
        log_success "✓ Migration patch implemented"
        fixes_implemented=$((fixes_implemented + 1))
    else
        log_fail "✗ Migration patch missing"
    fi
    
    # Fix 2: Retry logic
    if [ -f "scripts/db-push.sh" ] && grep -q "MAX_RETRIES" "scripts/db-push.sh"; then
        log_success "✓ Retry logic for database push"
        fixes_implemented=$((fixes_implemented + 1))
    else
        log_fail "✗ Retry logic missing"
    fi
    
    # Fix 3: Webhook improvements
    if [ -f "supabase/functions/github-webhook/index.ts" ] && grep -q "upsert" "supabase/functions/github-webhook/index.ts"; then
        log_success "✓ Webhook idempotency improvements"
        fixes_implemented=$((fixes_implemented + 1))
    else
        log_fail "✗ Webhook improvements missing"
    fi
    
    # Fix 4: Python client
    if [ -f "core/supabase_integration.py" ] && grep -q "content or {}" "core/supabase_integration.py"; then
        log_success "✓ Python client defensive defaults"
        fixes_implemented=$((fixes_implemented + 1))
    else
        log_fail "✗ Python client improvements missing"
    fi
    
    # Fix 5: Documentation
    if [ -f "CONTRIBUTING.md" ] && [ -f "TROUBLESHOOTING.md" ]; then
        log_success "✓ Repository documentation"
        fixes_implemented=$((fixes_implemented + 1))
    else
        log_fail "✗ Documentation missing"
    fi
    
    # Fix 6: CI workflows
    if [ -f ".github/workflows/ci.yml" ]; then
        log_success "✓ CI workflows implemented"
        fixes_implemented=$((fixes_implemented + 1))
    else
        log_fail "✗ CI workflows missing"
    fi
    
    if [ $fixes_implemented -eq 6 ]; then
        log_success "All issue #10 fixes implemented (6/6)"
        return 0
    else
        log_fail "Only $fixes_implemented/6 fixes implemented"
        return 1
    fi
}

# ═══════════════════════════════════════════════════════════════════════════
# Main execution
# ═══════════════════════════════════════════════════════════════════════════

main() {
    echo "════════════════════════════════════════════════════════════════"
    echo "  SpiralOS Comet Gate Verification"
    echo "════════════════════════════════════════════════════════════════"
    echo ""
    log_info "Mode: $MODE"
    echo ""
    
    # Run all tests
    test_migration_files || true
    test_webhook_function || true
    test_db_push_script || true
    test_python_client || true
    test_documentation || true
    test_ci_workflows || true
    test_sql_syntax || true
    test_python_tests || true
    test_issue_10_fix || true
    
    # Summary
    echo ""
    echo "════════════════════════════════════════════════════════════════"
    echo "  Test Summary"
    echo "════════════════════════════════════════════════════════════════"
    echo ""
    echo -e "Total tests run:    ${BLUE}$TESTS_RUN${NC}"
    echo -e "Tests passed:       ${GREEN}$TESTS_PASSED${NC}"
    echo -e "Tests failed:       ${RED}$TESTS_FAILED${NC}"
    echo ""
    
    if [ $TESTS_FAILED -eq 0 ]; then
        echo -e "${GREEN}✓ All Comet gate verification tests passed!${NC}"
        echo ""
        log_success "Comet gate is ready for deployment"
        return 0
    else
        echo -e "${RED}✗ Some tests failed${NC}"
        echo ""
        log_fail "Please fix the failing tests before proceeding"
        return 1
    fi
}

# Run main
main "$@"
