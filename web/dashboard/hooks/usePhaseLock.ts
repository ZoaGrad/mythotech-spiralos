"use client";

import { useCallback, useState } from "react";
import { createClient, SupabaseClient } from "@supabase/supabase-js";

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL!;
const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!;

// You can swap this for a shared client if you already have one.
const supabase: SupabaseClient = createClient(supabaseUrl, supabaseAnonKey);

export interface PhaseLockResult {
    passed: boolean;
    expected_root_hash: string | null;
    actual_root_hash: string;
    checkpoint_id: string | null;
    log_id: string;
    status_snapshot: any;
}

interface UsePhaseLockState {
    loading: boolean;
    error: string | null;
    result: PhaseLockResult | null;
}

export function usePhaseLock() {
    const [state, setState] = useState<UsePhaseLockState>({
        loading: false,
        error: null,
        result: null,
    });

    const runCheck = useCallback(async () => {
        setState(prev => ({ ...prev, loading: true, error: null }));

        const { data, error } = await supabase.rpc("fn_verify_phase_lock", {});

        if (error) {
            console.error("[PhaseLock] Verification error:", error);
            setState(prev => ({
                ...prev,
                loading: false,
                error: error.message ?? "Phase-lock verification failed.",
            }));
            return;
        }

        setState({
            loading: false,
            error: null,
            result: data as PhaseLockResult,
        });
    }, []);

    return {
        ...state,
        runCheck,
    };
}
