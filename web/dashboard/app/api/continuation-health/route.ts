import { createClient } from '@/lib/supabase/server';
import { NextResponse } from 'next/server';

export async function GET() {
    const supabase = createClient();

    // Fetch realized predictions
    const { data, error } = await supabase
        .from('view_continuation_health')
        .select('*')
        .not('realized_at', 'is', null)
        .order('realized_at', { ascending: false })
        .limit(100);

    if (error) {
        return NextResponse.json({ error: error.message }, { status: 500 });
    }

    // Calculate metrics
    const total = data.length;
    const avgAccuracy = total > 0
        ? data.reduce((acc, row) => acc + row.accuracy_score, 0) / total
        : 0;

    // Guardian Trust Index (Simple heuristic for now)
    const trustIndex = avgAccuracy;

    return NextResponse.json({
        metrics: {
            total_realizations: total,
            average_accuracy: avgAccuracy,
            guardian_trust_index: trustIndex
        },
        recent_events: data.slice(0, 20)
    });
}
