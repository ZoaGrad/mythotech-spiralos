import { serve } from "https://deno.land/std@0.224.0/http/server.ts";
import { createClient } from "jsr:@supabase/supabase-js@2";

const SUPABASE_URL = Deno.env.get("SUPABASE_URL")!;
const SERVICE_ROLE_KEY = Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!;
const FUNCTIONS_URL = Deno.env.get("SUPABASE_FUNCTIONS_URL") || `${SUPABASE_URL.replace(/\/$/, "")}/functions/v1`;

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

async function ensureQueueEntry(claim_id: string) {
  await supabase.from("emp_mint_queue").upsert({ claim_id, status: "pending" });
}

async function triggerAutoFinalize(claim_id: string) {
  try {
    const response = await fetch(`${FUNCTIONS_URL}/witness-finalize`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        apikey: SERVICE_ROLE_KEY,
        Authorization: `Bearer ${SERVICE_ROLE_KEY}`,
      },
      body: JSON.stringify({ claim_id }),
    });
    const data = await response.json();
    return { ok: response.ok, data };
  } catch (error) {
    console.error("Auto-finalize error", error);
    return { ok: false, data: { error: String(error) } };
  }
}

serve(async (req) => {
  if (req.method === "OPTIONS") {
    return new Response("ok", { headers: corsHeaders });
  }

  if (req.method !== "POST") {
    return jsonResponse({ error: "Method not allowed" }, 405);
  }

  try {
    const payload = await req.json();
    const { claim_id, initiator_id, target_id, witness_id, semantic, emotional, contextual, notes, parent_claim_id, payload: claim_payload } = payload;

    if (!claim_id) {
      if (!initiator_id || !claim_payload) {
        return jsonResponse({ error: "initiator_id and payload are required" }, 400);
      }

      const { data, error } = await supabase
        .from("witness_claims")
        .insert({
          initiator_id,
          target_id: target_id ?? null,
          mode: "STREAM",
          payload: claim_payload,
          required_witnesses: 3,
          decay_rate: 0.003,
          emp_multiplier: 1.0,
        })
        .select("id")
        .single();

      if (error) {
        return jsonResponse({ error: error.message }, 400);
      }

      const newClaimId = data.id as string;
      await supabase.from("ancestry_edges").insert({
        parent_claim: parent_claim_id ?? newClaimId,
        child_claim: newClaimId,
        decay_rate: 0.003,
      });

      await ensureQueueEntry(newClaimId);

      return jsonResponse({ status: "claim_recorded", claim_id: newClaimId });
    }

    if (!witness_id || semantic === undefined || emotional === undefined || contextual === undefined) {
      return jsonResponse({ error: "witness_id, semantic, emotional, contextual are required" }, 400);
    }

    const rhoSigma = (Number(semantic) + Number(emotional) + Number(contextual)) / 3;

    const { error: assessmentError } = await supabase.from("witness_assessments").insert({
      claim_id,
      witness_id,
      semantic,
      emotional,
      contextual,
      rho_sigma: rhoSigma,
      notes: notes ?? null,
    });

    if (assessmentError) {
      return jsonResponse({ error: assessmentError.message }, 400);
    }

    await supabase
      .from("witness_claims")
      .update({ status: "assessing", updated_at: new Date().toISOString() })
      .eq("id", claim_id);

    await ensureQueueEntry(claim_id);

    const { data: claimRow } = await supabase
      .from("witness_claims")
      .select("required_witnesses")
      .eq("id", claim_id)
      .maybeSingle();

    const required = claimRow?.required_witnesses ?? 3;

    const { count } = await supabase
      .from("witness_assessments")
      .select("id", { count: "exact", head: true })
      .eq("claim_id", claim_id);

    let finalizeResult: Record<string, unknown> | null = null;
    if (typeof count === "number" && count >= required) {
      const finalize = await triggerAutoFinalize(claim_id);
      finalizeResult = finalize.data;
    }

    return jsonResponse({
      status: "assessment_recorded",
      claim_id,
      assessments: count ?? 1,
      finalized: finalizeResult,
    });
  } catch (error) {
    console.error("Witness event error", error);
    return jsonResponse({ error: String(error) }, 500);
  }
});
