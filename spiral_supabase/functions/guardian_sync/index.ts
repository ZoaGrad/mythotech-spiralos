
// deno-lint-ignore-file no-explicit-any
// File: core/guardian/edge/guardian_sync.ts
// Deploy with: supabase functions deploy guardian_sync --project-ref $SUPABASE_PROJECT_REF

import "jsr:@supabase/functions@^2.4.1/edge-runtime.d.ts";

type Metric = {
  label: string;
  value: number | string | null;
};

function statusEmoji(score: number): string {
  if (score >= 1.4) return "🟠"; // hot/high
  if (score >= 0.6) return "🟢"; // healthy
  return "🔴"; // low/unstable
}

function safeNum(n: unknown, fallback = 0): number {
  const x = typeof n === "number" ? n : Number(n);
  return Number.isFinite(x) ? x : fallback;
}

export default async function handler(req: Request): Promise<Response> {
  const supabaseUrl = Deno.env.get("SUPABASE_URL");
  const supabaseKey = Deno.env.get("SUPABASE_SERVICE_ROLE_KEY");
  if (!supabaseUrl || !supabaseKey) {
    return new Response(
      JSON.stringify({ error: "Missing SUPABASE_URL or SUPABASE_SERVICE_ROLE_KEY" }),
      { status: 500 }
    );
  }

  const q = new URL(req.url).searchParams;
  const lookbackHrs = Number(q.get("hours")) || 24;

  // Minimal SQL aggregation via REST
  async function sql<T = any>(query: string): Promise<T[]> {
    const resp = await fetch(`${supabaseUrl}/rest/v1/rpc/raw_sql`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "apikey": supabaseKey,
        "Authorization": `Bearer ${supabaseKey}`,
      },
      body: JSON.stringify({ query }),
    });
    if (!resp.ok) throw new Error(await resp.text());
    return resp.json();
  }

  // NOTE: requires a Postgres function `raw_sql(query text)` that runs read‑only SQL.
  // If you don't have it yet, see docs/guardian/README.md for the safe creation script.

  const since = `NOW() - interval '${lookbackHrs} hours'`;

  const [totals] = await sql(`
    SELECT
      (SELECT COUNT(*) FROM vault_nodes) AS total_nodes,
      (SELECT COUNT(*) FROM ache_events WHERE created_at > ${since}) AS ache_events_recent,
      (SELECT AVG(value) FROM scarindex_calculations WHERE created_at > ${since}) AS scarindex_avg,
      (SELECT value FROM scarindex_calculations ORDER BY created_at DESC LIMIT 1) AS scarindex_latest,
      (SELECT COUNT(*) FROM guardian_alerts WHERE created_at > ${since}) AS alerts_24h
  `);

  const scarAvg = safeNum(totals?.scarindex_avg, NaN);
  const scarLatest = safeNum(totals?.scarindex_latest, NaN);
  const score = Number.isFinite(scarLatest) ? scarLatest : scarAvg;

  const status = {
    timestamp: new Date().toISOString(),
    window_hours: lookbackHrs,
    metrics: [
      { label: "VaultNodes", value: totals?.total_nodes ?? 0 },
      { label: "AcheEvents(lookback)", value: totals?.ache_events_recent ?? 0 },
      { label: "ScarIndex(avg)", value: Number.isFinite(scarAvg) ? Number(scarAvg.toFixed(3)) : null },
      { label: "ScarIndex(latest)", value: Number.isFinite(scarLatest) ? Number(scarLatest.toFixed(3)) : null },
      { label: "Alerts(24h)", value: totals?.alerts_24h ?? 0 },
    ] as Metric[],
    scar_status: statusEmoji(Number.isFinite(score) ? score : 0),
    scar_score: Number.isFinite(score) ? Number(score.toFixed(3)) : null,
  };

  return new Response(JSON.stringify(status), {
    headers: { "Content-Type": "application/json" },
  });
}
