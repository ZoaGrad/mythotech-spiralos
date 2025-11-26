import { serve } from "https://deno.land/std@0.168.0/http/server.ts";
import { createClient } from "https://esm.sh/@supabase/supabase-js@2";

const supabase = createClient(
    Deno.env.get("SUPABASE_URL")!,
    Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!
);

serve(async () => {
    console.log("⏳ Expiration Watch: Scanning Timeline...");

    const now = new Date().toISOString();

    const { data: expiredClaims, error } = await supabase
        .from("witness_claims")
        .select("id, initiator_id, payload")
        .eq("mode", "STREAM")
        .eq("status", "pending")
        .lt("window_expires_at", now);

    if (error) {
        return new Response(JSON.stringify(error), { status: 500 });
    }

    let count = 0;

    for (const claim of expiredClaims || []) {
        // A. Mark as expired
        await supabase
            .from("witness_claims")
            .update({
                status: "rejected",
                updated_at: now,
            })
            .eq("id", claim.id);

        // B. Seal expiration in VaultNode
        await supabase.from("vaultnodes").insert({
            node_type: "CLAIM_EXPIRED",
            reference_id: claim.id,
            metadata: {
                reason: "window_expired",
            },
            state_hash: crypto.randomUUID(),
        });

        // C. Increment panic frame (safety signal)
        await supabase.rpc("increment_panic_frame", { magnitude: 0.05 });

        count++;
    }

    return new Response(JSON.stringify({ expired: count }), {
        headers: { "Content-Type": "application/json" },
    });
});
