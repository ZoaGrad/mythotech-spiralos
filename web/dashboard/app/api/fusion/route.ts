import { supabase } from "@/lib/supabase";

export async function GET() {
    const { data, error } = await supabase
        .from("view_mesh_temporal_fusion")
        .select("*")
        .order("created_at", { ascending: false });

    return new Response(JSON.stringify(error || data), {
        status: error ? 500 : 200,
    });
}
