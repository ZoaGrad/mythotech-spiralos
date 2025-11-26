import { serve } from "https://deno.land/std@0.168.0/http/server.ts";
import { createClient } from "https://esm.sh/@supabase/supabase-js@2";

const corsHeaders = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Headers": "authorization, x-client-info, apikey, content-type",
};

serve(async (req) => {
    if (req.method === "OPTIONS") {
        return new Response("ok", { headers: corsHeaders });
    }

    try {
        const supabaseUrl = Deno.env.get("SUPABASE_URL")!;
        const supabaseKey = Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!;
        const supabase = createClient(supabaseUrl, supabaseKey);

        // 1. Determine Time Window
        // Check last reflection date
        const { data: lastReflections, error: refError } = await supabase
            .from("system_reflections")
            .select("created_at")
            .order("created_at", { ascending: false })
            .limit(1);

        let startTime = new Date(0).toISOString(); // Default to beginning of time
        if (lastReflections && lastReflections.length > 0) {
            startTime = lastReflections[0].created_at;
        }

        // 2. Fetch Divergences since last reflection
        const { data: divergences, error: divError } = await supabase
            .from("council_divergences")
            .select("*")
            .gt("created_at", startTime);

        if (divError) throw divError;

        const divergenceCount = divergences.length;
        const patterns: any = {
            total_divergences: divergenceCount,
            by_type: {},
            overruled_minds: []
        };

        // 3. Analyze Patterns (Heuristic)
        // Simple analysis: Count divergence types and identify if specific minds were consistently "wrong"
        // (i.e., their individual score disagreed with the human verdict)

        if (divergences.length > 0) {
            divergences.forEach(div => {
                // Count types
                patterns.by_type[div.divergence_type] = (patterns.by_type[div.divergence_type] || 0) + 1;
            });
        }

        // 4. Generate Proposed Adjustments
        // Law of Inertia: Only propose changes if significant divergence
        let proposedAdjustments: any = {};

        if (divergenceCount >= 3) {
            // Very basic logic for now: 
            // If mostly "council_overruled" (Human verified, Council rejected), weaken Skeptic slightly?
            // If mostly "witness_overruled" (Human rejected, Council verified), strengthen Skeptic?

            const councilOverruled = patterns.by_type['council_overruled'] || 0;
            const witnessOverruled = patterns.by_type['witness_overruled'] || 0;

            if (councilOverruled > witnessOverruled) {
                // Council was too strict/paranoid.
                proposedAdjustments = { skeptic_weight_delta: -0.05, weaver_weight_delta: 0.05 };
            } else if (witnessOverruled > councilOverruled) {
                // Council was too loose/gullible.
                proposedAdjustments = { skeptic_weight_delta: 0.05, weaver_weight_delta: -0.05 };
            }
        }

        // 5. Insert Reflection
        const reflectionPayload = {
            divergence_count: divergenceCount,
            patterns: patterns,
            proposed_adjustments: proposedAdjustments
        };

        const { data: reflection, error: insError } = await supabase
            .from("system_reflections")
            .insert(reflectionPayload)
            .select()
            .single();

        if (insError) throw insError;

        // 6. Create Governance Proposal (Dawn Cycle)
        // Fetch current weights
        let currentWeights = {
            judge: 1.0, weaver: 1.0, skeptic: 1.0, seer: 1.0, chronicler: 1.0, architect: 1.0, witness: 1.0
        };

        const { data: weightState } = await supabase
            .from("council_adaptation_state")
            .select("*")
            .eq("profile_name", "default")
            .single();

        if (weightState) {
            currentWeights = {
                judge: weightState.judge_weight,
                weaver: weightState.weaver_weight,
                skeptic: weightState.skeptic_weight,
                seer: weightState.seer_weight,
                chronicler: weightState.chronicler_weight,
                architect: weightState.architect_weight,
                witness: weightState.witness_weight
            };
        }

        // Apply deltas
        const newWeights = { ...currentWeights };
        if (proposedAdjustments.skeptic_weight_delta) newWeights.skeptic += proposedAdjustments.skeptic_weight_delta;
        if (proposedAdjustments.weaver_weight_delta) newWeights.weaver += proposedAdjustments.weaver_weight_delta;
        // ... map other deltas if we add them later

        // Clamp weights
        for (const key in newWeights) {
            // @ts-ignore
            newWeights[key] = Math.max(0.5, Math.min(1.5, newWeights[key]));
        }

        // Insert Proposal
        const { error: propError } = await supabase
            .from("governance_proposals")
            .insert({
                reflection_id: reflection.id,
                proposed_weights: newWeights,
                status: 'pending'
            });

        if (propError) throw propError;

        return new Response(
            JSON.stringify({ success: true, reflection: reflection }),
            { headers: { ...corsHeaders, "Content-Type": "application/json" } },
        );

    } catch (error) {
        return new Response(JSON.stringify({ error: error.message }), {
            status: 500,
            headers: { ...corsHeaders, "Content-Type": "application/json" },
        });
    }
});
