
#!/bin/bash
# Phase 8.1: Telemetry Normalization Engine Test Suite

set -e

SUPABASE_URL="https://xlmrnjatawslawquwzpf.supabase.co"
FUNCTION_URL="${SUPABASE_URL}/functions/v1/telemetry_normalize"
GUARDIAN_API_KEY="4c8839c842278d53ca4e4a43df1e8664efc36bd3e73397690342060e47b66bd6"

echo "🧪 Phase 8.1: Telemetry Normalization Engine Test Suite"
echo "========================================================"
echo ""

# Test 1: Happy Path - Valid Telemetry Normalization
echo "Test 1: Happy Path - Valid Telemetry Normalization"
echo "---------------------------------------------------"
curl -X POST "$FUNCTION_URL" \
  -H "Content-Type: application/json" \
  -H "x-guardian-api-key: $GUARDIAN_API_KEY" \
  -d '{
    "gateway_key": "gw-guardian-core",
    "event_type": "agent_sync_success",
    "source": "discord_bot",
    "timestamp": "'$(date -u +%s000)'",
    "payload": {
      "agent_id": "agent-001",
      "sync_duration_ms": 1234,
      "records_synced": 42
    },
    "metadata": {
      "test": "happy_path"
    }
  }'
echo -e "\n"

# Test 2: Cross-Validation - Gateway/Bridge Mapping
echo "Test 2: Cross-Validation - Gateway/Bridge Mapping"
echo "--------------------------------------------------"
curl -X POST "$FUNCTION_URL" \
  -H "Content-Type: application/json" \
  -H "x-guardian-api-key: $GUARDIAN_API_KEY" \
  -d '{
    "gateway_key": "gw-guardian-discord",
    "event_type": "message_received",
    "payload": {
      "guild_id": "123456789",
      "channel_id": "987654321",
      "content": "Hello Guardian!"
    }
  }'
echo -e "\n"

# Test 3: Timestamp Accuracy - Drift Calculation
echo "Test 3: Timestamp Accuracy - Drift Calculation"
echo "-----------------------------------------------"
PAST_TIMESTAMP=$(($(date -u +%s) - 60))000  # 60 seconds ago
curl -X POST "$FUNCTION_URL" \
  -H "Content-Type: application/json" \
  -H "x-guardian-api-key: $GUARDIAN_API_KEY" \
  -d '{
    "gateway_key": "gw-guardian-github",
    "event_type": "webhook_delayed",
    "timestamp": '$PAST_TIMESTAMP',
    "payload": {
      "repository": "mythotech-spiralos",
      "action": "push"
    }
  }'
echo -e "\n"

# Test 4: Ache Signature - Error Event
echo "Test 4: Ache Signature - Error Event (High Ache)"
echo "--------------------------------------------------"
curl -X POST "$FUNCTION_URL" \
  -H "Content-Type: application/json" \
  -H "x-guardian-api-key: $GUARDIAN_API_KEY" \
  -d '{
    "gateway_key": "gw-guardian-core",
    "event_type": "sync_error_critical",
    "source": "manual",
    "payload": {
      "error_message": "Database connection failed",
      "error_code": "DB_CONN_TIMEOUT",
      "retry_count": 3,
      "success": false
    }
  }'
echo -e "\n"

# Test 5: Agent Health - Success Event
echo "Test 5: Agent Health - Success Event (High Health)"
echo "---------------------------------------------------"
curl -X POST "$FUNCTION_URL" \
  -H "Content-Type: application/json" \
  -H "x-guardian-api-key: $GUARDIAN_API_KEY" \
  -d '{
    "gateway_key": "gw-guardian-core",
    "event_type": "health_check_success",
    "payload": {
      "uptime_seconds": 86400,
      "memory_usage_mb": 128,
      "success": true
    }
  }'
echo -e "\n"

# Test 6: Authentication - Missing API Key
echo "Test 6: Authentication - Missing API Key (Should Fail)"
echo "-------------------------------------------------------"
curl -X POST "$FUNCTION_URL" \
  -H "Content-Type: application/json" \
  -d '{
    "gateway_key": "gw-guardian-core",
    "event_type": "unauthorized_test"
  }'
echo -e "\n"

# Test 7: Error Handling - Invalid Payload
echo "Test 7: Error Handling - Invalid Payload (Should Fail)"
echo "-------------------------------------------------------"
curl -X POST "$FUNCTION_URL" \
  -H "Content-Type: application/json" \
  -H "x-guardian-api-key: $GUARDIAN_API_KEY" \
  -d '{
    "gateway_key": "gw-guardian-core"
  }'
echo -e "\n"

# Test 8: Complex Payload - Large Data
echo "Test 8: Complex Payload - Large Data"
echo "-------------------------------------"
curl -X POST "$FUNCTION_URL" \
  -H "Content-Type: application/json" \
  -H "x-guardian-api-key: $GUARDIAN_API_KEY" \
  -d '{
    "gateway_key": "gw-guardian-github",
    "event_type": "webhook_pull_request",
    "source": "github_webhook",
    "payload": {
      "action": "opened",
      "pull_request": {
        "id": 12345,
        "title": "Phase 8.1 - Telemetry Normalization Engine",
        "body": "This PR implements the complete telemetry normalization engine with canonical timestamping, ache signatures, and agent health estimation.",
        "user": {
          "login": "ZoaGrad"
        },
        "created_at": "'$(date -u +%Y-%m-%dT%H:%M:%SZ)'"
      },
      "repository": {
        "name": "mythotech-spiralos",
        "full_name": "ZoaGrad/mythotech-spiralos"
      }
    }
  }'
echo -e "\n"

echo "✅ Test suite complete!"
echo ""
echo "Next steps:"
echo "1. Verify events in guardian_telemetry_events table"
echo "2. Check ache_signature and agent_health calculations"
echo "3. Validate timestamp_drift_ms accuracy"
echo "4. Review sovereign_state fingerprints"

