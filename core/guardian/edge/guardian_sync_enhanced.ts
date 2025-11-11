
// deno-lint-ignore-file no-explicit-any
// File: core/guardian/edge/guardian_sync_enhanced.ts
// Enhanced Guardian Edge Function with comprehensive metrics
// Deploy with: supabase functions deploy guardian_sync --project-ref $SUPABASE_PROJECT_REF

import "jsr:@supabase/functions@^2.4.1/edge-runtime.d.ts";
import { createClient } from 'jsr:@supabase/supabase-js@2';

type Metric = {
  label: string;
  value: number | string | null;
};

type CoherenceComponents = {
  narrative: number;
  social: number;
  economic: number;
  technical: number;
};

type PIDState = {
  current_scarindex: number;
  target_scarindex: number;
  error: number;
  integral: number;
  derivative: number;
  guidance_scale: number;
};

type GuardianStatus = {
  timestamp: string;
  window_hours: number;
  metrics: Metric[];
  coherence_components: CoherenceComponents | null;
  pid_state: PIDState | null;
  scar_status: string;
  scar_score: number | null;
  panic_frames: number;
  trend: string | null;
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
      { status: 500, headers: { "Content-Type": "application/json" } }
    );
  }

  const supabase = createClient(supabaseUrl, supabaseKey);
  const q = new URL(req.url).searchParams;
  const lookbackHrs = Number(q.get("hours")) || 24;
  const includeComponents = q.get("components") !== "false";
  const includePID = q.get("pid") !== "false";
  const includeTrend = q.get("trend") !== "false";

  try {
    // Fetch basic metrics
    const { data: dashboard, error: dashError } = await supabase
      .from('guardian_dashboard')
      .select('*')
      .single();

    if (dashError) {
      console.error("Dashboard error:", dashError);
    }

    // Fetch recent ScarIndex calculations
    const { data: recentCalcs, error: calcError } = await supabase
      .from('scarindex_calculations')
      .select('value, c_narrative, c_social, c_economic, c_technical, created_at')
      .gte('created_at', new Date(Date.now() - lookbackHrs * 60 * 60 * 1000).toISOString())
      .order('created_at', { ascending: false });

    if (calcError) {
      console.error("Calculations error:", calcError);
    }

    // Calculate average ScarIndex
    const scarAvg = recentCalcs && recentCalcs.length > 0
      ? recentCalcs.reduce((sum, c) => sum + (c.value || 0), 0) / recentCalcs.length
      : null;

    // Get latest calculation
    const latestCalc = recentCalcs && recentCalcs.length > 0 ? recentCalcs[0] : null;
    const scarLatest = latestCalc?.value || null;

    // Get coherence components from latest calculation
    let coherenceComponents: CoherenceComponents | null = null;
    if (includeComponents && latestCalc) {
      coherenceComponents = {
        narrative: safeNum(latestCalc.c_narrative),
        social: safeNum(latestCalc.c_social),
        economic: safeNum(latestCalc.c_economic),
        technical: safeNum(latestCalc.c_technical),
      };
    }

    // Get PID controller state
    let pidState: PIDState | null = null;
    if (includePID) {
      const { data: pidData, error: pidError } = await supabase
        .from('pid_controller_state')
        .select('*')
        .order('created_at', { ascending: false })
        .limit(1)
        .single();

      if (!pidError && pidData) {
        pidState = {
          current_scarindex: safeNum(pidData.current_scarindex),
          target_scarindex: safeNum(pidData.target_scarindex, 0.70),
          error: safeNum(pidData.error),
          integral: safeNum(pidData.integral),
          derivative: safeNum(pidData.derivative),
          guidance_scale: safeNum(pidData.guidance_scale, 1.0),
        };
      }
    }

    // Get panic frames count
    const { count: panicCount, error: panicError } = await supabase
      .from('panic_frames')
      .select('*', { count: 'exact', head: true })
      .eq('status', 'ACTIVE');

    if (panicError) {
      console.error("Panic frames error:", panicError);
    }

    // Get trend if requested
    let trend: string | null = null;
    if (includeTrend) {
      const { data: trendData, error: trendError } = await supabase
        .from('coherence_trends')
        .select('trend_direction')
        .order('created_at', { ascending: false })
        .limit(1)
        .single();

      if (!trendError && trendData) {
        trend = trendData.trend_direction;
      }
    }

    // Get Ache events count
    const { count: acheCount, error: acheError } = await supabase
      .from('ache_events')
      .select('*', { count: 'exact', head: true })
      .gte('created_at', new Date(Date.now() - lookbackHrs * 60 * 60 * 1000).toISOString());

    if (acheError) {
      console.error("Ache events error:", acheError);
    }

    // Get alerts count
    const { count: alertsCount, error: alertsError } = await supabase
      .from('guardian_alerts')
      .select('*', { count: 'exact', head: true })
      .gte('created_at', new Date(Date.now() - 24 * 60 * 60 * 1000).toISOString());

    if (alertsError) {
      console.error("Alerts error:", alertsError);
    }

    // Determine score for status
    const score = scarLatest !== null ? scarLatest : (scarAvg !== null ? scarAvg : 0);

    // Build response
    const status: GuardianStatus = {
      timestamp: new Date().toISOString(),
      window_hours: lookbackHrs,
      metrics: [
        { label: "VaultNodes", value: dashboard?.total_vaultnodes ?? 0 },
        { label: "AcheEvents(lookback)", value: acheCount ?? 0 },
        { label: "ScarIndex(avg)", value: scarAvg !== null ? Number(scarAvg.toFixed(3)) : null },
        { label: "ScarIndex(latest)", value: scarLatest !== null ? Number(scarLatest.toFixed(3)) : null },
        { label: "Alerts(24h)", value: alertsCount ?? 0 },
        { label: "ActivePanicFrames", value: panicCount ?? 0 },
      ] as Metric[],
      coherence_components: coherenceComponents,
      pid_state: pidState,
      scar_status: statusEmoji(score),
      scar_score: score !== 0 ? Number(score.toFixed(3)) : null,
      panic_frames: panicCount ?? 0,
      trend: trend,
    };

    // Log heartbeat to database
    const { error: logError } = await supabase
      .from('guardian_heartbeats')
      .insert({
        scar_score: status.scar_score,
        scar_status: status.scar_status,
        metrics: status.metrics,
        coherence_components: coherenceComponents,
        pid_state: pidState,
        window_hours: lookbackHrs,
      });

    if (logError) {
      console.error("Failed to log heartbeat:", logError);
    }

    return new Response(JSON.stringify(status), {
      headers: { 
        "Content-Type": "application/json",
        "Access-Control-Allow-Origin": "*",
      },
    });

  } catch (error) {
    console.error("Handler error:", error);
    return new Response(
      JSON.stringify({ 
        error: "Internal server error", 
        details: error instanceof Error ? error.message : String(error) 
      }),
      { 
        status: 500,
        headers: { "Content-Type": "application/json" }
      }
    );
  }
}
