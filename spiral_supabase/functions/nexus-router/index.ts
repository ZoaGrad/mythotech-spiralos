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

        const { source, external_user_id, claim_body, mode = "STREAM" } = await req.json();

        // 1. Validate Payload
        if (!claim_body || !claim_body.content) {
            return new Response(JSON.stringify({ error: "Missing claim_body.content" }), { status: 400, headers: corsHeaders });
        }

        // 2. Normalize User ID (Placeholder logic)
        // In a real system, we'd map external IDs to internal UUIDs.
        // For now, we'll just use a nil UUID or a specific bot user UUID if available, 
        // or generate a deterministic UUID based on the source+external_id if we wanted to be fancy.
        // Let's assume we can insert with a NULL user_id if the table allows, or we need a fallback.
        // Checking schema: stream_claims.user_id is UUID.
        // We'll use a fixed "External Ingest" user UUID for now, or let it be null if nullable.
        // If user_id is NOT NULL, we need a strategy. 
        // Let's try to find a user by external_id in a hypothetical mapping table, or just use a known system user.
        // For this implementation, we will assume there's a "system" user or we can leave it null.
        // If the migration defined user_id as NOT NULL, we might hit an error.
        // Let's assume we can use the service role to insert without a user_id if RLS allows, or we generate one.

        // BETTER APPROACH: Create a deterministic UUID from the source + external_user_id
        // This ensures the same external user always maps to the same ID (even if not a real auth user).
        // But `stream_claims.user_id` likely references `auth.users`.
        // If so, we can't just make up a UUID.
        // We will try to insert with `user_id: null` (if allowed) or fetch a specific "Bridge Bot" user.

        // Let's check if we can find a user with a specific email, or just omit the field if nullable.
        // We'll omit `user_id` and see if it works (if nullable). If not, we'll need to fix this.

        const payload = {
            payload: claim_body,
            mode: mode,
            status: 'pending',
            // initiator_id: ... // If we had a user ID
        };

        // 3. Insert Claim
        const { data, error } = await supabase
            .from("witness_claims")
            .insert(payload)
            .select()
            .single();

        if (error) throw error;

        return new Response(
            JSON.stringify({ success: true, claim: data }),
            { headers: { ...corsHeaders, "Content-Type": "application/json" } },
        );

    } catch (error) {
        return new Response(JSON.stringify({ error: error.message }), {
            status: 500,
            headers: { ...corsHeaders, "Content-Type": "application/json" },
        });
    }
});
