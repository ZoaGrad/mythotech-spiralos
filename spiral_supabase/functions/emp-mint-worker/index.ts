import { serve } from "https://deno.land/std@0.168.0/http/server.ts";
import { createClient } from "https://esm.sh/@supabase/supabase-js@2";

// Initialize Supabase
const supabaseUrl = Deno.env.get("SUPABASE_URL")!;
const supabaseKey = Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!;
const supabase = createClient(supabaseUrl, supabaseKey);

serve(async () => {
  console.log("⚡ EMP Mint Worker: Pulse Initiated");

  // Pull Pending Items
  const { data: queueItems, error: queueError } = await supabase
    .from("emp_mint_queue")
    .select("*")
    .eq("status", "queued")
    .limit(50);

  if (queueError) {
    return new Response(JSON.stringify(queueError), { status: 500 });
  }

  if (!queueItems || queueItems.length === 0) {
    return new Response("No queued mints. Pulse resting.", { status: 200 });
  }

  let minted = 0;

  for (const item of queueItems) {
    // 1. Mint EMP
    const { error: ledgerError } = await supabase.from("emp_ledger").insert({
      user_id: item.user_id ?? item.recipient_id,
      claim_id: item.claim_id,
      amount: item.amount,
      rho_sigma: item.rho_sigma,
      transferable: false,
      origin_variant: item.metadata?.variant ?? "STREAM",
      metadata: item.metadata ?? {},
    });

    if (ledgerError) {
      console.error("Ledger mint error:", ledgerError);
      continue;
    }

    // 2. Seal VaultNode
    await supabase.from("vaultnodes").insert({
      node_type: "EMP_MINT",
      reference_id: item.claim_id,
      state_hash: crypto.randomUUID(),
      metadata: {
        amount: item.amount,
        user_id: item.user_id,
        rho_sigma: item.rho_sigma,
      },
    });

    // 3. Mark as completed
    await supabase
      .from("emp_mint_queue")
      .update({ status: "minted", processed_at: new Date().toISOString() })
      .eq("id", item.id);

    minted++;
  }

  return new Response(JSON.stringify({ minted }), {
    headers: { "Content-Type": "application/json" },
  });
});
