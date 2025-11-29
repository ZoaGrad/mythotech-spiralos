// web/dashboard/hooks/useParadoxRiskSurface.ts
"use client";

import { useEffect, useState } from "react";

export interface ParadoxRiskNode {
    id: string;
    created_at: string;
    paradox_risk: number;
    risk_band: "LOW" | "MEDIUM" | "HIGH" | "CRITICAL";
    drift_risk: number;
    tension_risk: number;
    prediction_window_start: string;
    prediction_window_end: string;
    status: string;
    realized_paradox_id: string | null;
    realized_at: string | null;
    realized_outcome: string | null;
    cause_type: string | null;
    link_severity: string | null;
    mesh_tension: number | null;
    fusion_strength: number | null;
    predicted_drift_ms: number | null;
    predicted_tension: number | null;
}

export function useParadoxRiskSurface() {
    const [data, setData] = useState<ParadoxRiskNode[] | null>(null);
    const [error, setError] = useState<Error | null>(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        let cancelled = false;

        async function fetchData() {
            if (cancelled) return;
            setLoading(true);
            try {
                const res = await fetch("/api/paradox-risk");
                const payload = await res.json();
                if (!res.ok) {
                    throw new Error(payload?.message || "Failed to load paradox risk surface");
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
