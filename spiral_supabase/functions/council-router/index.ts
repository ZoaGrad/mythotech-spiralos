import { serve } from "https://deno.land/std@0.168.0/http/server.ts";
import { createClient } from "https://esm.sh/@supabase/supabase-js@2.21.0";

const GEMINI_API_KEY = Deno.env.get("GEMINI_API_KEY")!;
const SUPABASE_URL = Deno.env.get("SUPABASE_URL")!;
const SUPABASE_SERVICE_ROLE_KEY = Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!;

const supabase = createClient(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY);

serve(async (req) => {
    try {
        const { claim_id, claim_text: input_text } = await req.json();
        let claim_text = input_text;
        let claim_summary_text = "";

        // 1. Fetch Claim if ID provided
        if (claim_id && !claim_text) {
            const { data, error } = await supabase
                .from("stream_claims")
                .select("*")
                .eq("id", claim_id)
                .single();

            if (error || !data) {
                return new Response(JSON.stringify({ error: "Claim not found" }), { status: 404 });
            }

            const body = data.claim_body;
            claim_text = typeof body === 'string' ? body : (body.content || JSON.stringify(body));
            "weaver": { "coherence_score": 0 - 100, "lore_alignment_grade": "S|A|B|C|F", "flags": "string" },
            "skeptic": { "risk_score": 0 - 100, "attack_vectors": "string", "severity_label": "low|medium|high|critical" },
            "seer": { "impact_score": -100 to 100, "predicted_consequences": "string", "long_tail_risk_note": "string" },
            "chronicler": { "similarity_score": 0 - 100, "references": "string", "conflict_flag": boolean },
            "architect": { "integrity_score": 0 - 100, "affected_subsystems": "string", "breaking_change_flag": boolean },
            "witness": { "ache_score": 0 - 100, "authenticity_note": "string", "exploitative": boolean }
        },
        "aggregate": {
            "reasoning": "Synthesis of the council's views"
        }
    }
    `;

        // 3. Call Gemini
        const llmResponse = await fetch(
            "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key=" + GEMINI_API_KEY,
            {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    contents: [{
                        parts: [{
                            text: systemPrompt + "\n\nCLAIM:\n" + claim_text
                        }]
                    }]
                })
            }
        );

        const llmData = await llmResponse.json();
        const rawText = llmData.candidates?.[0]?.content?.parts?.[0]?.text;

        if (!rawText) {
            throw new Error("LLM returned no content");
        }

        const cleanJson = rawText.replace(/```json / g, "").replace(/```/g, "").trim();
const analysis = JSON.parse(cleanJson);

// 4. Calculate Weights & Verdict
const c = analysis.council;

// Base Confidence: Average of positive scores
const positive_sum = c.judge.truth_score + c.weaver.coherence_score + c.architect.integrity_score;
let base_conf = positive_sum / 300.0;

// Penalties
if (c.skeptic.risk_score > 70) base_conf *= 0.5;
if (c.skeptic.severity_label === 'high' || c.skeptic.severity_label === 'critical') base_conf *= 0.5;
if (c.architect.breaking_change_flag) base_conf *= 0.6;
if (c.chronicler.conflict_flag) base_conf *= 0.8;

// Ache Weight
let ache_weight = 1.0;
if (c.witness.ache_score > 70 && !c.witness.exploitative) {
    ache_weight = 1.0 + ((c.witness.ache_score - 70) / 100.0); // Boost up to 1.3x
}

const sovereign_confidence = Math.min(1.0, Math.max(0.0, base_conf));

let recommended_verdict = "flagged";
if (sovereign_confidence > 0.8 && c.skeptic.risk_score < 40) recommended_verdict = "verified";
if (sovereign_confidence < 0.4 || c.skeptic.risk_score > 80) recommended_verdict = "rejected";

analysis.aggregate.ache_weight = parseFloat(ache_weight.toFixed(2));
analysis.aggregate.sovereign_confidence = parseFloat(sovereign_confidence.toFixed(2));
analysis.aggregate.recommended_verdict = recommended_verdict;

// 5. Log to Database
if (claim_id) {
    await supabase.from("council_judgments").insert({
        claim_id: claim_id,
        claim_summary: analysis.claim_summary,
        council_payload: analysis,
        recommended_verdict: recommended_verdict,
        sovereign_confidence: sovereign_confidence,
        ache_weight: ache_weight
    });
}

return new Response(JSON.stringify(analysis), {
    headers: { "Content-Type": "application/json" },
});

    } catch (e) {
    return new Response(JSON.stringify({ error: "COUNCIL_PARSE_ERROR", details: e.message }), { status: 500, headers: { "Content-Type": "application/json" } });
}
});
