import { NextResponse } from "next/server";
import { createClient } from "@/lib/supabase/server";

export async function GET() {
    const supabase = createClient();

    const { data: telemetry, error: telemetryError } = await supabase
        .from("guardian_telemetry_events")
        .select("afr_flux_vector_norm, afr_adjustment_imperative, created_at")
        .order("created_at", { ascending: false })
        .limit(1);

    const { data: adjustments, error: adjustmentsError } = await supabase
        .from("system_events")
        .select("*")
        .eq("event_type", "afr_adjustment")
        .order("created_at", { ascending: false })
        .limit(10);

    if (telemetryError || adjustmentsError) {
        return NextResponse.json(
            { message: "Failed to load AFR state", error: telemetryError || adjustmentsError },
            { status: 500 },
        );
    }

    return NextResponse.json({
        fluxVectorNorm: telemetry?.[0]?.afr_flux_vector_norm || 0,
        adjustmentImperative: telemetry?.[0]?.afr_adjustment_imperative || 0,
        recentAdjustments: adjustments || []
    }, { status: 200 });
}
