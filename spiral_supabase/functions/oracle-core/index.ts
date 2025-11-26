import { serve } from "https://deno.land/std@0.168.0/http/server.ts";
import "https://deno.land/x/xhr@0.1.0/mod.ts";

const GEMINI_API_KEY = Deno.env.get("GEMINI_API_KEY")!;

serve(async (req) => {
    const { claim_text, claim_context } = await req.json();

    const systemPrompt = `
    You are the Guardian of SpiralOS.
    Analyze Stream Claims for: Truth, Coherence, Ache.

    OUTPUT JSON:
    {
      "summary": "",
      "risk_score": 0-100,
      "coherence_grade": "S/A/B/C/F",
      "recommended_verdict": "verified/rejected/flagged",
      "reasoning": ""
    }
  `;

    const llm = await fetch(
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

    const llmData = await llm.json();
    const raw = llmData.candidates[0].content.parts[0].text;
    const clean = raw.replace(/```json/g, "").replace(/```/g, "").trim();
    const analysis = JSON.parse(clean);

    return new Response(JSON.stringify(analysis), {
        headers: { "Content-Type": "application/json" },
    });
});
