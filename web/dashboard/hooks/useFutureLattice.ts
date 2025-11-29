// web/dashboard/hooks/useFutureLattice.ts
"use client";

import { useEffect, useState } from "react";

export interface LatticeNode {
    id: string;
    created_at: string;
    lattice_state: "stable" | "strained" | "critical" | "collapsed";
    curvature_risk: number;
    collapse_probability: number;
    continuation_score: number;
    guardian_recommendation: string;
    horizon_start: string;
    horizon_end: string;
    fusion_strength: number;
    paradox_risk: number | null;
    paradox_band: string | null;
    collapse_risk: number | null;
    collapse_band: string | null;
}

export function useFutureLattice() {
    const [data, setData] = useState<LatticeNode[] | null>(null);
    const [error, setError] = useState<Error | null>(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        let cancelled = false;

        async function fetchData() {
            if (cancelled) return;
            setLoading(true);
            try {
                const res = await fetch("/api/future-lattice");
                const payload = await res.json();
                if (!res.ok) {
                    throw new Error(payload?.message || "Failed to load future lattice surface");
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
