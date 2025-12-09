// GET /scarindex/snapshot
// Computes coherence score from witness events and vault node chain integrity

import { serve } from "https://deno.land/std@0.177.0/http/server.ts";
import { createClient } from "https://esm.sh/@supabase/supabase-js@2";
import { sha256 } from "../lib/spiralos.ts";

const corsHeaders = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Headers": "authorization, x-client-info, apikey, content-type",
};

serve(async (req) => {
  if (req.method === "OPTIONS") {
    return new Response("ok", { headers: corsHeaders });
  }

  try {
    // Auth check
    const authHeader = req.headers.get("Authorization");
    if (!authHeader) {
      return new Response(
        JSON.stringify({ error: "Missing authorization header" }),
        { status: 401, headers: { ...corsHeaders, "Content-Type": "application/json" } }
      );
    }

    // Initialize Supabase client with service key (RLS bypass)
    const supabaseUrl = Deno.env.get("SUPABASE_URL")!;
    const supabaseServiceKey = Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!;
    const supabase = createClient(supabaseUrl, supabaseServiceKey);

    // Step A: Select last 100 witness_events, compute mean resonance
    const { data: witnessEvents, error: witnessError } = await supabase
      .from("witness_events")
      .select("resonance")
      .order("created_at", { ascending: false })
      .limit(100);

    if (witnessError) {
      console.error("Witness events error:", witnessError);
      return new Response(
        JSON.stringify({ error: "Failed to fetch witness events", details: witnessError }),
        { status: 500, headers: { ...corsHeaders, "Content-Type": "application/json" } }
      );
    }

    const resonances = witnessEvents
      ?.map((e: any) => e.resonance || 0)
      .filter((r: number) => !isNaN(r)) || [];
    
    const mean_resonance = resonances.length > 0
      ? resonances.reduce((a: number, b: number) => a + b, 0) / resonances.length
      : 0;

    // Step B: Select last 100 vault_nodes, verify chain integrity (previous_node_hash linkage)
    const { data: vaultNodes, error: vaultError } = await supabase
      .from("vault_nodes")
      .select("id, merkle_root, previous_node_hash")
      .order("created_at", { ascending: false })
      .limit(100);

    if (vaultError) {
      console.error("Vault nodes error:", vaultError);
      return new Response(
        JSON.stringify({ error: "Failed to fetch vault nodes", details: vaultError }),
        { status: 500, headers: { ...corsHeaders, "Content-Type": "application/json" } }
      );
    }

    // Verify chain integrity: check if previous_node_hash links are valid
    let validLinks = 0;
    let totalLinks = 0;
    
    if (vaultNodes && vaultNodes.length > 1) {
      for (let i = 0; i < vaultNodes.length - 1; i++) {
        totalLinks++;
        const currentNode = vaultNodes[i];
        const previousNode = vaultNodes[i + 1];
        
        // In a proper chain, current node's previous_node_hash should match previous node's merkle_root
        if (currentNode.previous_node_hash && currentNode.previous_node_hash === previousNode.merkle_root) {
          validLinks++;
        }
      }
    }

    const chain_integrity_ratio = totalLinks > 0 ? validLinks / totalLinks : 1.0;

    // Step C: coherence_score = mean_resonance * chain_integrity_ratio
    const coherence_score = mean_resonance * chain_integrity_ratio;

    // Prepare snapshot data
    const timestamp = new Date().toISOString();
    const snapshotData = {
      coherence_score,
      timestamp,
      mean_resonance,
      chain_integrity_ratio,
    };
    
    const snapshot_hash = await sha256(JSON.stringify(snapshotData));

    // Step D: Insert scar_index_snapshots row
    const { data: snapshot, error: insertError } = await supabase
      .from("scar_index_snapshots")
      .insert({
        coherence_score,
        timestamp,
        snapshot_hash,
        mean_resonance,
        chain_integrity_ratio,
      })
      .select()
      .single();

    if (insertError) {
      console.error("Insert error:", insertError);
      return new Response(
        JSON.stringify({ error: "Failed to insert snapshot", details: insertError }),
        { status: 500, headers: { ...corsHeaders, "Content-Type": "application/json" } }
      );
    }

    // Step E: Return results
    return new Response(
      JSON.stringify({
        coherence_score,
        timestamp,
        snapshot_hash,
        mean_resonance,
        chain_integrity_ratio,
        witness_count: witnessEvents?.length || 0,
        vault_node_count: vaultNodes?.length || 0,
      }),
      { headers: { ...corsHeaders, "Content-Type": "application/json" } }
    );
  } catch (error) {
    console.error("Error:", error);
    return new Response(
      JSON.stringify({ error: error.message }),
      { status: 400, headers: { ...corsHeaders, "Content-Type": "application/json" } }
    );
  }
});
