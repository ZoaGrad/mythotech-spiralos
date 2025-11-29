// web/dashboard/hooks/useGuardianActions.ts
"use client";

import { useEffect, useState } from "react";

export interface GuardianAction {
    id: string;
    created_at: string;
    lattice_state: string;
    collapse_probability: number;
    curvature_risk: number;
    continuation_score: number;
    chosen_action: string;
    severity: number;
    guardian_recommendation: string;
    status: string;
}

export function useGuardianActions() {
    const [data, setData] = useState<GuardianAction[] | null>(null);
    const [error, setError] = useState<Error | null>(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        let cancelled = false;

        async function fetchData() {
            if (cancelled) return;
            setLoading(true);
            try {
                const res = await fetch("/api/guardian-actions");
                const payload = await res.json();
                if (!res.ok) {
                    throw new Error(payload?.message || "Failed to load guardian actions");
                }
                if (!cancelled) {
                    setData(payload);
                    setError(null);
                }
            } catch (err: any) {
                if (!cancelled) setError(err);
            } finally {
                if (!cancelled) setLoading(false);
            }
        }

        fetchData();
        const id = setInterval(fetchData, 5000);

        return () => {
            cancelled = true;
            clearInterval(id);
        };
    }, []);

    return { data, error, loading };
}
