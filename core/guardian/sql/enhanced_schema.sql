-- SpiralOS Guardian - Enhanced Database Schema
-- This file contains Guardian-specific tables, views, and functions

-- ============================================================================
-- GUARDIAN TABLES
-- ============================================================================

-- Guardian heartbeat log
CREATE TABLE IF NOT EXISTS guardian_heartbeats (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  scar_score FLOAT,
  scar_status TEXT,
  metrics JSONB,
  coherence_components JSONB,
  pid_state JSONB,
  discord_message_id TEXT,
  window_hours INT DEFAULT 24,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_guardian_heartbeats_timestamp ON guardian_heartbeats(timestamp DESC);

-- Enhanced guardian alerts
CREATE TABLE IF NOT EXISTS guardian_alerts (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  alert_type TEXT NOT NULL, -- 'panic', 'coherence', 'pid', 'vault', 'trend'
  severity TEXT NOT NULL, -- 'info', 'warning', 'critical'
  message TEXT NOT NULL,
  metadata JSONB,
  resolved BOOLEAN DEFAULT FALSE,
  resolved_at TIMESTAMPTZ,
  resolved_by TEXT,
  discord_message_id TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_guardian_alerts_type ON guardian_alerts(alert_type);
CREATE INDEX idx_guardian_alerts_severity ON guardian_alerts(severity);
CREATE INDEX idx_guardian_alerts_created ON guardian_alerts(created_at DESC);
CREATE INDEX idx_guardian_alerts_resolved ON guardian_alerts(resolved) WHERE NOT resolved;

-- Guardian commands log
CREATE TABLE IF NOT EXISTS guardian_commands (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  command TEXT NOT NULL,
  user_id TEXT,
  username TEXT,
  channel_id TEXT,
  guild_id TEXT,
  response JSONB,
  execution_time_ms INT,
  success BOOLEAN DEFAULT TRUE,
  error_message TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_guardian_commands_created ON guardian_commands(created_at DESC);
CREATE INDEX idx_guardian_commands_command ON guardian_commands(command);

-- Coherence trend analysis
CREATE TABLE IF NOT EXISTS coherence_trends (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  analysis_window_hours INT NOT NULL,
  trend_direction TEXT NOT NULL, -- 'improving', 'stable', 'degrading'
  slope FLOAT,
  r_squared FLOAT,
  current_value FLOAT,
  avg_value FLOAT,
  min_value FLOAT,
  max_value FLOAT,
  data_points INT,
  metadata JSONB,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_coherence_trends_created ON coherence_trends(created_at DESC);

-- ============================================================================
-- ENHANCED VIEWS
-- ============================================================================

-- Guardian dashboard view
CREATE OR REPLACE VIEW guardian_dashboard AS
SELECT 
  (SELECT COUNT(*) FROM vault_nodes) as total_vaultnodes,
  (SELECT COUNT(*) FROM ache_events WHERE created_at > NOW() - INTERVAL '24 hours') as ache_events_24h,
  (SELECT AVG(value) FROM scarindex_calculations WHERE created_at > NOW() - INTERVAL '24 hours') as scarindex_avg_24h,
  (SELECT value FROM scarindex_calculations ORDER BY created_at DESC LIMIT 1) as scarindex_latest,
  (SELECT COUNT(*) FROM panic_frames WHERE status = 'ACTIVE') as active_panic_frames,
  (SELECT COUNT(*) FROM guardian_alerts WHERE created_at > NOW() - INTERVAL '24 hours' AND NOT resolved) as unresolved_alerts_24h,
  (SELECT trend_direction FROM coherence_trends ORDER BY created_at DESC LIMIT 1) as latest_trend,
  NOW() as snapshot_time;

-- Recent activity view
CREATE OR REPLACE VIEW guardian_recent_activity AS
SELECT 
  'ache_event' as activity_type,
  id::TEXT as activity_id,
  ache_level as value,
  created_at
FROM ache_events
WHERE created_at > NOW() - INTERVAL '24 hours'
UNION ALL
SELECT 
  'scarindex_calc' as activity_type,
  id::TEXT as activity_id,
  value as value,
  created_at
FROM scarindex_calculations
WHERE created_at > NOW() - INTERVAL '24 hours'
UNION ALL
SELECT 
  'vault_seal' as activity_type,
  id::TEXT as activity_id,
  NULL as value,
  created_at
FROM vault_nodes
WHERE created_at > NOW() - INTERVAL '24 hours'
ORDER BY created_at DESC;

-- Alert summary view
CREATE OR REPLACE VIEW guardian_alert_summary AS
SELECT 
  alert_type,
  severity,
  COUNT(*) as count,
  COUNT(*) FILTER (WHERE NOT resolved) as unresolved_count,
  MAX(created_at) as last_occurrence
FROM guardian_alerts
WHERE created_at > NOW() - INTERVAL '7 days'
GROUP BY alert_type, severity
ORDER BY severity DESC, count DESC;

-- Coherence component history
CREATE OR REPLACE VIEW coherence_component_history AS
SELECT 
  created_at,
  c_narrative,
  c_social,
  c_economic,
  c_technical,
  value as scarindex,
  (c_narrative * 0.30 + c_social * 0.25 + c_economic * 0.25 + c_technical * 0.20) as calculated_base
FROM scarindex_calculations
WHERE created_at > NOW() - INTERVAL '7 days'
ORDER BY created_at DESC;

-- ============================================================================
-- ENHANCED FUNCTIONS
-- ============================================================================

-- Function to get comprehensive Guardian status
CREATE OR REPLACE FUNCTION get_guardian_status(lookback_hours INT DEFAULT 24)
RETURNS JSON AS $$
DECLARE
  result JSON;
BEGIN
  SELECT json_build_object(
    'timestamp', NOW(),
    'window_hours', lookback_hours,
    'metrics', (
      SELECT json_build_object(
        'vault_nodes', (SELECT COUNT(*) FROM vault_nodes),
        'ache_events', (SELECT COUNT(*) FROM ache_events WHERE created_at > NOW() - (lookback_hours || ' hours')::INTERVAL),
        'scarindex_avg', (SELECT AVG(value) FROM scarindex_calculations WHERE created_at > NOW() - (lookback_hours || ' hours')::INTERVAL),
        'scarindex_latest', (SELECT value FROM scarindex_calculations ORDER BY created_at DESC LIMIT 1),
        'alerts_24h', (SELECT COUNT(*) FROM guardian_alerts WHERE created_at > NOW() - INTERVAL '24 hours'),
        'active_panic_frames', (SELECT COUNT(*) FROM panic_frames WHERE status = 'ACTIVE')
      )
    ),
    'coherence_components', (
      SELECT json_build_object(
        'narrative', c_narrative,
        'social', c_social,
        'economic', c_economic,
        'technical', c_technical
      )
      FROM scarindex_calculations
      ORDER BY created_at DESC
      LIMIT 1
    ),
    'pid_state', (
      SELECT json_build_object(
        'current_scarindex', current_scarindex,
        'target_scarindex', target_scarindex,
        'error', error,
        'integral', integral,
        'derivative', derivative,
        'guidance_scale', guidance_scale
      )
      FROM pid_controller_state
      ORDER BY created_at DESC
      LIMIT 1
    ),
    'scar_status', (
      SELECT CASE
        WHEN value >= 1.4 THEN '🟠'
        WHEN value >= 0.6 THEN '🟢'
        ELSE '🔴'
      END
      FROM scarindex_calculations
      ORDER BY created_at DESC
      LIMIT 1
    ),
    'scar_score', (
      SELECT value
      FROM scarindex_calculations
      ORDER BY created_at DESC
      LIMIT 1
    )
  ) INTO result;
  
  RETURN result;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to log Guardian heartbeat
CREATE OR REPLACE FUNCTION log_guardian_heartbeat(
  p_scar_score FLOAT,
  p_scar_status TEXT,
  p_metrics JSONB,
  p_coherence_components JSONB DEFAULT NULL,
  p_pid_state JSONB DEFAULT NULL,
  p_discord_message_id TEXT DEFAULT NULL,
  p_window_hours INT DEFAULT 24
)
RETURNS UUID AS $$
DECLARE
  heartbeat_id UUID;
BEGIN
  INSERT INTO guardian_heartbeats (
    scar_score,
    scar_status,
    metrics,
    coherence_components,
    pid_state,
    discord_message_id,
    window_hours
  ) VALUES (
    p_scar_score,
    p_scar_status,
    p_metrics,
    p_coherence_components,
    p_pid_state,
    p_discord_message_id,
    p_window_hours
  )
  RETURNING id INTO heartbeat_id;
  
  RETURN heartbeat_id;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to create Guardian alert
CREATE OR REPLACE FUNCTION create_guardian_alert(
  p_alert_type TEXT,
  p_severity TEXT,
  p_message TEXT,
  p_metadata JSONB DEFAULT NULL,
  p_discord_message_id TEXT DEFAULT NULL
)
RETURNS UUID AS $$
DECLARE
  alert_id UUID;
BEGIN
  INSERT INTO guardian_alerts (
    alert_type,
    severity,
    message,
    metadata,
    discord_message_id
  ) VALUES (
    p_alert_type,
    p_severity,
    p_message,
    p_metadata,
    p_discord_message_id
  )
  RETURNING id INTO alert_id;
  
  RETURN alert_id;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to resolve Guardian alert
CREATE OR REPLACE FUNCTION resolve_guardian_alert(
  p_alert_id UUID,
  p_resolved_by TEXT DEFAULT NULL
)
RETURNS BOOLEAN AS $$
BEGIN
  UPDATE guardian_alerts
  SET 
    resolved = TRUE,
    resolved_at = NOW(),
    resolved_by = p_resolved_by
  WHERE id = p_alert_id;
  
  RETURN FOUND;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to analyze coherence trend
CREATE OR REPLACE FUNCTION analyze_coherence_trend(
  p_window_hours INT DEFAULT 24
)
RETURNS JSON AS $$
DECLARE
  result JSON;
  data_count INT;
  trend_slope FLOAT;
  trend_direction TEXT;
BEGIN
  -- Get data points
  SELECT COUNT(*) INTO data_count
  FROM scarindex_calculations
  WHERE created_at > NOW() - (p_window_hours || ' hours')::INTERVAL;
  
  IF data_count < 5 THEN
    RETURN json_build_object(
      'status', 'insufficient_data',
      'data_points', data_count,
      'message', 'Need at least 5 data points for trend analysis'
    );
  END IF;
  
  -- Calculate linear regression slope using PostgreSQL
  WITH numbered_data AS (
    SELECT 
      value,
      ROW_NUMBER() OVER (ORDER BY created_at) as x,
      created_at
    FROM scarindex_calculations
    WHERE created_at > NOW() - (p_window_hours || ' hours')::INTERVAL
  ),
  stats AS (
    SELECT
      COUNT(*) as n,
      AVG(x) as x_avg,
      AVG(value) as y_avg,
      SUM((x - (SELECT AVG(x) FROM numbered_data)) * (value - (SELECT AVG(value) FROM numbered_data))) as numerator,
      SUM(POWER(x - (SELECT AVG(x) FROM numbered_data), 2)) as denominator
    FROM numbered_data
  )
  SELECT 
    CASE 
      WHEN denominator = 0 THEN 0
      ELSE numerator / denominator
    END INTO trend_slope
  FROM stats;
  
  -- Determine trend direction
  IF trend_slope > 0.01 THEN
    trend_direction := 'improving';
  ELSIF trend_slope < -0.01 THEN
    trend_direction := 'degrading';
  ELSE
    trend_direction := 'stable';
  END IF;
  
  -- Build result
  SELECT json_build_object(
    'status', 'success',
    'window_hours', p_window_hours,
    'data_points', data_count,
    'trend_direction', trend_direction,
    'slope', trend_slope,
    'current_value', (SELECT value FROM scarindex_calculations ORDER BY created_at DESC LIMIT 1),
    'avg_value', (SELECT AVG(value) FROM scarindex_calculations WHERE created_at > NOW() - (p_window_hours || ' hours')::INTERVAL),
    'min_value', (SELECT MIN(value) FROM scarindex_calculations WHERE created_at > NOW() - (p_window_hours || ' hours')::INTERVAL),
    'max_value', (SELECT MAX(value) FROM scarindex_calculations WHERE created_at > NOW() - (p_window_hours || ' hours')::INTERVAL)
  ) INTO result;
  
  -- Log the trend analysis
  INSERT INTO coherence_trends (
    analysis_window_hours,
    trend_direction,
    slope,
    current_value,
    avg_value,
    min_value,
    max_value,
    data_points,
    metadata
  ) VALUES (
    p_window_hours,
    trend_direction,
    trend_slope,
    (result->>'current_value')::FLOAT,
    (result->>'avg_value')::FLOAT,
    (result->>'min_value')::FLOAT,
    (result->>'max_value')::FLOAT,
    data_count,
    result
  );
  
  RETURN result;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- ============================================================================
-- TRIGGERS
-- ============================================================================

-- Trigger to auto-create alert when Panic Frame is activated
CREATE OR REPLACE FUNCTION auto_alert_panic_frame()
RETURNS TRIGGER AS $$
BEGIN
  IF NEW.status = 'ACTIVE' THEN
    PERFORM create_guardian_alert(
      'panic',
      'critical',
      format('Panic Frame activated - ScarIndex: %s (threshold: 0.30)', NEW.scarindex_value),
      json_build_object(
        'panic_frame_id', NEW.id,
        'scarindex_value', NEW.scarindex_value,
        'recovery_phase', NEW.recovery_phase
      )
    );
  END IF;
  
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_auto_alert_panic_frame
  AFTER INSERT ON panic_frames
  FOR EACH ROW
  EXECUTE FUNCTION auto_alert_panic_frame();

-- Trigger to auto-create alert for out-of-band ScarIndex
CREATE OR REPLACE FUNCTION auto_alert_scarindex_oob()
RETURNS TRIGGER AS $$
BEGIN
  IF NEW.value < 0.6 OR NEW.value >= 1.4 THEN
    PERFORM create_guardian_alert(
      'coherence',
      CASE 
        WHEN NEW.value < 0.3 THEN 'critical'
        WHEN NEW.value < 0.6 OR NEW.value >= 1.4 THEN 'warning'
        ELSE 'info'
      END,
      format('ScarIndex out of band: %s (healthy range: 0.6-1.4)', NEW.value),
      json_build_object(
        'scarindex_id', NEW.id,
        'scarindex_value', NEW.value,
        'c_narrative', NEW.c_narrative,
        'c_social', NEW.c_social,
        'c_economic', NEW.c_economic,
        'c_technical', NEW.c_technical
      )
    );
  END IF;
  
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_auto_alert_scarindex_oob
  AFTER INSERT ON scarindex_calculations
  FOR EACH ROW
  EXECUTE FUNCTION auto_alert_scarindex_oob();

-- ============================================================================
-- ROW LEVEL SECURITY (RLS)
-- ============================================================================

-- Enable RLS on Guardian tables
ALTER TABLE guardian_heartbeats ENABLE ROW LEVEL SECURITY;
ALTER TABLE guardian_alerts ENABLE ROW LEVEL SECURITY;
ALTER TABLE guardian_commands ENABLE ROW LEVEL SECURITY;
ALTER TABLE coherence_trends ENABLE ROW LEVEL SECURITY;

-- Allow service role full access
CREATE POLICY "Service role full access" ON guardian_heartbeats
  FOR ALL USING (auth.role() = 'service_role');

CREATE POLICY "Service role full access" ON guardian_alerts
  FOR ALL USING (auth.role() = 'service_role');

CREATE POLICY "Service role full access" ON guardian_commands
  FOR ALL USING (auth.role() = 'service_role');

CREATE POLICY "Service role full access" ON coherence_trends
  FOR ALL USING (auth.role() = 'service_role');

-- Allow anon read access to dashboard data
CREATE POLICY "Public read access" ON guardian_heartbeats
  FOR SELECT USING (true);

CREATE POLICY "Public read access" ON guardian_alerts
  FOR SELECT USING (true);

CREATE POLICY "Public read access" ON coherence_trends
  FOR SELECT USING (true);

-- ============================================================================
-- GRANTS
-- ============================================================================

-- Grant execute permissions on functions
GRANT EXECUTE ON FUNCTION get_guardian_status(INT) TO anon, authenticated, service_role;
GRANT EXECUTE ON FUNCTION log_guardian_heartbeat(FLOAT, TEXT, JSONB, JSONB, JSONB, TEXT, INT) TO service_role;
GRANT EXECUTE ON FUNCTION create_guardian_alert(TEXT, TEXT, TEXT, JSONB, TEXT) TO service_role;
GRANT EXECUTE ON FUNCTION resolve_guardian_alert(UUID, TEXT) TO service_role;
GRANT EXECUTE ON FUNCTION analyze_coherence_trend(INT) TO anon, authenticated, service_role;

-- ============================================================================
-- INDEXES FOR PERFORMANCE
-- ============================================================================

-- Additional indexes for common queries
CREATE INDEX IF NOT EXISTS idx_scarindex_calc_created ON scarindex_calculations(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_scarindex_calc_value ON scarindex_calculations(value);
CREATE INDEX IF NOT EXISTS idx_ache_events_created ON ache_events(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_vault_nodes_created ON vault_nodes(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_panic_frames_status ON panic_frames(status) WHERE status = 'ACTIVE';

-- ============================================================================
-- COMMENTS
-- ============================================================================

COMMENT ON TABLE guardian_heartbeats IS 'Log of all Guardian heartbeat checks';
COMMENT ON TABLE guardian_alerts IS 'System alerts generated by Guardian monitoring';
COMMENT ON TABLE guardian_commands IS 'Log of all Discord bot commands executed';
COMMENT ON TABLE coherence_trends IS 'Historical trend analysis of system coherence';

COMMENT ON FUNCTION get_guardian_status(INT) IS 'Get comprehensive Guardian system status';
COMMENT ON FUNCTION log_guardian_heartbeat(FLOAT, TEXT, JSONB, JSONB, JSONB, TEXT, INT) IS 'Log a Guardian heartbeat event';
COMMENT ON FUNCTION create_guardian_alert(TEXT, TEXT, TEXT, JSONB, TEXT) IS 'Create a new Guardian alert';
COMMENT ON FUNCTION resolve_guardian_alert(UUID, TEXT) IS 'Mark a Guardian alert as resolved';
COMMENT ON FUNCTION analyze_coherence_trend(INT) IS 'Analyze ScarIndex trend over specified time window';
