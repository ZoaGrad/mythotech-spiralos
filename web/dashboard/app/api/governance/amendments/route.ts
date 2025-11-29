import { createRouteHandlerClient } from '@supabase/auth-helpers-nextjs';
import { cookies } from 'next/headers';
import { NextResponse } from 'next/server';

export const dynamic = 'force-dynamic';

export async function GET() {
    const supabase = createRouteHandlerClient({ cookies });

    const { data, error } = await supabase
        .table('governance_amendments')
        .select('*')
        .order('submitted_at', { ascending: false });

    if (error) {
        return NextResponse.json({ error: error.message }, { status: 500 });
    }

    return NextResponse.json(data);
}

export async function POST(request: Request) {
    const supabase = createRouteHandlerClient({ cookies });
    const body = await request.json();

    const { title, proposal, rationale } = body;

    // Get next amendment number
    const { count } = await supabase.table('governance_amendments').select('*', { count: 'exact', head: true });
    const nextNum = (count || 0) + 1;

    const { data, error } = await supabase
        .table('governance_amendments')
        .insert({
            amendment_number: nextNum,
            title,
            proposal,
            rationale,
            status: 'draft'
        })
        .select()
        .single();

    if (error) {
        return NextResponse.json({ error: error.message }, { status: 500 });
    }

    return NextResponse.json(data);
}
