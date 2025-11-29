import { createClient } from '@/lib/supabase/server';
import { NextResponse } from 'next/server';

export async function GET() {
    const supabase = createClient();

    const { data, error } = await supabase
        .from('future_chain')
        .select(`
      *,
      integration_lattice (
        lattice_state,
        collapse_probability
      )
    `)
        .order('created_at', { ascending: false })
        .limit(50);

    if (error) {
        return NextResponse.json({ error: error.message }, { status: 500 });
    }

    return NextResponse.json(data);
}
