// web/dashboard/app/api/paradox-risk/route.ts
import { NextResponse } from "next/server";
import { createClient } from "@/lib/supabase/server";

export async function GET() {
    const supabase = createClient();

    const { data, error } = await supabase
        .from("view_paradox_risk_surface")
        .select("*")
        .order("paradox_risk", { ascending: false })
        .limit(200);

    if (error) {
        return NextResponse.json(
            { message: "Failed to load paradox risk surface", error },
            { status: 500 },
        );
    }

    return NextResponse.json(data ?? [], { status: 200 });
}
