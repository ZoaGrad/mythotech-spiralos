// web/dashboard/app/api/collapse-horizon/route.ts
import { NextResponse } from "next/server";
import { createClient } from "@/lib/supabase/server";

export async function GET() {
    const supabase = createClient();

    const { data, error } = await supabase
        .from("view_collapse_horizon_surface")
        .select("*")
        .order("collapse_risk", { ascending: false })
        .limit(200);

    if (error) {
        return NextResponse.json(
            { message: "Failed to load collapse horizon surface", error },
            { status: 500 },
        );
    }

    return NextResponse.json(data ?? [], { status: 200 });
}
