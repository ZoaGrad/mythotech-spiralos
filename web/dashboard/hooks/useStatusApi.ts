"use client";

import { useState, useEffect } from 'react';
import { createClient } from '@supabase/supabase-js';

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL || '';
const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY || '';

const supabase = createClient(supabaseUrl, supabaseAnonKey);

export interface SystemStatus {
    lock_status: {
        is_locked: boolean;
        reason: string;
        created_at: string;
        created_by: string;
    };
    latest_event: {
        event_type: string;
        created_at: string;
        payload: any;
    };
    event_stats: {
        total_events: number;
    };
    guardian_vows: Array<{
        subsystem: string;
        active: boolean;
        last_verified_at: string | null;
    }>;
    constitution_state: Record<string, string>;
    safety_state: {
        whitelist_count: number;
        policy_count: number;
    };
    system_version: string;
}

export function useStatusApi() {
    const [status, setStatus] = useState<SystemStatus | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    const fetchStatus = async () => {
        try {
            const { data, error } = await supabase.rpc('fn_status_api');
            if (error) throw error;
            setStatus(data as SystemStatus);
            setError(null);
        } catch (err: any) {
            console.error("Error fetching status:", err);
            setError(err.message);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchStatus();
        const interval = setInterval(fetchStatus, 3000); // 3s cadence
        return () => clearInterval(interval);
    }, []);

    return { status, loading, error, refetch: fetchStatus };
}
