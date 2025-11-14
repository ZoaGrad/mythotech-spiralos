// supabase/functions/gateway-telemetry/index.ts
// Phase 7.2: Auto-resolve bridge_id from gateway_key
import { serve } from "https://deno.land/std@0.224.0/http/server.ts";
import { createClient } from "jsr:@supabase/supabase-js@2";

type TelemetryPayload = {
  gateway_key?: string;
  bridge_id?: string;
  agent_id?: string;
  event_type?: string;
  source?: string;
  payload?: Record<string, unknown>;
  metadata?: Record<string, unknown>;
};

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

function jsonResponse(body: unknown, status = 200): Response {
  return new Response(JSON.stringify(body, null, 2), {
    status,
    headers: {
      "Content-Type": "application/json",
      ...corsHeaders,
    },
  });
}

async function resolveBridgeId(gateway_key: string): Promise<string | null> {
  const { data, error } = await supabase
    .from("bridge_gateways")
    .select("bridge_id")
    .eq("gateway_key", gateway_key)
    .limit(1)
    .maybeSingle();

  if (error) {
    console.error("Error resolving bridge_id from gateway_key:", error);
    return null;
  }

  return data?.bridge_id ?? null;
}

serve(async (req: Request): Promise<Response> => {
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

  // 🔐 Simple sovereignty gate
  const headerApiKey = req.headers.get("x-guardian-api-key") ?? "";
  if (!GUARDIAN_API_KEY || headerApiKey !== GUARDIAN_API_KEY) {
    return jsonResponse({ error: "Unauthorized" }, 401);
  }

  let body: TelemetryPayload;
  try {
    body = (await req.json()) as TelemetryPayload;
  } catch (_e) {
    return jsonResponse({ error: "Invalid JSON body" }, 400);
  }

  const {
    gateway_key,
    bridge_id: providedBridgeId,
    agent_id,
    event_type,
    source,
    payload = {},
    metadata = {},
  } = body;

  if (!gateway_key) {
    return jsonResponse(
      { error: "gateway_key is required in request body" },
      400,
    );
  }

  if (!event_type) {
    return jsonResponse(
      { error: "event_type is required in request body" },
      400,
    );
  }

  const effectiveSource = source ?? "unknown_client";
  const effectiveAgentId = agent_id ?? `gateway:${gateway_key}`;

  // 🔁 AUTO-RESOLVE bridge_id IF MISSING
  let bridge_id = providedBridgeId ?? null;

  if (!bridge_id) {
    const resolvedBridgeId = await resolveBridgeId(gateway_key);
    if (!resolvedBridgeId) {
      return jsonResponse(
        {
          error: "Unknown gateway_key",
          gateway_key,
          hint: "Seed bridge_gateways or check spelling",
        },
        404,
      );
    }
    bridge_id = resolvedBridgeId;
  } else {
    // If both provided, validate they match mapping
    const resolvedBridgeId = await resolveBridgeId(gateway_key);
    if (!resolvedBridgeId) {
      return jsonResponse(
        {
          error: "Unknown gateway_key for provided bridge_id",
          gateway_key,
          bridge_id,
        },
        404,
      );
    }

    if (resolvedBridgeId !== bridge_id) {
      return jsonResponse(
        {
          error: "bridge_id does not match mapping for gateway_key",
          gateway_key,
          provided_bridge_id: bridge_id,
          expected_bridge_id: resolvedBridgeId,
        },
        409,
      );
    }
  }

  // 🧾 Insert telemetry event
  const insertPayload = {
    bridge_id,
    gateway_key,
    agent_id: effectiveAgentId,
    event_type,
    source: effectiveSource,
    payload,
    metadata,
  };

  const { data, error } = await supabase
    .from("telemetry_events")
    .insert(insertPayload)
    .select("id, created_at, bridge_id, gateway_key, agent_id, source")
    .single();

  if (error) {
    console.error("Error inserting telemetry event:", error);
    return jsonResponse(
      {
        error: "Failed to insert telemetry event",
        details: error.message ?? error,
      },
      500,
    );
  }

  return jsonResponse(
    {
      status: "ok",
      message: "Telemetry recorded",
      event: data,
    },
    200,
  );
});
