
// supabase/functions/telemetry_normalize/index.ts
// Phase 8.1: Telemetry Normalization Engine
// Transforms raw telemetry into unified, analyzable structure

import { serve } from "https://deno.land/std@0.224.0/http/server.ts";
import { createClient } from "jsr:@supabase/supabase-js@2";

// ============================================================================
// TYPES
// ============================================================================
type RawTelemetryPayload = {
  gateway_key: string;
  bridge_id?: string;
  event_type: string;
  source?: string;
  timestamp?: string | number;
  payload?: Record<string, unknown>;
  metadata?: Record<string, unknown>;
};

type NormalizedEvent = {
  id: string;
  bridge_id: string | null;
  gateway_key: string;
  event_type: string;
  source: string;
  signal_type: string | null;
  timestamp_iso: string;
  timestamp_epoch: number;
  timestamp_drift_ms: number;
  payload: Record<string, unknown>;
  normalized_payload: Record<string, unknown>;
  ache_signature: number;
  agent_health: number;
  latency_ms: number;
  sovereign_state: string;
  metadata: Record<string, unknown>;
  created_at: string;
};

// ============================================================================
// ENVIRONMENT
// ============================================================================
const SUPABASE_URL = Deno.env.get("SUPABASE_URL")!;
const SERVICE_ROLE_KEY = Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!;
const GUARDIAN_API_KEY = Deno.env.get("GUARDIAN_API_KEY") ?? "";

const supabase = createClient(SUPABASE_URL, SERVICE_ROLE_KEY);

const corsHeaders = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Methods": "POST, OPTIONS",
  "Access-Control-Allow-Headers":
    "authorization, x-guardian-api-key, content-type",
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
// BRIDGE RESOLUTION
// ============================================================================
async function resolveBridgeId(gateway_key: string): Promise<string | null> {
  const { data, error } = await supabase
    .from("bridge_gateways")
    .select("bridge_id")
    .eq("gateway_key", gateway_key)
    .limit(1)
    .maybeSingle();

  if (error) {
    console.error("❌ Error resolving bridge_id:", error);
    return null;
  }

  return data?.bridge_id ?? null;
}

// ============================================================================
// SOURCE CLASSIFICATION
// ============================================================================
function classifySource(
  providedSource?: string,
  payload?: Record<string, unknown>,
): string {
  if (providedSource) return providedSource;

  // Heuristic classification based on payload structure
  if (payload?.guild_id || payload?.channel_id) return "discord_bot";
  if (payload?.repository || payload?.pull_request) return "github_webhook";
  if (payload?.manual === true) return "manual";
  if (payload?.scheduled === true) return "scheduled";

  return "unknown";
}

// ============================================================================
// SIGNAL TYPE CLASSIFICATION
// ============================================================================
function classifySignalType(
  event_type: string,
  source: string,
): string | null {
  const eventLower = event_type.toLowerCase();

  // High-priority signals
  if (eventLower.includes("error") || eventLower.includes("fail")) {
    return "error_signal";
  }
  if (eventLower.includes("warning") || eventLower.includes("alert")) {
    return "warning_signal";
  }

  // Activity signals
  if (eventLower.includes("message") || eventLower.includes("post")) {
    return "activity_signal";
  }
  if (eventLower.includes("sync") || eventLower.includes("update")) {
    return "sync_signal";
  }

  // Health signals
  if (eventLower.includes("health") || eventLower.includes("status")) {
    return "health_signal";
  }

  // Source-based classification
  if (source === "discord_bot") return "discord_signal";
  if (source === "github_webhook") return "github_signal";

  return "generic_signal";
}

// ============================================================================
// ACHE SIGNATURE CALCULATION
// ============================================================================
function calculateAcheSignature(
  event_type: string,
  payload: Record<string, unknown>,
  source: string,
): number {
  let signature = 0.5; // baseline

  const eventLower = event_type.toLowerCase();

  // Error/failure events have high ache
  if (eventLower.includes("error") || eventLower.includes("fail")) {
    signature += 0.3;
  }

  // Warning events have moderate ache
  if (eventLower.includes("warning") || eventLower.includes("alert")) {
    signature += 0.2;
  }

  // Success events reduce ache
  if (eventLower.includes("success") || eventLower.includes("complete")) {
    signature -= 0.2;
  }

  // Payload complexity increases ache
  const payloadSize = JSON.stringify(payload).length;
  if (payloadSize > 1000) signature += 0.1;
  if (payloadSize > 5000) signature += 0.1;

  // Source-specific adjustments
  if (source === "discord_bot" && payload.content) {
    const content = String(payload.content);
    if (content.includes("!") || content.includes("?")) signature += 0.05;
  }

  // Clamp to [0, 1]
  return Math.max(0, Math.min(1, signature));
}

// ============================================================================
// AGENT HEALTH ESTIMATION
// ============================================================================
function estimateAgentHealth(
  event_type: string,
  payload: Record<string, unknown>,
  ache_signature: number,
): number {
  let health = 0.8; // baseline healthy

  const eventLower = event_type.toLowerCase();

  // Error events reduce health
  if (eventLower.includes("error") || eventLower.includes("fail")) {
    health -= 0.3;
  }

  // Warning events slightly reduce health
  if (eventLower.includes("warning")) {
    health -= 0.1;
  }

  // Success events improve health
  if (eventLower.includes("success") || eventLower.includes("complete")) {
    health += 0.1;
  }

  // High ache reduces health
  health -= ache_signature * 0.2;

  // Payload indicators
  if (payload.success === false) health -= 0.2;
  if (payload.success === true) health += 0.1;

  // Clamp to [0, 1]
  return Math.max(0, Math.min(1, health));
}

// ============================================================================
// SOVEREIGN STATE FINGERPRINT
// ============================================================================
function generateSovereignState(
  bridge_id: string | null,
  gateway_key: string,
  timestamp_epoch: number,
): string {
  // Simple fingerprint: bridge_id + gateway_key + time bucket (5min)
  const timeBucket = Math.floor(timestamp_epoch / 300000); // 5-minute buckets
  const components = [
    bridge_id ?? "null",
    gateway_key.substring(0, 8),
    timeBucket.toString(),
  ];

  return components.join(":");
}

// ============================================================================
// PAYLOAD NORMALIZATION
// ============================================================================
function normalizePayload(
  payload: Record<string, unknown>,
  source: string,
): Record<string, unknown> {
  const normalized: Record<string, unknown> = { ...payload };

  // Discord-specific normalization
  if (source === "discord_bot") {
    if (payload.content) {
      normalized.message_length = String(payload.content).length;
      normalized.has_mentions = String(payload.content).includes("@");
    }
  }

  // GitHub-specific normalization
  if (source === "github_webhook") {
    if (payload.repository) {
      normalized.repo_name = (payload.repository as Record<string, unknown>)
        .name;
    }
    if (payload.action) {
      normalized.webhook_action = payload.action;
    }
  }

  // Add normalization timestamp
  normalized._normalized_at = new Date().toISOString();

  return normalized;
}

// ============================================================================
// CANONICAL TIMESTAMPING
// ============================================================================
function canonicalTimestamp(providedTimestamp?: string | number): {
  timestamp_iso: string;
  timestamp_epoch: number;
  timestamp_drift_ms: number;
} {
  const serverNow = Date.now();
  let clientTime: number;

  if (typeof providedTimestamp === "number") {
    clientTime = providedTimestamp;
  } else if (typeof providedTimestamp === "string") {
    clientTime = new Date(providedTimestamp).getTime();
  } else {
    clientTime = serverNow;
  }

  const drift = serverNow - clientTime;

  return {
    timestamp_iso: new Date(serverNow).toISOString(),
    timestamp_epoch: serverNow,
    timestamp_drift_ms: Math.round(drift),
  };
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
  let body: RawTelemetryPayload;
  try {
    body = (await req.json()) as RawTelemetryPayload;
  } catch (_e) {
    return jsonResponse({ error: "Invalid JSON body" }, 400);
  }

  const {
    gateway_key,
    bridge_id: providedBridgeId,
    event_type,
    source: providedSource,
    timestamp: providedTimestamp,
    payload = {},
    metadata = {},
  } = body;

  // Validate required fields
  if (!gateway_key) {
    return jsonResponse({ error: "gateway_key is required" }, 400);
  }
  if (!event_type) {
    return jsonResponse({ error: "event_type is required" }, 400);
  }

  // 1. Resolve bridge_id from gateway_key
  const resolvedBridgeId = providedBridgeId ??
    (await resolveBridgeId(gateway_key));

  // 2. Classify source
  const source = classifySource(providedSource, payload);

  // 3. Canonical timestamping
  const { timestamp_iso, timestamp_epoch, timestamp_drift_ms } =
    canonicalTimestamp(providedTimestamp);

  // 4. Classify signal type
  const signal_type = classifySignalType(event_type, source);

  // 5. Calculate ache signature
  const ache_signature = calculateAcheSignature(event_type, payload, source);

  // 6. Estimate agent health
  const agent_health = estimateAgentHealth(
    event_type,
    payload,
    ache_signature,
  );

  // 7. Generate sovereign state fingerprint
  const sovereign_state = generateSovereignState(
    resolvedBridgeId,
    gateway_key,
    timestamp_epoch,
  );

  // 8. Normalize payload
  const normalized_payload = normalizePayload(payload, source);

  // 9. Calculate latency
  const latency_ms = Date.now() - startTime;

  // 10. Insert into guardian_telemetry_events
  const { data, error } = await supabase
    .from("guardian_telemetry_events")
    .insert({
      bridge_id: resolvedBridgeId,
      gateway_key,
      event_type,
      source,
      signal_type,
      timestamp_iso,
      timestamp_epoch,
      timestamp_drift_ms,
      payload,
      normalized_payload,
      ache_signature,
      agent_health,
      latency_ms,
      sovereign_state,
      metadata,
    })
    .select()
    .single();

  if (error) {
    console.error("❌ Error inserting normalized event:", error);
    return jsonResponse(
      { error: "Failed to insert normalized event", details: error.message },
      500,
    );
  }

  console.log("✅ Normalized event created:", data.id);

  return jsonResponse({
    success: true,
    event: data as NormalizedEvent,
    processing_time_ms: Date.now() - startTime,
  });
});

