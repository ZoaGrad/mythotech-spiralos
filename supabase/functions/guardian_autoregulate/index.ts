
// supabase/functions/guardian_autoregulate/index.ts
// Phase 8.4: Auto-Regulation Engine
// Implements 6 healing strategies for autonomous Guardian system correction

import { serve } from "https://deno.land/std@0.224.0/http/server.ts";
import { createClient } from "jsr:@supabase/supabase-js@2";

// ============================================================================
// TYPES
// ============================================================================
type AutoRegulationRequest = {
  anomaly_id?: string;
  bridge_id?: string;
  mode?: "AUTO" | "MANUAL";
};

type Anomaly = {
  id: string;
  bridge_id: string;
  anomaly_type: string;
  severity: string;
  details: Record<string, unknown>;
  status: string;
  detected_at: string;
};

type CorrectionProfile = {
  profile_id: string;
  bridge_id: string;
  baseline_health: number | null;
  preferred_correction_types: string[];
  last_mutation: string | null;
  correction_budget: number;
  cooldown_seconds: number;
  metadata: Record<string, unknown>;
  updated_at: string;
};

type CorrectionResult = {
  correction_type: string;
  success: boolean;
  details: string;
  affected_entities?: string[];
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
    } else {
      console.log("✅ Discord notification sent");
    }
  } catch (error) {
    console.error("❌ Discord notification error:", error);
  }
}

// ============================================================================
// CORRECTION PROFILE MANAGEMENT
// ============================================================================
async function getOrCreateCorrectionProfile(
  bridge_id: string,
): Promise<CorrectionProfile | null> {
  // Try to get existing profile
  const { data: existing, error: fetchError } = await supabase
    .from("guardian_correction_profiles")
    .select("*")
    .eq("bridge_id", bridge_id)
    .maybeSingle();

  if (fetchError) {
    console.error("❌ Error fetching correction profile:", fetchError);
    return null;
  }

  if (existing) {
    return existing as CorrectionProfile;
  }

  // Create new profile
  const { data: created, error: createError } = await supabase
    .from("guardian_correction_profiles")
    .insert({
      bridge_id,
      baseline_health: 0.8,
      preferred_correction_types: [
        "HEARTBEAT_CORRECTION",
        "ACHE_BUFFER",
        "SCARINDEX_RECOVERY_PULSE",
      ],
      correction_budget: 100,
      cooldown_seconds: 300,
      metadata: { auto_created: true },
    })
    .select()
    .single();

  if (createError) {
    console.error("❌ Error creating correction profile:", createError);
    return null;
  }

  console.log("✅ Created new correction profile for bridge:", bridge_id);
  return created as CorrectionProfile;
}

async function checkCooldown(
  bridge_id: string,
  cooldown_seconds: number,
): Promise<boolean> {
  const { data, error } = await supabase
    .from("guardian_autoregulation_history")
    .select("created_at")
    .eq("bridge_id", bridge_id)
    .order("created_at", { ascending: false })
    .limit(1)
    .maybeSingle();

  if (error) {
    console.error("❌ Error checking cooldown:", error);
    return false; // Allow correction on error
  }

  if (!data) return true; // No previous corrections

  const lastCorrection = new Date(data.created_at).getTime();
  const now = Date.now();
  const elapsed = (now - lastCorrection) / 1000;

  return elapsed >= cooldown_seconds;
}

async function logCorrection(
  bridge_id: string,
  anomaly_id: string | null,
  correction_type: string,
  severity_level: string,
  success: boolean,
  correction_payload: Record<string, unknown>,
): Promise<void> {
  const { error } = await supabase
    .from("guardian_autoregulation_history")
    .insert({
      bridge_id,
      anomaly_id,
      correction_type,
      severity_level,
      success,
      correction_payload,
      metadata: { timestamp: new Date().toISOString() },
    });

  if (error) {
    console.error("❌ Error logging correction:", error);
  }
}

// ============================================================================
// HEALING STRATEGY 1: SCARINDEX RECOVERY PULSE
// ============================================================================
async function applyScarIndexRecoveryPulse(
  anomaly: Anomaly,
): Promise<CorrectionResult> {
  console.log("🔧 Applying ScarIndex Recovery Pulse for bridge:", anomaly.bridge_id);

  try {
    // Get current ScarIndex
    const { data: currentScar, error: fetchError } = await supabase
      .from("guardian_scarindex_current")
      .select("*")
      .eq("bridge_id", anomaly.bridge_id)
      .maybeSingle();

    if (fetchError || !currentScar) {
      console.error("❌ Failed to fetch current ScarIndex");
      return {
        correction_type: "SCARINDEX_RECOVERY_PULSE",
        success: false,
        details: "Failed to fetch current ScarIndex",
      };
    }

    const currentValue = currentScar.scar_value || 0;
    const targetValue = Math.max(0.5, currentValue * 1.15); // 15% recovery toward healthy range
    const recoveryDelta = targetValue - currentValue;

    // Apply recovery pulse
    const { error: updateError } = await supabase
      .from("guardian_scarindex_current")
      .update({
        scar_value: targetValue,
        updated_at: new Date().toISOString(),
      })
      .eq("bridge_id", anomaly.bridge_id);

    if (updateError) {
      console.error("❌ Failed to apply ScarIndex recovery:", updateError);
      return {
        correction_type: "SCARINDEX_RECOVERY_PULSE",
        success: false,
        details: "Failed to update ScarIndex",
      };
    }

    // Log to history
    await supabase.from("guardian_scarindex_history").insert({
      bridge_id: anomaly.bridge_id,
      scar_value: targetValue,
      delta: recoveryDelta,
      source: "auto_regulation",
      metadata: {
        anomaly_id: anomaly.id,
        recovery_pulse: true,
        original_value: currentValue,
      },
    });

    console.log(`✅ ScarIndex recovered: ${currentValue.toFixed(4)} → ${targetValue.toFixed(4)}`);

    return {
      correction_type: "SCARINDEX_RECOVERY_PULSE",
      success: true,
      details: `ScarIndex recovered from ${currentValue.toFixed(4)} to ${targetValue.toFixed(4)}`,
      affected_entities: [anomaly.bridge_id],
    };
  } catch (error) {
    console.error("❌ ScarIndex recovery error:", error);
    return {
      correction_type: "SCARINDEX_RECOVERY_PULSE",
      success: false,
      details: `Error: ${error instanceof Error ? error.message : "Unknown error"}`,
    };
  }
}

// ============================================================================
// HEALING STRATEGY 2: SOVEREIGNTY DRIFT STABILIZER
// ============================================================================
async function applySovereigntyStabilizer(
  anomaly: Anomaly,
): Promise<CorrectionResult> {
  console.log("🔧 Applying Sovereignty Drift Stabilizer for bridge:", anomaly.bridge_id);

  try {
    // Get recent sovereign states
    const { data: recentStates, error: fetchError } = await supabase
      .from("guardian_telemetry_events")
      .select("sovereign_state")
      .eq("bridge_id", anomaly.bridge_id)
      .order("timestamp_iso", { ascending: false })
      .limit(10);

    if (fetchError || !recentStates || recentStates.length === 0) {
      console.error("❌ Failed to fetch sovereign states");
      return {
        correction_type: "SOVEREIGNTY_STABILIZER",
        success: false,
        details: "Failed to fetch sovereign states",
      };
    }

    // Find the most stable state (most frequent in recent history)
    const stateFrequency = new Map<string, number>();
    for (const state of recentStates) {
      if (state.sovereign_state) {
        const count = stateFrequency.get(state.sovereign_state) || 0;
        stateFrequency.set(state.sovereign_state, count + 1);
      }
    }

    let stableState = "";
    let maxFrequency = 0;
    for (const [state, frequency] of stateFrequency) {
      if (frequency > maxFrequency) {
        maxFrequency = frequency;
        stableState = state;
      }
    }

    if (!stableState) {
      return {
        correction_type: "SOVEREIGNTY_STABILIZER",
        success: false,
        details: "No stable sovereign state found",
      };
    }

    // Insert a synthetic stabilization event
    const { error: insertError } = await supabase
      .from("guardian_telemetry_events")
      .insert({
        bridge_id: anomaly.bridge_id,
        gateway_key: `bridge-${anomaly.bridge_id}`,
        event_type: "sovereignty_stabilization",
        source: "auto_regulation",
        signal_type: "stabilization_signal",
        timestamp_iso: new Date().toISOString(),
        timestamp_epoch: Date.now(),
        timestamp_drift_ms: 0,
        payload: {
          anomaly_id: anomaly.id,
          stabilized_state: stableState,
        },
        sovereign_state: stableState,
        ache_signature: 0.3,
        agent_health: 0.8,
        metadata: {
          correction_type: "SOVEREIGNTY_STABILIZER",
        },
      });

    if (insertError) {
      console.error("❌ Failed to insert stabilization event:", insertError);
      return {
        correction_type: "SOVEREIGNTY_STABILIZER",
        success: false,
        details: "Failed to insert stabilization event",
      };
    }

    console.log(`✅ Sovereignty stabilized to: ${stableState}`);

    return {
      correction_type: "SOVEREIGNTY_STABILIZER",
      success: true,
      details: `Sovereignty stabilized to: ${stableState}`,
      affected_entities: [anomaly.bridge_id],
    };
  } catch (error) {
    console.error("❌ Sovereignty stabilization error:", error);
    return {
      correction_type: "SOVEREIGNTY_STABILIZER",
      success: false,
      details: `Error: ${error instanceof Error ? error.message : "Unknown error"}`,
    };
  }
}

// ============================================================================
// HEALING STRATEGY 3: ACHE BUFFERING
// ============================================================================
async function applyAcheBuffering(
  anomaly: Anomaly,
): Promise<CorrectionResult> {
  console.log("🔧 Applying Ache Buffering for bridge:", anomaly.bridge_id);

  try {
    // Get correction profile
    const profile = await getOrCreateCorrectionProfile(anomaly.bridge_id);
    if (!profile) {
      return {
        correction_type: "ACHE_BUFFER",
        success: false,
        details: "Failed to get correction profile",
      };
    }

    // Set buffering flag in metadata
    const updatedMetadata = {
      ...profile.metadata,
      ache_buffer_active: true,
      ache_buffer_started: new Date().toISOString(),
      ache_buffer_duration_seconds: 1800, // 30 minutes
      dampening_factor: 0.7, // Reduce ache impact by 30%
    };

    const { error: updateError } = await supabase
      .from("guardian_correction_profiles")
      .update({
        metadata: updatedMetadata,
        updated_at: new Date().toISOString(),
      })
      .eq("bridge_id", anomaly.bridge_id);

    if (updateError) {
      console.error("❌ Failed to apply ache buffering:", updateError);
      return {
        correction_type: "ACHE_BUFFER",
        success: false,
        details: "Failed to update correction profile",
      };
    }

    console.log("✅ Ache buffering applied for 30 minutes");

    return {
      correction_type: "ACHE_BUFFER",
      success: true,
      details: "Ache buffering active for 30 minutes with 0.7x dampening",
      affected_entities: [anomaly.bridge_id],
    };
  } catch (error) {
    console.error("❌ Ache buffering error:", error);
    return {
      correction_type: "ACHE_BUFFER",
      success: false,
      details: `Error: ${error instanceof Error ? error.message : "Unknown error"}`,
    };
  }
}

// ============================================================================
// HEALING STRATEGY 4: HEARTBEAT CORRECTION
// ============================================================================
async function applyHeartbeatCorrection(
  anomaly: Anomaly,
): Promise<CorrectionResult> {
  console.log("🔧 Applying Heartbeat Correction for bridge:", anomaly.bridge_id);

  try {
    // Insert synthetic heartbeat event
    const { error: insertError } = await supabase
      .from("guardian_telemetry_events")
      .insert({
        bridge_id: anomaly.bridge_id,
        gateway_key: `bridge-${anomaly.bridge_id}`,
        event_type: "synthetic_heartbeat",
        source: "auto_regulation",
        signal_type: "health_signal",
        timestamp_iso: new Date().toISOString(),
        timestamp_epoch: Date.now(),
        timestamp_drift_ms: 0,
        payload: {
          anomaly_id: anomaly.id,
          synthetic: true,
          reason: "heartbeat_gap_detected",
        },
        ache_signature: 0.5,
        agent_health: 0.7,
        metadata: {
          correction_type: "HEARTBEAT_CORRECTION",
        },
      });

    if (insertError) {
      console.error("❌ Failed to insert synthetic heartbeat:", insertError);
      return {
        correction_type: "HEARTBEAT_CORRECTION",
        success: false,
        details: "Failed to insert synthetic heartbeat",
      };
    }

    console.log("✅ Synthetic heartbeat inserted");

    return {
      correction_type: "HEARTBEAT_CORRECTION",
      success: true,
      details: "Synthetic heartbeat event inserted to maintain telemetry continuity",
      affected_entities: [anomaly.bridge_id],
    };
  } catch (error) {
    console.error("❌ Heartbeat correction error:", error);
    return {
      correction_type: "HEARTBEAT_CORRECTION",
      success: false,
      details: `Error: ${error instanceof Error ? error.message : "Unknown error"}`,
    };
  }
}

// ============================================================================
// HEALING STRATEGY 5: ENTROPY CORRECTION
// ============================================================================
async function applyEntropyCorrection(
  anomaly: Anomaly,
): Promise<CorrectionResult> {
  console.log("🔧 Applying Entropy Correction for bridge:", anomaly.bridge_id);

  try {
    // Get correction profile
    const profile = await getOrCreateCorrectionProfile(anomaly.bridge_id);
    if (!profile) {
      return {
        correction_type: "ENTROPY_CORRECTION",
        success: false,
        details: "Failed to get correction profile",
      };
    }

    // Tighten anomaly thresholds temporarily
    const updatedMetadata = {
      ...profile.metadata,
      entropy_correction_active: true,
      entropy_correction_started: new Date().toISOString(),
      entropy_correction_duration_seconds: 3600, // 1 hour
      tightened_thresholds: {
        ache_threshold: 0.70, // Normal: 0.80
        entropy_threshold: 0.12, // Normal: 0.15
        scarindex_threshold: 0.45, // Normal: 0.40
      },
    };

    const { error: updateError } = await supabase
      .from("guardian_correction_profiles")
      .update({
        metadata: updatedMetadata,
        updated_at: new Date().toISOString(),
      })
      .eq("bridge_id", anomaly.bridge_id);

    if (updateError) {
      console.error("❌ Failed to apply entropy correction:", updateError);
      return {
        correction_type: "ENTROPY_CORRECTION",
        success: false,
        details: "Failed to update correction profile",
      };
    }

    console.log("✅ Entropy correction applied - thresholds tightened for 1 hour");

    return {
      correction_type: "ENTROPY_CORRECTION",
      success: true,
      details: "Anomaly detection thresholds tightened for 1 hour to reduce entropy",
      affected_entities: [anomaly.bridge_id],
    };
  } catch (error) {
    console.error("❌ Entropy correction error:", error);
    return {
      correction_type: "ENTROPY_CORRECTION",
      success: false,
      details: `Error: ${error instanceof Error ? error.message : "Unknown error"}`,
    };
  }
}

// ============================================================================
// HEALING STRATEGY 6: SELF-PRESERVATION FREEZE MODE
// ============================================================================
async function applySelfPreservationFreeze(
  anomaly: Anomaly,
): Promise<CorrectionResult> {
  console.log("🔧 Applying Self-Preservation Freeze Mode for bridge:", anomaly.bridge_id);

  try {
    // Get correction profile
    const profile = await getOrCreateCorrectionProfile(anomaly.bridge_id);
    if (!profile) {
      return {
        correction_type: "SELF_PRESERVATION_FREEZE",
        success: false,
        details: "Failed to get correction profile",
      };
    }

    // Set freeze flag
    const updatedMetadata = {
      ...profile.metadata,
      freeze_mode_active: true,
      freeze_started: new Date().toISOString(),
      freeze_duration_seconds: 1800, // 30 minutes
      freeze_reason: `CRITICAL anomaly: ${anomaly.anomaly_type}`,
    };

    const { error: updateError } = await supabase
      .from("guardian_correction_profiles")
      .update({
        metadata: updatedMetadata,
        correction_budget: 0, // Prevent further corrections
        updated_at: new Date().toISOString(),
      })
      .eq("bridge_id", anomaly.bridge_id);

    if (updateError) {
      console.error("❌ Failed to apply freeze mode:", updateError);
      return {
        correction_type: "SELF_PRESERVATION_FREEZE",
        success: false,
        details: "Failed to update correction profile",
      };
    }

    // Send critical alert to Discord
    await notifyDiscord(
      `🚨 **CRITICAL: Self-Preservation Freeze Activated**`,
      [{
        color: 0xFF0000,
        title: "Self-Preservation Freeze Mode",
        description: `Bridge frozen due to CRITICAL anomaly: ${anomaly.anomaly_type}`,
        fields: [
          {
            name: "Bridge ID",
            value: anomaly.bridge_id,
            inline: true,
          },
          {
            name: "Anomaly Type",
            value: anomaly.anomaly_type,
            inline: true,
          },
          {
            name: "Duration",
            value: "30 minutes",
            inline: true,
          },
        ],
        timestamp: new Date().toISOString(),
      }],
    );

    console.log("✅ Self-preservation freeze mode activated");

    return {
      correction_type: "SELF_PRESERVATION_FREEZE",
      success: true,
      details: "Bridge frozen for 30 minutes to prevent cascading failures",
      affected_entities: [anomaly.bridge_id],
    };
  } catch (error) {
    console.error("❌ Freeze mode error:", error);
    return {
      correction_type: "SELF_PRESERVATION_FREEZE",
      success: false,
      details: `Error: ${error instanceof Error ? error.message : "Unknown error"}`,
    };
  }
}

// ============================================================================
// CORRECTION STRATEGY DISPATCHER
// ============================================================================
async function applyCorrection(anomaly: Anomaly): Promise<CorrectionResult> {
  const { anomaly_type, severity } = anomaly;

  // Check if bridge is frozen
  const profile = await getOrCreateCorrectionProfile(anomaly.bridge_id);
  if (
    profile &&
    profile.metadata.freeze_mode_active &&
    severity !== "CRITICAL"
  ) {
    console.log("⚠️ Bridge is frozen, skipping non-critical correction");
    return {
      correction_type: "NONE",
      success: false,
      details: "Bridge is in freeze mode, non-critical corrections disabled",
    };
  }

  // Check cooldown (except for CRITICAL)
  if (profile && severity !== "CRITICAL") {
    const cooldownOk = await checkCooldown(
      anomaly.bridge_id,
      profile.cooldown_seconds,
    );
    if (!cooldownOk) {
      console.log("⚠️ Cooldown period active, skipping correction");
      return {
        correction_type: "NONE",
        success: false,
        details: "Cooldown period active",
      };
    }
  }

  // Apply appropriate correction based on anomaly type
  let result: CorrectionResult;

  switch (anomaly_type) {
    case "SCARINDEX_DROP":
    case "SCARINDEX_LOW":
      result = await applyScarIndexRecoveryPulse(anomaly);
      break;

    case "SOVEREIGNTY_INSTABILITY":
      result = await applySovereigntyStabilizer(anomaly);
      break;

    case "ACHE_SPIKE":
    case "ACHE_HIGH":
      result = await applyAcheBuffering(anomaly);
      break;

    case "HEARTBEAT_GAP":
    case "HEARTBEAT_MISSING":
      result = await applyHeartbeatCorrection(anomaly);
      break;

    case "ENTROPY_SPIKE":
    case "ENTROPY_HIGH":
      result = await applyEntropyCorrection(anomaly);
      break;

    default:
      console.log(`⚠️ No specific correction for anomaly type: ${anomaly_type}`);
      result = {
        correction_type: "NONE",
        success: false,
        details: `No correction strategy for anomaly type: ${anomaly_type}`,
      };
  }

  // For CRITICAL severity, also apply freeze mode
  if (severity === "CRITICAL" && result.success) {
    const freezeResult = await applySelfPreservationFreeze(anomaly);
    if (freezeResult.success) {
      result.details += " + Freeze mode activated";
    }
  }

  // Log the correction
  await logCorrection(
    anomaly.bridge_id,
    anomaly.id,
    result.correction_type,
    severity,
    result.success,
    {
      anomaly_type,
      details: result.details,
      affected_entities: result.affected_entities || [],
    },
  );

  return result;
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
  let body: AutoRegulationRequest;
  try {
    body = (await req.json()) as AutoRegulationRequest;
  } catch (_e) {
    return jsonResponse({ error: "Invalid JSON body" }, 400);
  }

  const { anomaly_id, bridge_id, mode = "AUTO" } = body;

  // Validate: need either anomaly_id or bridge_id
  if (!anomaly_id && !bridge_id) {
    return jsonResponse(
      { error: "Either anomaly_id or bridge_id is required" },
      400,
    );
  }

  console.log(`🔧 Auto-regulation request: mode=${mode}, anomaly_id=${anomaly_id}, bridge_id=${bridge_id}`);

  // Fetch anomalies to process
  let anomalies: Anomaly[] = [];

  if (anomaly_id) {
    // Process specific anomaly
    const { data, error } = await supabase
      .from("guardian_anomalies")
      .select("*")
      .eq("id", anomaly_id)
      .eq("status", "ACTIVE")
      .maybeSingle();

    if (error) {
      console.error("❌ Error fetching anomaly:", error);
      return jsonResponse(
        { error: "Failed to fetch anomaly", details: error.message },
        500,
      );
    }

    if (data) {
      anomalies = [data as Anomaly];
    }
  } else if (bridge_id) {
    // Process all active anomalies for bridge
    const { data, error } = await supabase
      .from("guardian_anomalies")
      .select("*")
      .eq("bridge_id", bridge_id)
      .eq("status", "ACTIVE")
      .order("severity", { ascending: false }) // CRITICAL first
      .order("detected_at", { ascending: true }); // Oldest first

    if (error) {
      console.error("❌ Error fetching anomalies:", error);
      return jsonResponse(
        { error: "Failed to fetch anomalies", details: error.message },
        500,
      );
    }

    anomalies = (data as Anomaly[]) || [];
  }

  if (anomalies.length === 0) {
    return jsonResponse({
      success: true,
      message: "No active anomalies to process",
      corrections: [],
      processing_time_ms: Date.now() - startTime,
    });
  }

  console.log(`📋 Processing ${anomalies.length} anomaly(ies)`);

  // Apply corrections
  const corrections: Array<{
    anomaly_id: string;
    bridge_id: string;
    anomaly_type: string;
    severity: string;
    result: CorrectionResult;
  }> = [];

  for (const anomaly of anomalies) {
    console.log(`\n🔍 Processing anomaly: ${anomaly.id} (${anomaly.anomaly_type})`);
    const result = await applyCorrection(anomaly);
    
    corrections.push({
      anomaly_id: anomaly.id,
      bridge_id: anomaly.bridge_id,
      anomaly_type: anomaly.anomaly_type,
      severity: anomaly.severity,
      result,
    });

    // If correction was successful, update anomaly status
    if (result.success && result.correction_type !== "NONE") {
      await supabase
        .from("guardian_anomalies")
        .update({
          status: "RESOLVED",
          metadata: {
            ...(anomaly.details || {}),
            resolved_at: new Date().toISOString(),
            resolved_by: "auto_regulation",
            correction_type: result.correction_type,
          },
        })
        .eq("id", anomaly.id);
    }
  }

  // Send summary to Discord
  const successCount = corrections.filter((c) => c.result.success).length;
  const failureCount = corrections.length - successCount;

  await notifyDiscord(
    `🔧 **Auto-Regulation Summary**`,
    [{
      color: successCount === corrections.length ? 0x00FF00 : 0xFFA500,
      title: `Processed ${corrections.length} Anomaly(ies)`,
      fields: [
        {
          name: "✅ Successful Corrections",
          value: successCount.toString(),
          inline: true,
        },
        {
          name: "❌ Failed Corrections",
          value: failureCount.toString(),
          inline: true,
        },
        {
          name: "Corrections Applied",
          value: corrections
            .filter((c) => c.result.success)
            .map((c) => `• ${c.result.correction_type}`)
            .join("\n") || "None",
          inline: false,
        },
      ],
      timestamp: new Date().toISOString(),
    }],
  );

  console.log(`\n✅ Auto-regulation completed: ${successCount}/${corrections.length} successful`);

  return jsonResponse({
    success: true,
    message: `Processed ${corrections.length} anomaly(ies)`,
    corrections,
    summary: {
      total: corrections.length,
      successful: successCount,
      failed: failureCount,
    },
    processing_time_ms: Date.now() - startTime,
  });
});

