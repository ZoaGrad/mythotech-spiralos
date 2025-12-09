// POST /scarloop/ingest
// Computes scarloop coherence delta and mints ScarCoin.

import { serve } from "https://deno.land/std@0.177.0/http/server.ts";
import { createClient } from "https://esm.sh/@supabase/supabase-js@2";
import { z } from "https://deno.land/x/zod@v3.21.4/mod.ts";
import { sha256, floatFromHash } from "../lib/spiralos.ts";

const corsHeaders = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Headers": "authorization, x-client-info, apikey, content-type",
};

const RequestSchema = z.object({
  ache_description: z.string(),
  context: z.object({}).optional(),
});

serve(async (req) => {
  if (req.method === "OPTIONS") {
    return new Response("ok", { headers: corsHeaders });
  }

  try {
    // Auth check
    const authHeader = req.headers.get("Authorization");
    if (!authHeader) {
      return new Response(
        JSON.stringify({ error: "Missing authorization header" }),
        { status: 401, headers: { ...corsHeaders, "Content-Type": "application/json" } }
      );
    }

    // Validate request
    const body = await req.json();
    const { ache_description, context } = RequestSchema.parse(body);

    // Step A: Compute H = sha256(ache_description) → ache_before (0-1 float from first 8 hex chars / 0xffffffff)
    const hash = await sha256(ache_description);
    const ache_before = floatFromHash(hash);

    // Step B: Call internal "cognitive_organs" (mock: ache_after = ache_before * 0.85 + Math.random()*0.05)
    const ache_after = ache_before * 0.85 + Math.random() * 0.05;

    // Step C: coherence_delta = ache_before - ache_after
    const coherence_delta = ache_before - ache_after;

    // Step D: scarcoin_minted = Math.max(0, coherence_delta * 1000)
    const scarcoin_minted = Math.max(0, coherence_delta * 1000);

    // Prepare payload
    const payload = {
      ache_description,
      context: context || {},
      ache_before,
      ache_after,
      coherence_delta,
      timestamp: new Date().toISOString(),
    };

    const merkle_root = await sha256(JSON.stringify(payload));

    // Initialize Supabase client with service key (RLS bypass)
    const supabaseUrl = Deno.env.get("SUPABASE_URL")!;
    const supabaseServiceKey = Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!;
    const supabase = createClient(supabaseUrl, supabaseServiceKey);

    // Step E: Insert vault_nodes row
    const { data: node, error: insertError } = await supabase
      .from("vault_nodes")
      .insert({
        content_type: "ache",
        content_ref: payload,
        merkle_root,
        signature: "dummy",
      })
      .select()
      .single();

    if (insertError) {
      console.error("Insert error:", insertError);
      return new Response(
        JSON.stringify({ error: "Failed to insert vault node", details: insertError }),
        { status: 500, headers: { ...corsHeaders, "Content-Type": "application/json" } }
      );
    }

    // Step F: Return results
    return new Response(
      JSON.stringify({
        ache_before,
        ache_after,
        coherence_delta,
        scarcoin_minted,
        node_id: node.id,
      }),
      { headers: { ...corsHeaders, "Content-Type": "application/json" } }
    );
  } catch (error) {
    console.error("Error:", error);
    return new Response(
      JSON.stringify({ error: error.message }),
      { status: 400, headers: { ...corsHeaders, "Content-Type": "application/json" } }
    );
  }
});
