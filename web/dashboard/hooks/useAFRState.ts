"use client";

import { useEffect, useState } from "react";

export interface AFRMetrics {
    fluxVectorNorm: number;
    adjustmentImperative: number;
    recentAdjustments: any[];
}

export function useAFRState() {
    const [afrMetrics, setAfrMetrics] = useState<AFRMetrics>({
        fluxVectorNorm: 0,
        adjustmentImperative: 0,
        recentAdjustments: []
    });
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<Error | null>(null);

    useEffect(() => {
        let cancelled = false;

        async function fetchData() {
            if (cancelled) return;
            setLoading(true);
            try {
                const res = await fetch("/api/afr-state");
                const payload = await res.json();
                if (!res.ok) {
                    throw new Error(payload?.message || "Failed to load AFR state");
                }
                if (!cancelled) {
                    setAfrMetrics(payload);
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

    return { afrMetrics, loading, error };
}
