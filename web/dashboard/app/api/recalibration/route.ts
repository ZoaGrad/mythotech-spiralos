import { createRouteHandlerClient } from '@supabase/auth-helpers-nextjs';
import { cookies } from 'next/headers';
import { NextResponse } from 'next/server';

export const dynamic = 'force-dynamic';

export async function GET(request: Request) {
    try {
        const supabase = createRouteHandlerClient({ cookies });

        const { searchParams } = new URL(request.url);
        const limit = parseInt(searchParams.get('limit') || '200');

        const { data, error } = await supabase
            .table('guardian_recalibration_log')
            .select('*')
            .order('recalibrated_at', { ascending: false })
            .limit(limit);

        if (error) {
            console.error('Error fetching recalibration log:', error);
            return NextResponse.json({ error: error.message }, { status: 500 });
        }

        return NextResponse.json(data);
    } catch (e) {
        console.error('Unexpected error:', e);
        return NextResponse.json({ error: 'Internal Server Error' }, { status: 500 });
    }
}
