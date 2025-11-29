import { useState, useEffect } from 'react';
import { createClient } from '@supabase/supabase-js';

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL!;
const supabaseKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!;
const supabase = createClient(supabaseUrl, supabaseKey);

export interface DriftEntry {
    id: string;
    created_at: string;
    anchor_timestamp: string;
    drift_delta_ms: number | null;
    phase_lock_hash: string | null;
    severity: 'GREEN' | 'YELLOW' | 'RED';
    source: string;
}

export function useTemporalDrift() {
    const [entries, setEntries] = useState<DriftEntry[]>([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchDrift = async () => {
            const { data, error } = await supabase
                .from('view_temporal_drift_status')
                .select('*');

            if (data) {
                setEntries(data);
            }
            setLoading(false);
        };

        fetchDrift();
        const interval = setInterval(fetchDrift, 3000); // Poll every 3s
        return () => clearInterval(interval);
    }, []);

    return { entries, loading };
}
