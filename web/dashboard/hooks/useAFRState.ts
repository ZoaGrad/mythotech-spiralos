'use client';
import { useState, useEffect } from 'react';
import { createClient } from '@/lib/supabase/client';

interface AFRState {
    adjustment_imperative: number;
    flux_vector_norm: number;
    horizon_cycles: number;
    predicted_entropy: number;
}

export function useAFRState() {
    const [afrState, setAfrState] = useState<AFRState | null>(null);
    const supabase = createClient();

    useEffect(() => {
        const fetchAfrData = async () => {
            // Fetch latest AFR fields from guardian_telemetry_events
            const { data: telemetryData, error: telemetryError } = await supabase
                .from('guardian_telemetry_events')
                .select('afr_adjustment_imperative, afr_flux_vector_norm')
                .order('created_at', { ascending: false })
                .limit(1)
                .single();
            if (telemetryError) console.error('Error fetching AFR telemetry:', telemetryError);

            // Fetch latest AFR fields from scarindex_calculations
            const { data: scarIndexData, error: scarIndexError } = await supabase
                .from('scarindex_calculations')
                .select('afr_horizon_cycles, afr_predicted_entropy')
                .order('created_at', { ascending: false })
                .limit(1)
                .single();
            if (scarIndexError) console.error('Error fetching AFR scarindex:', scarIndexError);

            if (telemetryData && scarIndexData) {
                setAfrState({
                    adjustment_imperative: telemetryData.afr_adjustment_imperative,
                    flux_vector_norm: telemetryData.afr_flux_vector_norm,
                    horizon_cycles: scarIndexData.afr_horizon_cycles,
                    predicted_entropy: scarIndexData.afr_predicted_entropy,
                });
            }
        };

        fetchAfrData();
        const interval = setInterval(fetchAfrData, 3000); // Poll more frequently for AFR
        return () => clearInterval(interval);
    }, []);

    return afrState;
}
