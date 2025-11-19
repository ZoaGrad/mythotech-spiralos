// SpiralOS Guardian Status Badge ΔΩ.141.3
// Deno Edge Function for shields.io dynamic badge
// Reads latest Guardian heartbeat from scarindex_history

import { serve } from "https://deno.land/std@0.177.0/http/server.ts";

const SUPABASE_URL = Deno.env.get("SUPABASE_URL")!;
const SUPABASE_ANON_KEY = Deno.env.get("SUPABASE_ANON_KEY")!;

serve(async (_req) => {
  try {
    const res = await fetch(`${SUPABASE_URL}/rest/v1/scarindex_history?select=scar_index,timestamp&order=timestamp.desc&limit=1`, {
      headers: {
        apikey: SUPABASE_ANON_KEY,
        Authorization: `Bearer ${SUPABASE_ANON_KEY}`,
      },
    });

    if (!res.ok) throw new Error(`Supabase error: ${res.status}`);
    const data = await res.json();

    if (!Array.isArray(data) || !data.length) {
      return new Response(
        JSON.stringify({
          schemaVersion: 1,
          label: "Guardian",
          message: "No Data",
          color: "inactive",
        }),
        { headers: { "Content-Type": "application/json" } }
      );
    }

    const latest = data[0];
    const scarIndex = Number(latest.scar_index ?? 0);
    let status = "Offline";
    let color = "critical";

    if (scarIndex >= 0.8) {
      status = "Online";
      color = "success";
    } else if (scarIndex >= 0.6) {
      status = "Stable";
      color = "informational";
    } else if (scarIndex >= 0.4) {
      status = "Degraded";
      color = "yellow";
    } else {
      status = "Offline";
      color = "red";
    }

    return new Response(
      JSON.stringify({
        schemaVersion: 1,
        label: "Guardian",
        message: status,
        color,
      }),
      { headers: { "Content-Type": "application/json" } }
    );
  } catch (err) {
    console.error("Guardian badge error:", err);
    return new Response(
      JSON.stringify({
        schemaVersion: 1,
        label: "Guardian",
        message: "Error",
        color: "red",
      }),
      { headers: { "Content-Type": "application/json" } }
    );
  }
});
