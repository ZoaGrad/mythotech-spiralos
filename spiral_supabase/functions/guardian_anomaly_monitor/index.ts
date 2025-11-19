
// supabase/functions/guardian_anomaly_monitor/index.ts
// Phase 8.3: Guardian Anomaly Detection Circuit
// Detects 5 types of anomalies and triggers auto-regulation for HIGH/CRITICAL

import { serve } from "https://deno.land/std@0.224.0/http/server.ts";
import { createClient } from "jsr:@supabase/supabase-js@2";

// ============================================================================
// TYPES
// ============================================================================
type AnomalyDetectionRequest = {
  bridge_id?: string;
  scan_all?: boolean;
};

type DetectedAnomaly = {
  bridge_id: string;
  anomaly_type: string;
  severity: string;
  details: Record<string, unknown>;
};

// ============================================================================
// ENVIRONMENT
// ============================================================================
const SUPABASE_URL = Deno.env.get("SUPABASE_URL")!;
const SERVICE_ROLE_KEY = Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!;
const GUARDIAN_API_KEY = Deno.env.get("GUARDIAN_API_KEY") ?? "";
const DISCORD_GUARDIAN_WEBHOOK_URL = Deno.env.get("DISCORD_GUARDIAN_WEBHOOK_URL") ?? "";

const supabase = createClient(SUPABASE_URL, SERVICE_ROLE_KEY);

const corsHeaders = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Methods": "POST, OPTIONS",
  "Access-Control-Allow-Headers":
    "authorization, x-guardian-api-key, content-type",
};

// Deduplication window: 60 minutes
const DEDUPLICATION_WINDOW_MS = 60 * 60 * 1000;

// ============================================================================
// THRESHOLDS (from Phase 8.3 spec)
// ============================================================================
const THRESHOLDS = {
  HEARTBEAT_GAP_MINUTES: 10,
  ACHE_HIGH: 0.80,
  ACHE_DELTA: 0.25,
  SCARINDEX_LOW: 0.40,
  SCARINDEX_DROP_PERCENT: 20,
  SOVEREIGNTY_CHANGES_PER_HOUR: 3,
  ENTROPY_HIGH: 0.15,
};

// ============================================================================
// UTILITIES
// ============================================================================
function jsonResponse(body: unknown, status = 200): Response {
  return new Response(JSON.stringify(body, null, 2), {
    status,
    headers: {
      "Content-Type": "application/json",
      ...corsHeaders,
    },
  });
}

// ============================================================================
// DISCORD NOTIFICATION
// ============================================================================
async function notifyDiscord(
  message: string,
  embeds?: Array<Record<string, unknown>>,
): Promise<void> {
  if (!DISCORD_GUARDIAN_WEBHOOK_URL) {
    console.warn("⚠️ Discord webhook URL not configured");
    return;
  }

  try {
    const payload: Record<string, unknown> = { content: message };
    if (embeds && embeds.length > 0) {
      payload.embeds = embeds;
    }

    const response = await fetch(DISCORD_GUARDIAN_WEBHOOK_URL, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });

    if (!response.ok) {
      console.error("❌ Discord notification failed:", response.status);
    }
  } catch (error) {
    console.error("❌ Discord notification error:", error);
  }
}

// ============================================================================
// DEDUPLICATION CHECK
// ============================================================================
async function isDuplicateAnomaly(
  bridge_id: string,
  anomaly_type: string,
): Promise<boolean> {
  const windowStart = new Date(Date.now() - DEDUPLICATION_WINDOW_MS);

  const { data, error } = await supabase
    .from("guardian_anomalies")
    .select("id")
    .eq("bridge_id", bridge_id)
    .eq("anomaly_type", anomaly_type)
    .eq("status", "ACTIVE")
    .gte("detected_at", windowStart.toISOString())
    .limit(1)
    .maybeSingle();

  if (error) {
    console.error("❌ Error checking duplicate:", error);
    return false;
  }

  return data !== null;
}

// ============================================================================
// ANOMALY INSERTION
// ============================================================================
async function insertAnomaly(
  anomaly: DetectedAnomaly,
): Promise<string | null> {
  // Check deduplication
  const isDuplicate = await isDuplicateAnomaly(
    anomaly.bridge_id,
    anomaly.anomaly_type,
  );

  if (isDuplicate) {
    console.log(`⏭️ Skipping duplicate anomaly: ${anomaly.anomaly_type} for ${anomaly.bridge_id}`);
    return null;
  }

  const { data, error } = await supabase
    .from("guardian_anomalies")
    .insert({
      bridge_id: anomaly.bridge_id,
      anomaly_type: anomaly.anomaly_type,
      severity: anomaly.severity,
      status: "ACTIVE",
      details: anomaly.details,
      detected_at: new Date().toISOString(),
    })
    .select("id")
    .single();

  if (error) {
    console.error("❌ Error inserting anomaly:", error);
    return null;
  }

  console.log(`✅ Anomaly inserted: ${data.id}`);
  return data.id;
}

// ============================================================================
// ANOMALY DETECTION: HEARTBEAT GAP
// ============================================================================
async function detectHeartbeatGap(bridge_id: string): Promise<DetectedAnomaly | null> {
  const thresholdTime = new Date(Date.now() - THRESHOLDS.HEARTBEAT_GAP_MINUTES * 60 * 1000);

  const { data, error } = await supabase
    .from("guardian_telemetry_events")
    .select("timestamp_iso")
    .eq("bridge_id", bridge_id)
    .order("timestamp_iso", { ascending: false })
    .limit(1)
    .maybeSingle();

  if (error) {
    console.error("❌ Error checking heartbeat:", error);
    return null;
  }

  if (!data) {
    // No telemetry at all
    return {
      bridge_id,
      anomaly_type: "HEARTBEAT_GAP",
      severity: "CRITICAL",
      details: {
        reason: "No telemetry events found",
        threshold_minutes: THRESHOLDS.HEARTBEAT_GAP_MINUTES,
      },
    };
  }

  const lastTimestamp = new Date(data.timestamp_iso);
  const gapMinutes = (Date.now() - lastTimestamp.getTime()) / (1000 * 60);

  if (gapMinutes > THRESHOLDS.HEARTBEAT_GAP_MINUTES) {
    return {
      bridge_id,
      anomaly_type: "HEARTBEAT_GAP",
      severity: gapMinutes > 30 ? "CRITICAL" : "HIGH",
      details: {
        last_telemetry: data.timestamp_iso,
        gap_minutes: Math.round(gapMinutes * 10) / 10,
        threshold_minutes: THRESHOLDS.HEARTBEAT_GAP_MINUTES,
      },
    };
  }

  return null;
}

// ============================================================================
// ANOMALY DETECTION: ACHE SPIKE
// ============================================================================
async function detectAcheSpike(bridge_id: string): Promise<DetectedAnomaly | null> {
  // Get recent ache signatures
  const { data, error } = await supabase
    .from("guardian_telemetry_events")
    .select("ache_signature, timestamp_iso")
    .eq("bridge_id", bridge_id)
    .not("ache_signature", "is", null)
    .order("timestamp_iso", { ascending: false })
    .limit(10);

  if (error || !data || data.length < 2) {
    return null;
  }

  const latest = data[0].ache_signature!;
  const previous = data[1].ache_signature!;
  const delta = Math.abs(latest - previous);

  // Check for high ache or large delta
  if (latest > THRESHOLDS.ACHE_HIGH || delta > THRESHOLDS.ACHE_DELTA) {
    return {
      bridge_id,
      anomaly_type: "ACHE_SPIKE",
      severity: latest > 0.90 ? "CRITICAL" : "HIGH",
      details: {
        current_ache: latest,
        previous_ache: previous,
        delta,
        threshold_value: THRESHOLDS.ACHE_HIGH,
        threshold_delta: THRESHOLDS.ACHE_DELTA,
      },
    };
  }

  return null;
}

// ============================================================================
// ANOMALY DETECTION: SCARINDEX DROP
// ============================================================================
async function detectScarIndexDrop(bridge_id: string): Promise<DetectedAnomaly | null> {
  // Get current and recent ScarIndex values
  const { data: current, error: currentError } = await supabase
    .from("guardian_scarindex_current")
    .select("scar_value, updated_at")
    .eq("bridge_id", bridge_id)
    .maybeSingle();

  if (currentError || !current) {
    return null;
  }

  const currentValue = current.scar_value;

  // Check for low ScarIndex
  if (currentValue < THRESHOLDS.SCARINDEX_LOW) {
    return {
      bridge_id,
      anomaly_type: "SCARINDEX_DROP",
      severity: currentValue < 0.25 ? "CRITICAL" : "HIGH",
      details: {
        current_scarindex: currentValue,
        threshold: THRESHOLDS.SCARINDEX_LOW,
        reason: "ScarIndex below threshold",
      },
    };
  }

  // Check for large drop
  const { data: history, error: historyError } = await supabase
    .from("guardian_scarindex_history")
    .select("scar_value, timestamp")
    .eq("bridge_id", bridge_id)
    .order("timestamp", { ascending: false })
    .limit(5);

  if (historyError || !history || history.length < 2) {
    return null;
  }

  const previousValue = history[1].scar_value;
  const dropPercent = ((previousValue - currentValue) / previousValue) * 100;

  if (dropPercent > THRESHOLDS.SCARINDEX_DROP_PERCENT) {
    return {
      bridge_id,
      anomaly_type: "SCARINDEX_DROP",
      severity: dropPercent > 40 ? "CRITICAL" : "HIGH",
      details: {
        current_scarindex: currentValue,
        previous_scarindex: previousValue,
        drop_percent: Math.round(dropPercent * 10) / 10,
        threshold_percent: THRESHOLDS.SCARINDEX_DROP_PERCENT,
      },
    };
  }

  return null;
}

// ============================================================================
// ANOMALY DETECTION: SOVEREIGNTY INSTABILITY
// ============================================================================
async function detectSovereigntyInstability(bridge_id: string): Promise<DetectedAnomaly | null> {
  const oneHourAgo = new Date(Date.now() - 60 * 60 * 1000);

  const { data, error } = await supabase
    .from("guardian_telemetry_events")
    .select("sovereign_state")
    .eq("bridge_id", bridge_id)
    .gte("timestamp_iso", oneHourAgo.toISOString())
    .not("sovereign_state", "is", null)
    .order("timestamp_iso", { ascending: false });

  if (error || !data || data.length < 2) {
    return null;
  }

  // Count unique sovereign states
  const uniqueStates = new Set(data.map((d) => d.sovereign_state));
  const changeCount = uniqueStates.size - 1;

  if (changeCount >= THRESHOLDS.SOVEREIGNTY_CHANGES_PER_HOUR) {
    return {
      bridge_id,
      anomaly_type: "SOVEREIGNTY_INSTABILITY",
      severity: changeCount > 5 ? "CRITICAL" : "MEDIUM",
      details: {
        changes_per_hour: changeCount,
        threshold: THRESHOLDS.SOVEREIGNTY_CHANGES_PER_HOUR,
        unique_states: uniqueStates.size,
        sample_size: data.length,
      },
    };
  }

  return null;
}

// ============================================================================
// ANOMALY DETECTION: ENTROPY SPIKE
// ============================================================================
async function detectEntropySpike(bridge_id: string): Promise<DetectedAnomaly | null> {
  // Calculate entropy from recent telemetry patterns
  const { data, error } = await supabase
    .from("guardian_telemetry_events")
    .select("event_type, source, signal_type")
    .eq("bridge_id", bridge_id)
    .order("timestamp_iso", { ascending: false })
    .limit(20);

  if (error || !data || data.length < 10) {
    return null;
  }

  // Calculate Shannon entropy of event types
  const eventCounts = new Map<string, number>();
  for (const event of data) {
    const key = `${event.event_type}:${event.source}`;
    eventCounts.set(key, (eventCounts.get(key) || 0) + 1);
  }

  let entropy = 0;
  for (const count of eventCounts.values()) {
    const p = count / data.length;
    entropy -= p * Math.log2(p);
  }

  // Normalize entropy to [0, 1]
  const maxEntropy = Math.log2(data.length);
  const normalizedEntropy = entropy / maxEntropy;

  if (normalizedEntropy > THRESHOLDS.ENTROPY_HIGH) {
    return {
      bridge_id,
      anomaly_type: "ENTROPY_SPIKE",
      severity: normalizedEntropy > 0.20 ? "HIGH" : "MEDIUM",
      details: {
        entropy: Math.round(normalizedEntropy * 1000) / 1000,
        threshold: THRESHOLDS.ENTROPY_HIGH,
        unique_patterns: eventCounts.size,
        sample_size: data.length,
      },
    };
  }

  return null;
}

// ============================================================================
// TRIGGER AUTO-REGULATION
// ============================================================================
async function triggerAutoRegulation(bridge_id: string): Promise<void> {
  console.log(`🔧 Triggering auto-regulation for bridge: ${bridge_id}`);

  try {
    const response = await fetch(`${SUPABASE_URL}/functions/v1/guardian_autoregulate`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "x-guardian-api-key": GUARDIAN_API_KEY,
        "Authorization": `Bearer ${SERVICE_ROLE_KEY}`,
      },
      body: JSON.stringify({
        bridge_id,
        mode: "AUTO",
      }),
    });

    if (!response.ok) {
      console.error("❌ Auto-regulation trigger failed:", response.status);
    } else {
      console.log("✅ Auto-regulation triggered successfully");
    }
  } catch (error) {
    console.error("❌ Auto-regulation trigger error:", error);
  }
}

// ============================================================================
// SCAN BRIDGE FOR ANOMALIES
// ============================================================================
async function scanBridge(bridge_id: string): Promise<DetectedAnomaly[]> {
  console.log(`🔍 Scanning bridge: ${bridge_id}`);

  const detectors = [
    detectHeartbeatGap,
    detectAcheSpike,
    detectScarIndexDrop,
    detectSovereigntyInstability,
    detectEntropySpike,
  ];

  const anomalies: DetectedAnomaly[] = [];

  for (const detector of detectors) {
    try {
      const anomaly = await detector(bridge_id);
      if (anomaly) {
        anomalies.push(anomaly);
      }
    } catch (error) {
      console.error(`❌ Detector error for ${detector.name}:`, error);
    }
  }

  return anomalies;
}

// ============================================================================
// MAIN HANDLER
// ============================================================================
serve(async (req: Request): Promise<Response> => {
  const startTime = Date.now();
  const { method } = req;

  // CORS preflight
  if (method === "OPTIONS") {
    return new Response(null, {
      status: 204,
      headers: corsHeaders,
    });
  }

  if (method !== "POST") {
    return jsonResponse(
      { error: "Method not allowed", allowed: ["POST"] },
      405,
    );
  }

  // 🔐 Authentication
  const headerApiKey = req.headers.get("x-guardian-api-key") ?? "";
  if (!GUARDIAN_API_KEY || headerApiKey !== GUARDIAN_API_KEY) {
    return jsonResponse({ error: "Unauthorized" }, 401);
  }

  // Parse request body
  let body: AnomalyDetectionRequest;
  try {
    body = (await req.json()) as AnomalyDetectionRequest;
  } catch (_e) {
    body = { scan_all: true };
  }

  const { bridge_id, scan_all = false } = body;

  // Get bridges to scan
  let bridgeIds: string[] = [];

  if (bridge_id) {
    bridgeIds = [bridge_id];
  } else if (scan_all) {
    const { data, error } = await supabase
      .from("bridge_nodes")
      .select("id")
      .eq("is_active", true);

    if (error) {
      return jsonResponse(
        { error: "Failed to fetch bridges", details: error.message },
        500,
      );
    }

    bridgeIds = data.map((b) => b.id);
  } else {
    return jsonResponse({ error: "Either bridge_id or scan_all is required" }, 400);
  }

  console.log(`🔍 Scanning ${bridgeIds.length} bridge(s) for anomalies`);

  // Scan all bridges
  const results: Array<{
    bridge_id: string;
    anomalies: DetectedAnomaly[];
    inserted: string[];
  }> = [];

  for (const bid of bridgeIds) {
    const anomalies = await scanBridge(bid);
    const inserted: string[] = [];

    for (const anomaly of anomalies) {
      const anomalyId = await insertAnomaly(anomaly);
      if (anomalyId) {
        inserted.push(anomalyId);
      }
    }

    results.push({
      bridge_id: bid,
      anomalies,
      inserted,
    });

    // Trigger auto-regulation for HIGH/CRITICAL anomalies (Phase 8.4)
    const hasHighPriorityAnomaly = anomalies.some(
      (a) => a.severity === "HIGH" || a.severity === "CRITICAL",
    );

    if (hasHighPriorityAnomaly && inserted.length > 0) {
      console.log(`⚠️ High-priority anomaly detected, triggering auto-regulation`);
      await triggerAutoRegulation(bid);
    }
  }

  // Count totals
  const totalAnomalies = results.reduce((sum, r) => sum + r.anomalies.length, 0);
  const totalInserted = results.reduce((sum, r) => sum + r.inserted.length, 0);

  // Send Discord notification
  if (totalInserted > 0) {
    await notifyDiscord(
      `⚠️ **Anomaly Detection Alert**`,
      [{
        color: 0xFFA500,
        title: `Detected ${totalInserted} New Anomaly(ies)`,
        description: `Scanned ${bridgeIds.length} bridge(s)`,
        fields: results
          .filter((r) => r.inserted.length > 0)
          .map((r) => ({
            name: `Bridge ${r.bridge_id.substring(0, 8)}...`,
            value: r.anomalies
              .map((a) => `• ${a.anomaly_type} (${a.severity})`)
              .join("\n"),
            inline: false,
          })),
        timestamp: new Date().toISOString(),
      }],
    );
  }

  console.log(`✅ Anomaly detection completed: ${totalInserted}/${totalAnomalies} new anomalies`);

  return jsonResponse({
    success: true,
    message: `Scanned ${bridgeIds.length} bridge(s)`,
    results,
    summary: {
      bridges_scanned: bridgeIds.length,
      total_anomalies_detected: totalAnomalies,
      total_anomalies_inserted: totalInserted,
      auto_regulation_triggered: totalInserted > 0,
    },
    processing_time_ms: Date.now() - startTime,
  });
});

