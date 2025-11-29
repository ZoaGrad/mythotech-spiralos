import { createRouteHandlerClient } from '@supabase/auth-helpers-nextjs';
import { cookies } from 'next/headers';
import { NextResponse } from 'next/server';

export const dynamic = 'force-dynamic';

export async function GET() {
    const supabase = createRouteHandlerClient({ cookies });

    // Fetch active constraints
    const constraintsRes = await supabase
        .table('guardian_constraints')
        .select('*')
        .eq('active', true)
        .order('constraint_code', { ascending: true });

    if (constraintsRes.error) {
        return NextResponse.json({ error: constraintsRes.error.message }, { status: 500 });
    }

    // Fetch recent violations (last 24h)
    const violationsRes = await supabase
        .table('constraint_violations')
        .select('*')
        .order('created_at', { ascending: false })
        .limit(50);

    if (violationsRes.error) {
        return NextResponse.json({ error: violationsRes.error.message }, { status: 500 });
    }

    return NextResponse.json({
        constraints: constraintsRes.data,
        violations: violationsRes.data,
    });
}
