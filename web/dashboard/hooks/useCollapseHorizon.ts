// web/dashboard/hooks/useCollapseHorizon.ts
"use client";

import { useEffect, useState } from "react";

export interface CollapseEnvelopeNode {
    id: string;
    created_at: string;
    collapse_risk: number;
    collapse_band: "LOW" | "MEDIUM" | "HIGH" | "CRITICAL";
    envelope_kind: "DRIFT" | "TENSION" | "FUSION" | "COMPOSITE";
    horizon_start: string;
    horizon_end: string;
    status: string;
    realized_outcome: string | null;
    realized_at: string | null;
    paradox_risk: number;
    paradox_risk_band: string;
    drift_risk: number;
    tension_risk: number;
    scarindex_value: number | null;
    panic_status: string | null;
}

export function useCollapseHorizon() {
    const [data, setData] = useState<CollapseEnvelopeNode[] | null>(null);
    const [error, setError] = useState<Error | null>(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        let cancelled = false;

        async function fetchData() {
            if (cancelled) return;
            setLoading(true);
            try {
                const res = await fetch("/api/collapse-horizon");
                const payload = await res.json();
                if (!res.ok) {
                    throw new Error(payload?.message || "Failed to load collapse horizon surface");
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
