import { serve } from "https://deno.land/std@0.168.0/http/server.ts";
import { createClient } from "https://esm.sh/@supabase/supabase-js@2.21.0";

const SUPABASE_URL = Deno.env.get("SUPABASE_URL")!;
const SUPABASE_SERVICE_ROLE_KEY = Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!;

const supabase = createClient(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY);

serve(async (req) => {
    try {
        // 1. Fetch Current State
        let { data: state, error: stateError } = await supabase
            .from("council_adaptation_state")
            .select("*")
            .eq("profile_name", "default")
            .single();

        if (stateError || !state) {
            // Initialize default if missing
            const defaultState = {
                profile_name: "default",
                judge_weight: 1.0, weaver_weight: 1.0, skeptic_weight: 1.0,
                seer_weight: 1.0, chronicler_weight: 1.0, architect_weight: 1.0, witness_weight: 1.0,
                divergence_sample_window_days: 30,
                total_divergences: 0,
                role_stats: {}
            };
            const { data: newState, error: createError } = await supabase
                .from("council_adaptation_state")
                .insert(defaultState)
                .select()
                .single();

            if (createError) throw createError;
            state = newState;
        }

        // 2. Define Window
        const windowDays = state.divergence_sample_window_days;
        const fromTs = new Date(Date.now() - (windowDays * 24 * 60 * 60 * 1000)).toISOString();

        // 3. Fetch Divergences
        const { data: divergences, error: divError } = await supabase
            .from("council_divergences")
            .select("*")
            .gte("created_at", fromTs)
            .neq("divergence_type", "aligned");

        if (divError) throw divError;

        if (!divergences || divergences.length < 5) { // Min threshold
            return new Response(JSON.stringify({ status: "insufficient_data", count: divergences?.length || 0 }), { headers: { "Content-Type": "application/json" } });
        }

        // 4. Analyze Pressure
        // Simplified Heuristic: 
        // If witness_correct & council_overruled -> Council was too strict. Reduce Skeptic/Architect? Boost Witness?
        // If council_correct & witness_overruled -> Witness was too loose. Boost Skeptic?

        // For this implementation, we will track "wins" per role based on alignment with the "correct" outcome.
        // But we don't have "resolved_outcome" populated automatically yet.
        // So we will rely on the "Law of Friction" assumption: 
        // If human overrules council (council_overruled), we assume human is "right" for now (Sovereignty).
        // So we want to nudge the council towards the human's view.

        const role_deltas = {
            judge: 0, weaver: 0, skeptic: 0, seer: 0, chronicler: 0, architect: 0, witness: 0
        };

        let witness_overrule_count = 0;
        let council_overrule_count = 0;

        for (const div of divergences) {
            if (div.divergence_type === 'council_overruled') {
                // Human verified, Council rejected/flagged.
                // Council was too conservative.
                // Nudge "Risk" roles down, "Ache" roles up.
                role_deltas.skeptic -= 0.05;
                role_deltas.architect -= 0.02;
                role_deltas.witness += 0.05;
                council_overrule_count++;
            } else if (div.divergence_type === 'witness_overruled') {
                // Human rejected, Council verified.
                // Council was too optimistic.
                // Nudge "Risk" roles up.
                role_deltas.skeptic += 0.05;
                role_deltas.judge += 0.02;
                witness_overrule_count++;
            }
        }

        // 5. Apply Damping & Update
        const new_weights = {
            judge: Math.max(0.5, Math.min(2.0, state.judge_weight + (role_deltas.judge * 0.1))), // 0.1 learning rate
            weaver: Math.max(0.5, Math.min(2.0, state.weaver_weight + (role_deltas.weaver * 0.1))),
            skeptic: Math.max(0.5, Math.min(2.0, state.skeptic_weight + (role_deltas.skeptic * 0.1))),
            seer: Math.max(0.5, Math.min(2.0, state.seer_weight + (role_deltas.seer * 0.1))),
            chronicler: Math.max(0.5, Math.min(2.0, state.chronicler_weight + (role_deltas.chronicler * 0.1))),
            architect: Math.max(0.5, Math.min(2.0, state.architect_weight + (role_deltas.architect * 0.1))),
            witness: Math.max(0.5, Math.min(2.0, state.witness_weight + (role_deltas.witness * 0.1))),
        };

        // 6. Save New State
        const { data: updated, error: updateError } = await supabase
            .from("council_adaptation_state")
            .update({
                ...new_weights, # Spread new weights
            total_divergences: divergences.length,
                witness_overrule_count: witness_overrule_count,
                council_overrule_count: council_overrule_count,
                version: state.version + 1,
                last_recomputed_at: new Date().toISOString()
            })
            .eq("id", state.id)
            .select()
            .single();

        if (updateError) throw updateError;

        return new Response(JSON.stringify({
            status: "ok",
            profile_name: "default",
            version: updated.version,
            weights: new_weights,
            sample: {
                window_days: windowDays,
                total_divergences: divergences.length,
                used_for_update: true
            }
        }), { headers: { "Content-Type": "application/json" } });

    } catch (e) {
        return new Response(JSON.stringify({ error: e.message }), { status: 500, headers: { "Content-Type": "application/json" } });
    }
});
