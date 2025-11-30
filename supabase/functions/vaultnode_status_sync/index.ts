import { serve } from "https://deno.land/std@0.168.0/http/server.ts"
import { createClient } from "https://esm.sh/@supabase/supabase-js@2"

serve(async (req) => {
    try {
        const supabase = createClient(
            Deno.env.get("SUPABASE_URL") ?? "",
            Deno.env.get("SUPABASE_SERVICE_ROLE_KEY") ?? ""
        )

        const { node_id, status, metadata } = await req.json()

        // Update Registry
        const { data, error } = await supabase
            .from("vaultnode_registry")
            .upsert({
                node_id,
                status,
                metadata,
                updated_at: new Date().toISOString()
            })
            .select()
            .single()

        if (error) throw error

        return new Response(
            JSON.stringify({ success: true, node: data }),
            { headers: { "Content-Type": "application/json" } }
        )
    } catch (error) {
        return new Response(
            JSON.stringify({ success: false, error: error.message }),
            { status: 400, headers: { "Content-Type": "application/json" } }
        )
    }
})
