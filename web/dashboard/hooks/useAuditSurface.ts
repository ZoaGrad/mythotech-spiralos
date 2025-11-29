import { useState, useEffect } from 'react';
import { createClient } from '@supabase/supabase-js';

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL!;
const supabaseKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!;
const supabase = createClient(supabaseUrl, supabaseKey);

export interface AuditEvent {
    id: string;
    created_at: string;
    event_type: string;
    component: string;
    payload: any;
    phase_lock_hash: string | null;
}

export function useAuditSurface() {
    const [events, setEvents] = useState<AuditEvent[]>([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchEvents = async () => {
            const { data, error } = await supabase
                .from('view_global_audit_surface')
                .select('*');

            if (data) {
                setEvents(data);
            }
            setLoading(false);
        };

        fetchEvents();
        const interval = setInterval(fetchEvents, 3000); // Poll every 3s
        return () => clearInterval(interval);
    }, []);

    return { events, loading };
}
