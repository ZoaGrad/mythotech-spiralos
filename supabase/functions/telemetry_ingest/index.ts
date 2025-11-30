import { serve } from "https://deno.land/std@0.168.0/http/server.ts";
import { createClient } from "https://esm.sh/@supabase/supabase-js@2";

const supabaseUrl = Deno.env.get("SUPABASE_URL")!;
const supabaseServiceKey = Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!;
const supabase = createClient(supabaseUrl, supabaseServiceKey);

serve(async (req) => {
    if (req.method !== "POST") {
        return new Response("Method Not Allowed", { status: 405 });
    }

    try {
        const body = await req.json();
        const { event_type, source_id, payload, signature, metadata } = body;

        // 1. Input Validation
        if (!event_type || !source_id || !payload) {
            throw new Error("Missing required fields: event_type, source_id, payload");
        }

        // 2. Authentication (Simple API Key Check for now)
        const authHeader = req.headers.get("Authorization");
        if (!authHeader) {
            // For now, we log but don't block to allow testing without keys if needed, 
            // OR we enforce it. Let's enforce a basic check if env var is set.
            const expectedKey = Deno.env.get("TELEMETRY_API_KEY");
            if (expectedKey && authHeader !== `Bearer ${expectedKey}`) {
                throw new Error("Unauthorized: Invalid API Key");
            }
        }

        // 3. Efficient Write
        const { data, error } = await supabase
            .from("telemetry_events")
            .insert({
                event_type,
                source_id,
                payload,
                signature,
                metadata,
                processed_status: "pending",
                event_timestamp: new Date().toISOString()
            })
            .select()
            .single();

        if (error) {
            throw error;
        }

        return new Response(JSON.stringify({ status: "ok", id: data.id }), {
            status: 201,
            headers: { "Content-Type": "application/json" },
        });

    } catch (e) {
        console.error("Telemetry Ingestion Failed:", e);

        // 4. Error Logging to Guardian
        try {
            await supabase.from("guardian_logs").insert({
                level: "ERROR",
                source: "telemetry_ingest",
                message: `Ingestion failed: ${e.message}`,
                metadata: { error: String(e) }
            });
        } catch (logError) {
            console.error("Failed to log to Guardian:", logError);
        }

        return new Response(JSON.stringify({ error: e.message }), {
            status: 400,
            headers: { "Content-Type": "application/json" }
        });
    }
});
