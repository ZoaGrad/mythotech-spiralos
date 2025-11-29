// web/dashboard/app/api/future-lattice/route.ts
import { NextResponse } from "next/server";
import { createClient } from "@/lib/supabase/server";

export async function GET() {
    const supabase = createClient();

    const { data, error } = await supabase
        .from("view_future_lattice_surface")
        .select("*")
        .order("collapse_probability", { ascending: false })
        .limit(200);

    if (error) {
        return NextResponse.json(
            { message: "Failed to load future lattice surface", error },
            { status: 500 },
        );
    }

    return NextResponse.json(data ?? [], { status: 200 });
}
