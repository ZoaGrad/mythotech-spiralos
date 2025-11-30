// supabase/functions/telemetry_ingest/index.ts
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

        const { event_type, source, payload } = body;

        const { error } = await supabase
            .from("telemetry_events")
            .insert({
                event_type,
                source,
                payload,
            });

        if (error) {
            console.error("Insert error:", error);
            return new Response("Error", { status: 500 });
        }

        return new Response(JSON.stringify({ status: "ok" }), {
            status: 200,
            headers: { "Content-Type": "application/json" },
        });
    } catch (e) {
        console.error("Bad telemetry:", e);
        return new Response("Bad Request", { status: 400 });
    }
});
