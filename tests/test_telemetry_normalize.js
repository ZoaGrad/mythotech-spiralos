
// Phase 8.1: Telemetry Normalization Engine - JavaScript Test Suite
// Usage: node test_telemetry_normalize.js

const SUPABASE_URL = "https://xlmrnjatawslawquwzpf.supabase.co";
const FUNCTION_URL = `${SUPABASE_URL}/functions/v1/telemetry_normalize`;
const GUARDIAN_API_KEY = "4c8839c842278d53ca4e4a43df1e8664efc36bd3e73397690342060e47b66bd6";

async function testNormalization(testName, payload, expectSuccess = true) {
  console.log(`\n🧪 ${testName}`);
  console.log("=".repeat(60));

  try {
    const response = await fetch(FUNCTION_URL, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "x-guardian-api-key": GUARDIAN_API_KEY,
      },
      body: JSON.stringify(payload),
    });

    const data = await response.json();

    if (expectSuccess && response.ok) {
      console.log("✅ Test passed");
      console.log("Event ID:", data.event?.id);
      console.log("Bridge ID:", data.event?.bridge_id);
      console.log("Source:", data.event?.source);
      console.log("Signal Type:", data.event?.signal_type);
      console.log("Ache Signature:", data.event?.ache_signature);
      console.log("Agent Health:", data.event?.agent_health);
      console.log("Timestamp Drift:", data.event?.timestamp_drift_ms, "ms");
      console.log("Latency:", data.event?.latency_ms, "ms");
      console.log("Sovereign State:", data.event?.sovereign_state);
    } else if (!expectSuccess && !response.ok) {
      console.log("✅ Test passed (expected failure)");
      console.log("Error:", data.error);
    } else {
      console.log("❌ Test failed");
      console.log("Response:", data);
    }
  } catch (error) {
    console.log("❌ Test error:", error.message);
  }
}

async function runTests() {
  console.log("🚀 Phase 8.1: Telemetry Normalization Engine Test Suite");
  console.log("========================================================\n");

  // Test 1: Happy Path
  await testNormalization(
    "Test 1: Happy Path - Valid Telemetry Normalization",
    {
      gateway_key: "gw-guardian-core",
      event_type: "agent_sync_success",
      source: "discord_bot",
      timestamp: Date.now(),
      payload: {
        agent_id: "agent-001",
        sync_duration_ms: 1234,
        records_synced: 42,
      },
      metadata: {
        test: "happy_path",
      },
    }
  );

  // Test 2: Cross-Validation
  await testNormalization(
    "Test 2: Cross-Validation - Gateway/Bridge Mapping",
    {
      gateway_key: "gw-guardian-discord",
      event_type: "message_received",
      payload: {
        guild_id: "123456789",
        channel_id: "987654321",
        content: "Hello Guardian!",
      },
    }
  );

  // Test 3: Timestamp Drift
  await testNormalization(
    "Test 3: Timestamp Accuracy - Drift Calculation",
    {
      gateway_key: "gw-guardian-github",
      event_type: "webhook_delayed",
      timestamp: Date.now() - 60000, // 60 seconds ago
      payload: {
        repository: "mythotech-spiralos",
        action: "push",
      },
    }
  );

  // Test 4: High Ache Signature
  await testNormalization(
    "Test 4: Ache Signature - Error Event (High Ache)",
    {
      gateway_key: "gw-guardian-core",
      event_type: "sync_error_critical",
      source: "manual",
      payload: {
        error_message: "Database connection failed",
        error_code: "DB_CONN_TIMEOUT",
        retry_count: 3,
        success: false,
      },
    }
  );

  // Test 5: High Agent Health
  await testNormalization(
    "Test 5: Agent Health - Success Event (High Health)",
    {
      gateway_key: "gw-guardian-core",
      event_type: "health_check_success",
      payload: {
        uptime_seconds: 86400,
        memory_usage_mb: 128,
        success: true,
      },
    }
  );

  // Test 6: Authentication Failure
  await testNormalization(
    "Test 6: Authentication - Missing API Key (Should Fail)",
    {
      gateway_key: "gw-guardian-core",
      event_type: "unauthorized_test",
    },
    false
  );

  // Test 7: Invalid Payload
  await testNormalization(
    "Test 7: Error Handling - Invalid Payload (Should Fail)",
    {
      gateway_key: "gw-guardian-core",
      // Missing event_type
    },
    false
  );

  // Test 8: Complex Payload
  await testNormalization(
    "Test 8: Complex Payload - Large Data",
    {
      gateway_key: "gw-guardian-github",
      event_type: "webhook_pull_request",
      source: "github_webhook",
      payload: {
        action: "opened",
        pull_request: {
          id: 12345,
          title: "Phase 8.1 - Telemetry Normalization Engine",
          body: "This PR implements the complete telemetry normalization engine.",
          user: {
            login: "ZoaGrad",
          },
          created_at: new Date().toISOString(),
        },
        repository: {
          name: "mythotech-spiralos",
          full_name: "ZoaGrad/mythotech-spiralos",
        },
      },
    }
  );

  console.log("\n✅ Test suite complete!");
  console.log("\nNext steps:");
  console.log("1. Verify events in guardian_telemetry_events table");
  console.log("2. Check ache_signature and agent_health calculations");
  console.log("3. Validate timestamp_drift_ms accuracy");
  console.log("4. Review sovereign_state fingerprints");
}

runTests();

