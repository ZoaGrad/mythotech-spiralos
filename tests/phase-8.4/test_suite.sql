
-- Phase 8.4: Auto-Regulation Engine Test Suite - SQL Scripts
-- ============================================================================
-- These SQL scripts set up test data for the 12 test scenarios
-- Run these BEFORE executing the HTTP tests
-- ============================================================================

\echo 'Phase 8.4 Test Suite - SQL Setup'
\echo '================================='

-- Set test bridge ID
\set test_bridge_id 'f8f41ffa-6c2b-4a2a-a3be-32f0236668f4'

-- ============================================================================
-- CLEANUP: Remove existing test data
-- ============================================================================
\echo 'Cleaning up existing test data...'

DELETE FROM public.guardian_autoregulation_history 
WHERE bridge_id = :'test_bridge_id';

DELETE FROM public.guardian_anomalies 
WHERE bridge_id = :'test_bridge_id';

DELETE FROM public.guardian_correction_profiles 
WHERE bridge_id = :'test_bridge_id';

DELETE FROM public.guardian_scarindex_history 
WHERE bridge_id = :'test_bridge_id';

-- ============================================================================
-- TEST 1: ScarIndex Recovery - Low Value
-- ============================================================================
\echo 'Setting up Test 1: ScarIndex Recovery (Low Value)...'

-- Set low ScarIndex
INSERT INTO public.guardian_scarindex_current (bridge_id, scar_value, updated_at)
VALUES (:'test_bridge_id', 0.30, NOW())
ON CONFLICT (bridge_id) 
DO UPDATE SET scar_value = 0.30, updated_at = NOW();

-- Create anomaly
INSERT INTO public.guardian_anomalies (bridge_id, anomaly_type, severity, status, details)
VALUES (:'test_bridge_id', 'SCARINDEX_DROP', 'HIGH', 'ACTIVE', 
        '{"reason": "low_value", "current_scarindex": 0.30, "threshold": 0.40}'::jsonb);

\echo '✅ Test 1 setup complete'

-- ============================================================================
-- TEST 2: ScarIndex Recovery - Large Drop
-- ============================================================================
\echo 'Setting up Test 2: ScarIndex Recovery (Large Drop)...'

-- Create history showing drop
INSERT INTO public.guardian_scarindex_history (bridge_id, scar_value, delta, source, timestamp)
VALUES 
  (:'test_bridge_id', 0.80, 0, 'baseline', NOW() - INTERVAL '1 hour'),
  (:'test_bridge_id', 0.50, -0.30, 'drop_event', NOW() - INTERVAL '5 minutes');

-- Update current to dropped value
INSERT INTO public.guardian_scarindex_current (bridge_id, scar_value, updated_at)
VALUES (:'test_bridge_id', 0.50, NOW())
ON CONFLICT (bridge_id) 
DO UPDATE SET scar_value = 0.50, updated_at = NOW();

-- Create anomaly
INSERT INTO public.guardian_anomalies (bridge_id, anomaly_type, severity, status, details)
VALUES (:'test_bridge_id', 'SCARINDEX_DROP', 'CRITICAL', 'ACTIVE', 
        '{"reason": "large_drop", "current_scarindex": 0.50, "previous_scarindex": 0.80, "drop_percent": 37.5}'::jsonb);

\echo '✅ Test 2 setup complete'

-- ============================================================================
-- TEST 3: Sovereignty Stabilizer
-- ============================================================================
\echo 'Setting up Test 3: Sovereignty Stabilizer...'

-- Create multiple telemetry events with different sovereign states
DO $$
DECLARE
  i INTEGER;
  state_suffix TEXT;
BEGIN
  FOR i IN 1..6 LOOP
    state_suffix := 'state_' || i::TEXT;
    INSERT INTO public.guardian_telemetry_events (
      bridge_id, gateway_key, event_type, source, signal_type,
      timestamp_iso, timestamp_epoch, timestamp_drift_ms,
      payload, ache_signature, agent_health, sovereign_state
    )
    VALUES (
      :'test_bridge_id', 'gw-guardian-core', 'sovereignty_test', 'test_suite', 'test_signal',
      NOW() - (i * INTERVAL '8 minutes'), 
      EXTRACT(EPOCH FROM (NOW() - (i * INTERVAL '8 minutes')))::BIGINT * 1000,
      0, '{}'::jsonb, 0.5, 0.8, state_suffix
    );
  END LOOP;
END $$;

-- Create anomaly
INSERT INTO public.guardian_anomalies (bridge_id, anomaly_type, severity, status, details)
VALUES (:'test_bridge_id', 'SOVEREIGNTY_INSTABILITY', 'MEDIUM', 'ACTIVE', 
        '{"changes_per_hour": 5, "unique_states": 6, "threshold": 3}'::jsonb);

\echo '✅ Test 3 setup complete'

-- ============================================================================
-- TEST 4: Ache Buffer
-- ============================================================================
\echo 'Setting up Test 4: Ache Buffer...'

-- Create high ache telemetry events
INSERT INTO public.guardian_telemetry_events (
  bridge_id, gateway_key, event_type, source, signal_type,
  timestamp_iso, timestamp_epoch, timestamp_drift_ms,
  payload, ache_signature, agent_health
)
VALUES 
  (:'test_bridge_id', 'gw-guardian-core', 'ache_test_1', 'test_suite', 'error_signal',
   NOW() - INTERVAL '5 minutes', EXTRACT(EPOCH FROM (NOW() - INTERVAL '5 minutes'))::BIGINT * 1000,
   0, '{}'::jsonb, 0.85, 0.6),
  (:'test_bridge_id', 'gw-guardian-core', 'ache_test_2', 'test_suite', 'error_signal',
   NOW() - INTERVAL '2 minutes', EXTRACT(EPOCH FROM (NOW() - INTERVAL '2 minutes'))::BIGINT * 1000,
   0, '{}'::jsonb, 0.88, 0.55);

-- Create anomaly
INSERT INTO public.guardian_anomalies (bridge_id, anomaly_type, severity, status, details)
VALUES (:'test_bridge_id', 'ACHE_SPIKE', 'HIGH', 'ACTIVE', 
        '{"current_ache": 0.88, "previous_ache": 0.85, "threshold": 0.80}'::jsonb);

\echo '✅ Test 4 setup complete'

-- ============================================================================
-- TEST 5: Heartbeat Correction
-- ============================================================================
\echo 'Setting up Test 5: Heartbeat Correction...'

-- Remove recent telemetry to simulate heartbeat gap
-- (Already cleaned up above, just create the anomaly)

INSERT INTO public.guardian_anomalies (bridge_id, anomaly_type, severity, status, details)
VALUES (:'test_bridge_id', 'HEARTBEAT_GAP', 'HIGH', 'ACTIVE', 
        '{"gap_minutes": 15, "threshold_minutes": 10, "last_telemetry": null}'::jsonb);

\echo '✅ Test 5 setup complete'

-- ============================================================================
-- TEST 6: Entropy Correction
-- ============================================================================
\echo 'Setting up Test 6: Entropy Correction...'

-- Create diverse event patterns for entropy
DO $$
DECLARE
  i INTEGER;
BEGIN
  FOR i IN 1..15 LOOP
    INSERT INTO public.guardian_telemetry_events (
      bridge_id, gateway_key, event_type, source, signal_type,
      timestamp_iso, timestamp_epoch, timestamp_drift_ms,
      payload, ache_signature, agent_health
    )
    VALUES (
      :'test_bridge_id', 'gw-guardian-core', 
      'entropy_event_' || i::TEXT, 
      CASE WHEN i % 3 = 0 THEN 'discord_bot' WHEN i % 3 = 1 THEN 'github_webhook' ELSE 'manual' END,
      'generic_signal',
      NOW() - (i * INTERVAL '2 minutes'),
      EXTRACT(EPOCH FROM (NOW() - (i * INTERVAL '2 minutes')))::BIGINT * 1000,
      0, '{}'::jsonb, 0.5, 0.7
    );
  END LOOP;
END $$;

-- Create anomaly
INSERT INTO public.guardian_anomalies (bridge_id, anomaly_type, severity, status, details)
VALUES (:'test_bridge_id', 'ENTROPY_SPIKE', 'HIGH', 'ACTIVE', 
        '{"entropy": 0.18, "threshold": 0.15, "unique_patterns": 15}'::jsonb);

\echo '✅ Test 6 setup complete'

-- ============================================================================
-- TEST 7: Self-Preservation Freeze Mode
-- ============================================================================
\echo 'Setting up Test 7: Self-Preservation Freeze Mode...'

-- Create CRITICAL anomaly
INSERT INTO public.guardian_anomalies (bridge_id, anomaly_type, severity, status, details)
VALUES (:'test_bridge_id', 'SCARINDEX_DROP', 'CRITICAL', 'ACTIVE', 
        '{"reason": "catastrophic_failure", "current_scarindex": 0.15, "threshold": 0.40}'::jsonb);

\echo '✅ Test 7 setup complete'

-- ============================================================================
-- TEST 9: Mixed Anomaly Batch
-- ============================================================================
\echo 'Setting up Test 9: Mixed Anomaly Batch...'

INSERT INTO public.guardian_anomalies (bridge_id, anomaly_type, severity, status, details)
VALUES 
  (:'test_bridge_id', 'ACHE_SPIKE', 'HIGH', 'ACTIVE', '{"ache": 0.85}'::jsonb),
  (:'test_bridge_id', 'HEARTBEAT_GAP', 'MEDIUM', 'ACTIVE', '{"gap_minutes": 12}'::jsonb),
  (:'test_bridge_id', 'ENTROPY_SPIKE', 'LOW', 'ACTIVE', '{"entropy": 0.16}'::jsonb);

\echo '✅ Test 9 setup complete'

-- ============================================================================
-- TEST 11: Performance Test Setup (50 anomalies)
-- ============================================================================
\echo 'Setting up Test 11: Performance Test (50 anomalies)...'

DO $$
DECLARE
  i INTEGER;
  anomaly_types TEXT[] := ARRAY['HEARTBEAT_GAP', 'ACHE_SPIKE', 'SCARINDEX_DROP', 'SOVEREIGNTY_INSTABILITY', 'ENTROPY_SPIKE'];
  severities TEXT[] := ARRAY['LOW', 'MEDIUM', 'HIGH', 'CRITICAL'];
BEGIN
  FOR i IN 1..50 LOOP
    INSERT INTO public.guardian_anomalies (bridge_id, anomaly_type, severity, status, details)
    VALUES (
      :'test_bridge_id',
      anomaly_types[(i % 5) + 1],
      severities[(i % 4) + 1],
      'ACTIVE',
      jsonb_build_object('test_id', i, 'performance_test', true)
    );
  END LOOP;
END $$;

\echo '✅ Test 11 setup complete (50 anomalies created)'

-- ============================================================================
-- VERIFICATION QUERIES
-- ============================================================================
\echo ''
\echo 'Test Setup Summary'
\echo '=================='

SELECT 
  anomaly_type,
  severity,
  COUNT(*) as count
FROM public.guardian_anomalies
WHERE bridge_id = :'test_bridge_id'
  AND status = 'ACTIVE'
GROUP BY anomaly_type, severity
ORDER BY anomaly_type, severity;

\echo ''
\echo '✅ All test data setup complete!'
\echo 'You can now run the HTTP tests in test_suite.http'

