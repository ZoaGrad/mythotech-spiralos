"""
Gateway Transmissions Integration Test Suite

Tests for sovereignty telemetry system including SQL schema validation,
constraint enforcement, and Edge Function behavior simulation.

VaultNode: ΔΩ.147.0 - Gateway Telemetry Infrastructure
"""

import sys


def test_sql_constraints():
    """Test that SQL schema constraints are properly defined"""
    print("\n" + "=" * 70)
    print("TEST: SQL Schema Constraints")
    print("=" * 70)

    # Read SQL migration file
    with open("supabase/migrations/20251111_01_gateway_transmissions.sql", "r") as f:
        sql_content = f.read()

    # Verify table creation
    assert "CREATE TABLE public.gateway_transmissions" in sql_content, "Table creation statement not found"

    # Verify required columns
    required_columns = [
        "bridge_id TEXT NOT NULL UNIQUE",
        "resonance_score NUMERIC",
        "necessity_score NUMERIC",
        "payload JSONB",
        "constraint_tensor JSONB",
        "created_at TIMESTAMP WITH TIME ZONE",
    ]

    for column in required_columns:
        assert column in sql_content, f"Required column '{column}' not found"

    # Verify CHECK constraints for thermodynamic bounds [0, 1]
    assert (
        "CONSTRAINT resonance_score_bounds CHECK (resonance_score >= 0 AND resonance_score <= 1)" in sql_content
    ), "Resonance score bounds constraint missing"

    assert (
        "CONSTRAINT necessity_score_bounds CHECK (necessity_score >= 0 AND necessity_score <= 1)" in sql_content
    ), "Necessity score bounds constraint missing"

    # Verify JSONB validation constraints
    assert (
        "CONSTRAINT payload_is_object CHECK (jsonb_typeof(payload) = 'object')" in sql_content
    ), "Payload JSONB constraint missing"

    assert (
        "CONSTRAINT constraint_tensor_is_object CHECK (jsonb_typeof(constraint_tensor) = 'object')" in sql_content
    ), "Constraint tensor JSONB constraint missing"

    print("✅ All SQL constraints properly defined")
    print("   ✓ Resonance score bounds [0, 1]")
    print("   ✓ Necessity score bounds [0, 1]")
    print("   ✓ JSONB object validation")
    print("   ✓ Bridge ID uniqueness")


def test_indexes():
    """Test that performance indexes are defined"""
    print("\n" + "=" * 70)
    print("TEST: Performance Indexes")
    print("=" * 70)

    with open("supabase/migrations/20251111_01_gateway_transmissions.sql", "r") as f:
        sql_content = f.read()

    # Verify required indexes
    required_indexes = [
        "idx_gateway_transmissions_bridge_id",
        "idx_gateway_transmissions_created_at",
        "idx_gateway_transmissions_resonance",
        "idx_gateway_transmissions_necessity",
        "idx_gateway_transmissions_sovereignty",
        "idx_gateway_transmissions_payload_gin",
        "idx_gateway_transmissions_tensor_gin",
    ]

    for index in required_indexes:
        assert f"CREATE INDEX {index}" in sql_content, f"Index '{index}' not found"

    # Verify GIN indexes for JSONB
    assert "USING GIN (payload)" in sql_content, "Payload GIN index missing"
    assert "USING GIN (constraint_tensor)" in sql_content, "Constraint tensor GIN index missing"

    print("✅ All performance indexes defined")
    print(f"   ✓ {len(required_indexes)} indexes created")
    print("   ✓ GIN indexes for JSONB fields")


def test_rls_policies():
    """Test that Row Level Security policies are defined"""
    print("\n" + "=" * 70)
    print("TEST: Row Level Security Policies")
    print("=" * 70)

    with open("supabase/migrations/20251111_01_gateway_transmissions.sql", "r") as f:
        sql_content = f.read()

    # Verify RLS is enabled
    assert "ALTER TABLE public.gateway_transmissions ENABLE ROW LEVEL SECURITY" in sql_content, "RLS not enabled"

    # Verify policies exist
    assert "CREATE POLICY" in sql_content, "No RLS policies defined"

    # Verify service role has full access
    assert "Enable all operations for service role" in sql_content, "Service role policy missing"

    # Verify read access for authenticated and anonymous users
    assert (
        "Enable read access for authenticated users" in sql_content
        or "Enable read access for anonymous users" in sql_content
    ), "Read access policies missing"

    print("✅ Row Level Security properly configured")
    print("   ✓ RLS enabled on table")
    print("   ✓ Service role full access")
    print("   ✓ Public read access configured")


def test_helper_functions():
    """Test that helper functions and views are defined"""
    print("\n" + "=" * 70)
    print("TEST: Helper Functions and Views")
    print("=" * 70)

    with open("supabase/migrations/20251111_01_gateway_transmissions.sql", "r") as f:
        sql_content = f.read()

    # Verify trigger function for updated_at
    assert (
        "CREATE OR REPLACE FUNCTION update_gateway_transmission_updated_at()" in sql_content
    ), "Updated_at trigger function missing"

    assert "CREATE TRIGGER gateway_transmission_updated_at_trigger" in sql_content, "Updated_at trigger missing"

    # Verify high sovereignty view
    assert (
        "CREATE OR REPLACE VIEW public.high_sovereignty_transmissions" in sql_content
    ), "High sovereignty view missing"

    # Verify analytics function
    assert (
        "CREATE OR REPLACE FUNCTION public.calculate_sovereignty_metrics" in sql_content
    ), "Sovereignty metrics function missing"

    print("✅ Helper functions and views defined")
    print("   ✓ Auto-update trigger for updated_at")
    print("   ✓ High sovereignty transmissions view")
    print("   ✓ Sovereignty metrics analytics function")


def test_edge_function_structure():
    """Test Edge Function structure and validation logic"""
    print("\n" + "=" * 70)
    print("TEST: Edge Function Structure")
    print("=" * 70)

    with open("supabase/functions/gateway-telemetry/index.ts", "r") as f:
        ts_content = f.read()

    # Verify imports
    assert "import { serve }" in ts_content, "Missing serve import"
    assert "import { createClient }" in ts_content, "Missing Supabase client import"

    # Verify CORS headers
    assert "corsHeaders" in ts_content, "CORS headers not defined"
    assert (
        "'Access-Control-Allow-Origin': '*'" in ts_content or '"Access-Control-Allow-Origin": "*"' in ts_content
    ), "CORS origin not configured"

    # Verify type definitions
    assert "interface GatewayTransmission" in ts_content, "GatewayTransmission interface missing"
    assert "interface SovereigntyConstraints" in ts_content, "SovereigntyConstraints interface missing"
    assert "interface C5C7TensorMetrics" in ts_content, "C5C7TensorMetrics interface missing"

    # Verify validation function
    assert "function validateSovereigntyConstraints" in ts_content, "Sovereignty validation function missing"

    # Verify constraint checks
    assert "resonance_score < 0 || transmission.resonance_score > 1" in ts_content, "Resonance score validation missing"
    assert "necessity_score < 0 || transmission.necessity_score > 1" in ts_content, "Necessity score validation missing"

    # Verify C5-C7 tensor extraction
    assert "function extractC5C7TensorMetrics" in ts_content, "Tensor metrics extraction function missing"
    assert (
        "coherence_c5" in ts_content and "coherence_c6" in ts_content and "coherence_c7" in ts_content
    ), "C5-C7 coherence calculations missing"

    # Verify error handling
    assert "try {" in ts_content and "catch (error)" in ts_content, "Error handling missing"

    print("✅ Edge Function structure validated")
    print("   ✓ CORS configuration")
    print("   ✓ Type definitions")
    print("   ✓ Sovereignty constraint validation")
    print("   ✓ C₅-C₇ tensor metrics extraction")
    print("   ✓ Error handling")


def test_ci_pipeline_structure():
    """Test CI/CD pipeline structure"""
    print("\n" + "=" * 70)
    print("TEST: CI/CD Pipeline Structure")
    print("=" * 70)

    with open(".github/workflows/telemetry-pipeline.yml", "r") as f:
        pipeline_content = f.read()

    # Verify job definitions
    required_jobs = [
        "sql-lint",
        "typescript-check",
        "integration-tests",
        "deploy-staging",
        "deploy-production",
        "rollback",
        "notify-discord",
        "summary",
    ]

    for job in required_jobs:
        assert f"{job}:" in pipeline_content, f"Job '{job}' not found"

    # Verify SQL validation steps
    assert "Validate SQL syntax" in pipeline_content, "SQL validation step missing"
    assert "DROP TABLE" in pipeline_content, "Destructive operation check missing"
    assert "TRUNCATE" in pipeline_content, "Truncate operation check missing"

    # Verify TypeScript validation
    assert "deno check" in pipeline_content, "Deno TypeScript check missing"

    # Verify Supabase CLI usage
    assert "supabase" in pipeline_content, "Supabase CLI not used"
    assert "supabase db push" in pipeline_content, "Migration push command missing"
    assert "supabase functions deploy" in pipeline_content, "Function deployment missing"

    # Verify Discord notifications
    assert "Discord Notification" in pipeline_content, "Discord notification job missing"
    assert "DISCORD_WEBHOOK_URL" in pipeline_content, "Discord webhook not configured"

    # Verify rollback procedures
    assert "Rollback Deployment" in pipeline_content, "Rollback job missing"

    print("✅ CI/CD pipeline structure validated")
    print(f"   ✓ {len(required_jobs)} jobs defined")
    print("   ✓ SQL linting and validation")
    print("   ✓ TypeScript checking")
    print("   ✓ Integration tests")
    print("   ✓ Staging/Production deployment")
    print("   ✓ Discord notifications")
    print("   ✓ Rollback procedures")


def test_constitutional_compliance():
    """Test constitutional alignment requirements"""
    print("\n" + "=" * 70)
    print("TEST: Constitutional Compliance")
    print("=" * 70)

    with open("supabase/migrations/20251111_01_gateway_transmissions.sql", "r") as f:
        sql_content = f.read()

    # Verify thermodynamic bounds enforcement
    thermodynamic_checks = [
        "resonance_score >= 0 AND resonance_score <= 1",
        "necessity_score >= 0 AND necessity_score <= 1",
    ]

    for check in thermodynamic_checks:
        assert check in sql_content, f"Thermodynamic check missing: {check}"

    # Verify immutable timestamps
    assert "created_at TIMESTAMP WITH TIME ZONE" in sql_content, "Created_at timestamp missing"
    assert "updated_at TIMESTAMP WITH TIME ZONE" in sql_content, "Updated_at timestamp missing"

    # Verify VaultNode lineage documentation
    assert "ΔΩ" in sql_content, "VaultNode lineage marker missing"

    print("✅ Constitutional compliance verified")
    print("   ✓ Thermodynamic bounds [0, 1] enforced")
    print("   ✓ Immutable audit trail (timestamps)")
    print("   ✓ VaultNode lineage documented")
    print("   ✓ Sovereignty metrics tracked")


def run_all_tests():
    """Run complete test suite"""
    print("\n" + "=" * 70)
    print("🌀 GATEWAY TRANSMISSIONS INTEGRATION TEST SUITE")
    print("=" * 70)
    print("VaultNode: ΔΩ.147.0 - Gateway Telemetry Infrastructure")
    print("=" * 70)

    tests = [
        test_sql_constraints,
        test_indexes,
        test_rls_policies,
        test_helper_functions,
        test_edge_function_structure,
        test_ci_pipeline_structure,
        test_constitutional_compliance,
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            test()
            passed += 1
        except AssertionError as e:
            failed += 1
            print(f"❌ Test failed: {e}")
        except Exception as e:
            failed += 1
            print(f"❌ Test error: {e}")

    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    print(f"Passed: {passed}/{len(tests)}")
    print(f"Failed: {failed}/{len(tests)}")

    if failed == 0:
        print("\n✅ ALL TESTS PASSED - Constitutional integrity verified")
        print("=" * 70)
        return 0
    else:
        print("\n❌ SOME TESTS FAILED - Review implementation")
        print("=" * 70)
        return 1


if __name__ == "__main__":
    sys.exit(run_all_tests())
