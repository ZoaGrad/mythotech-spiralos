import { serve } from "https://deno.land/std@0.224.0/http/server.ts";
import { createClient } from "jsr:@supabase/supabase-js@2";

const SUPABASE_URL = Deno.env.get("SUPABASE_URL")!;
const SERVICE_ROLE_KEY = Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!;
const STREAM_THRESHOLD = 0.65;

const supabase = createClient(SUPABASE_URL, SERVICE_ROLE_KEY);

const corsHeaders = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Methods": "POST, OPTIONS",
  "Access-Control-Allow-Headers": "authorization, x-client-info, apikey, content-type",
};

function jsonResponse(body: unknown, status = 200): Response {
  return new Response(JSON.stringify(body, null, 2), {
    status,
    headers: { "Content-Type": "application/json", ...corsHeaders },
  });
}

function median(values: number[]): number {
  if (!values.length) return 0;
  const sorted = [...values].sort((a, b) => a - b);
  const mid = Math.floor(sorted.length / 2);
  return sorted.length % 2 === 0 ? (sorted[mid - 1] + sorted[mid]) / 2 : sorted[mid];
}

async function sealVaultEvent(claim_id: string, rho_sigma: number, status: string) {
  const payload = { claim_id, rho_sigma, status };
  const encoder = new TextEncoder();
  const hashBuffer = await crypto.subtle.digest("SHA-256", encoder.encode(JSON.stringify(payload)));
  const hashArray = Array.from(new Uint8Array(hashBuffer));
  const hashHex = hashArray.map((b) => b.toString(16).padStart(2, "0")).join("");

  await supabase.from("vaultnodes").insert({
    node_type: "witness_stream",
    reference_id: claim_id,
    state_hash: hashHex,
    previous_hash: null,
    metadata: payload,
  });
}

serve(async (req) => {
  if (req.method === "OPTIONS") {
    return new Response("ok", { headers: corsHeaders });
  }

  if (req.method !== "POST") {
    return jsonResponse({ error: "Method not allowed" }, 405);
  }

  try {
    const { claim_id } = await req.json();
    if (!claim_id) {
      return jsonResponse({ error: "claim_id is required" }, 400);
    }

    const { data: claim, error: claimError } = await supabase
      .from("witness_claims")
      .select("id, required_witnesses, emp_multiplier")
      .eq("id", claim_id)
      .single();

    if (claimError || !claim) {
      return jsonResponse({ error: claimError?.message || "claim not found" }, 404);
    }

    const { data: assessments, error: assessmentError } = await supabase
      .from("witness_assessments")
      .select("semantic, emotional, contextual")
      .eq("claim_id", claim_id);

    if (assessmentError) {
      return jsonResponse({ error: assessmentError.message }, 400);
    }

    const semanticMedian = median(assessments?.map((a) => Number(a.semantic)) || []);
    const emotionalMedian = median(assessments?.map((a) => Number(a.emotional)) || []);
    const contextualMedian = median(assessments?.map((a) => Number(a.contextual)) || []);

    const rhoSigma = (semanticMedian + emotionalMedian + contextualMedian) / 3;
    const passed = rhoSigma >= STREAM_THRESHOLD;

    await supabase
      .from("witness_claims")
      .update({
        semantic_median: semanticMedian,
        emotional_median: emotionalMedian,
        contextual_median: contextualMedian,
        rho_sigma: rhoSigma,
        status: passed ? "finalized" : "rejected",
        emp_queued: passed,
        updated_at: new Date().toISOString(),
      })
      .eq("id", claim_id);

    if (passed) {
      await supabase.from("emp_mint_queue").upsert({
        claim_id,
        amount: rhoSigma * (claim.emp_multiplier ?? 1),
        rho_sigma: rhoSigma,
        status: "queued",
        metadata: { variant: "STREAM" },
      });
      await sealVaultEvent(claim_id, rhoSigma, "APPROVED");
    } else {
      await sealVaultEvent(claim_id, rhoSigma, "REJECTED");
    }

    return jsonResponse({ status: "finalized", rho_sigma: rhoSigma, emp_queued: passed });
  } catch (error) {
    console.error("Witness finalize error", error);
    return jsonResponse({ error: String(error) }, 500);
  }
});
