import { NextRequest, NextResponse } from 'next/server';
import { createClient } from '@supabase/supabase-js';

const supabase = createClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.SUPABASE_SERVICE_ROLE_KEY!
);

export async function GET() {
    try {
        // Fetch latest CCC
        const { data: cccState, error: cccError } = await supabase
            .from('constitutional_cognitive_context')
            .select('*')
            .order('timestamp', { ascending: false })
            .limit(1)
            .single();

        // Fetch proposed amendments
        const { data: amendments, error: amendmentsError } = await supabase
            .from('constitutional_amendments')
            .select('*')
            .eq('status', 'proposed')
            .order('proposed_at', { ascending: true });

        if (cccError && cccError.code !== 'PGRST116') { // PGRST116 = no rows
            console.error('Error fetching CCC:', cccError);
        }
        if (amendmentsError) {
            console.error('Error fetching amendments:', amendmentsError);
        }

        return NextResponse.json({
            cccState: cccState || null,
            amendments: amendments || []
        });
    } catch (error) {
        console.error('Arbitration API error:', error);
        return NextResponse.json(
            { error: 'Failed to fetch arbitration data' },
            { status: 500 }
        );
    }
}

export async function POST(request: NextRequest) {
    try {
        const { amendmentId, decision } = await request.json();

        if (!amendmentId || !decision) {
            return NextResponse.json(
                { error: 'Missing amendmentId or decision' },
                { status: 400 }
            );
        }

        // For now, just update the status - full execution engine comes later
        const { error } = await supabase
            .from('constitutional_amendments')
            .update({
                status: decision === 'ratify' ? 'ratified' : 'rejected',
                decided_at: new Date().toISOString()
            })
            .eq('id', amendmentId);

        if (error) {
            console.error('Error updating amendment:', error);
            return NextResponse.json(
                { error: 'Failed to process arbitration decision' },
                { status: 500 }
            );
        }

        return NextResponse.json({ success: true });
    } catch (error) {
        console.error('Arbitration POST error:', error);
        return NextResponse.json(
            { error: 'Failed to process arbitration request' },
            { status: 500 }
        );
    }
}
