// web/dashboard/app/api/guardian-actions/route.ts
import { NextResponse } from "next/server";
import { createClient } from "@/lib/supabase/server";

export async function GET() {
    const supabase = createClient();

    const { data, error } = await supabase
        .from("guardian_action_events")
        .select("*")
        .order("created_at", { ascending: false })
        .limit(200);

    if (error) {
        return NextResponse.json(
            { message: "Failed to load guardian actions", error },
            { status: 500 },
        );
    }

    return NextResponse.json(data ?? [], { status: 200 });
}
