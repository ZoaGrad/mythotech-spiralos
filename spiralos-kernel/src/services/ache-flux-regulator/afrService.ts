import { supabase } from '../../shared/supabaseClient.js';

export class AFRService {
    async getCurrentState() {
        // Fetch latest AFR telemetry from guardian_telemetry_events
        const { data, error } = await supabase
            .from('guardian_telemetry_events')
            .select('afr_adjustment_imperative, afr_flux_vector_norm')
            .order('created_at', { ascending: false })
            .limit(1)
            .single();

        if (error || !data) {
            // Fallback if no data yet (e.g. worker hasn't run)
            return {
                adjustment_imperative: 0.5,
                flux_vector_norm: 0.1,
                predicted_entropy_at_horizon: 0.1,
                horizon_cycles: 100
            };
        }

        return {
            adjustment_imperative: data.afr_adjustment_imperative || 0.5,
            flux_vector_norm: data.afr_flux_vector_norm || 0.1,
            predicted_entropy_at_horizon: 0.1, // Not yet in telemetry, keeping mock
            horizon_cycles: 100
        };
    }
}
