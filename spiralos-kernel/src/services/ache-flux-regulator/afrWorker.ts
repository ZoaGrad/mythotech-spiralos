import { env } from '../../shared/env.js';
import { logger } from '../../shared/logger.js';
import { withRetry } from '../../shared/retry.js';
import { supabase } from '../../shared/supabaseClient.js';

const delay = (ms: number) => new Promise((resolve) => setTimeout(resolve, ms));

export class AcheFluxRegulatorWorker {

    async gatherSystemState() {
        // From ScarIndex Oracle
        const { data: scarIndex } = await withRetry(() =>
            supabase
                .from('scarindex_calculations')
                .select('scarindex, created_at')
                .order('created_at', { ascending: false })
                .limit(10)
        ) as any;

        // From PoA Ledger (attestations as proxy for ache_events if not exists)
        const { data: acheThroughput } = await withRetry(() =>
            supabase
                .from('attestations') // Using attestations as proxy for now
                .select('entropy, created_at') // entropy as ache_level?
                .gte('created_at', new Date(Date.now() - 3600000).toISOString())
        ) as any;

        // From LRE efficiency
        const { data: lreEfficiency } = await withRetry(() =>
            supabase
                .from('guardian_telemetry_events')
                .select('agent_health, latency_ms, created_at')
                .order('created_at', { ascending: false })
                .limit(20)
        ) as any;

        // From Witness coherence
        const { data: witnessCoherence } = await withRetry(() =>
            supabase
                .from('witness_events')
                .select('resonance, status, created_at')
                .gte('created_at', new Date(Date.now() - 7200000).toISOString())
        ) as any;

        return {
            scarIndex: scarIndex || [],
            acheThroughput: acheThroughput || [],
            lreEfficiency: lreEfficiency || [],
            witnessCoherence: witnessCoherence || []
        };
    }

    calculateTrend(values: number[]) {
        if (values.length < 2) return 0;
        const first = values[values.length - 1];
        const last = values[0];
        return (last - first) / values.length;
    }

    computeEntropyComposite(scar: number, lre: number, witness: number) {
        // Simple weighted average for now
        return (scar * 0.4) + (lre * 0.3) + (witness * 0.3);
    }

    calculateAdjustmentImperative(fluxState: any) {
        // Logic: If flux vector is high, imperative is high.
        // If systemic entropy is high, imperative is high.
        return (fluxState.flux_vector_norm * 0.5) + (fluxState.systemic_entropy * 0.5);
    }

    determineAdjustmentType(fluxState: any) {
        if (fluxState.scar_index_trend < 0) return 'stabilize_volatility';
        if (fluxState.lre_efficiency_trend < 0) return 'optimize_routing';
        return 'general_dampening';
    }

    getTargetParameter(fluxState: any) {
        if (fluxState.scar_index_trend < 0) return 'transaction_fee';
        return 'mint_rate';
    }

    generateConstitutionalAmendment(fluxState: any) {
        return {
            rationale: "High Flux Vector detected",
            suggested_weights: { operational: 0.4, audit: 0.4, constitutional: 0.2 }
        };
    }

    calculateFluxState(systemState: any) {
        const scarTrend = this.calculateTrend(systemState.scarIndex.map((s: any) => s.scarindex));
        const acheTrend = this.calculateTrend(systemState.acheThroughput.map((a: any) => a.entropy || 0)); // using entropy
        const lreTrend = this.calculateTrend(systemState.lreEfficiency.map((l: any) => l.agent_health));

        const systemicEntropy = this.computeEntropyComposite(
            systemState.scarIndex[0]?.scarindex || 0.5,
            systemState.lreEfficiency[0]?.agent_health || 0.8,
            systemState.witnessCoherence[0]?.resonance || 0.7
        );

        return {
            scar_index_current: systemState.scarIndex[0]?.scarindex || 0.5,
            scar_index_trend: scarTrend,
            ache_throughput_current: systemState.acheThroughput.length / 3600,
            ache_throughput_trend: acheTrend,
            lre_efficiency_current: systemState.lreEfficiency[0]?.agent_health || 0.8,
            lre_efficiency_trend: lreTrend,
            witness_coherence_current: systemState.witnessCoherence[0]?.resonance || 0.7,
            systemic_entropy: systemicEntropy,
            flux_vector_norm: Math.sqrt(scarTrend ** 2 + acheTrend ** 2 + lreTrend ** 2),
            adjustment_imperative: 0.0 // Placeholder, recalculated below
        };
    }

    async executeRegulatoryActions(fluxState: any) {
        const imperative = this.calculateAdjustmentImperative(fluxState);
        fluxState.adjustment_imperative = imperative; // Update state

        logger.info({ imperative, fluxState }, 'AFR Analysis Complete');

        if (imperative >= 0.9) {
            await withRetry(() =>
                supabase
                    .from('governance_proposals')
                    .insert({
                        title: 'AFR Constitutional Amendment',
                        description: JSON.stringify(this.generateConstitutionalAmendment(fluxState)),
                        status: 'pending',
                        // consistency_score: 1 - fluxState.systemic_entropy // Column might not exist?
                    })
            ) as any;
        }
        else if (imperative >= 0.7) {
            await withRetry(() =>
                supabase
                    .from('system_events')
                    .insert({
                        event_type: 'afr_adjustment',
                        payload: {
                            adjustment_type: this.determineAdjustmentType(fluxState),
                            magnitude: imperative,
                            target_parameter: this.getTargetParameter(fluxState),
                            reason: `Ache-Flux regulation: imperative ${imperative.toFixed(3)}`
                        }
                    })
            ) as any;

            // Execute actual parameter adjustment (Placeholder)
            // await this.executeParameterAdjustment(fluxState);
        }

        // Update telemetry
        // Need a valid ID. For now, we just log or insert a new event if we can't find one.
        // Or we fetch the latest one.
        const { data: latestTelemetry } = await supabase
            .from('guardian_telemetry_events')
            .select('id')
            .order('created_at', { ascending: false })
            .limit(1);

        if (latestTelemetry && latestTelemetry[0]) {
            await supabase
                .from('guardian_telemetry_events')
                .update({
                    afr_flux_vector_norm: fluxState.flux_vector_norm,
                    afr_adjustment_imperative: imperative
                })
                .eq('id', latestTelemetry[0].id);
        }
    }

    async runCycle() {
        try {
            const systemState = await this.gatherSystemState();
            const fluxState = this.calculateFluxState(systemState);
            await this.executeRegulatoryActions(fluxState);
        } catch (error) {
            logger.error({ error }, 'AFR Cycle Failed');
        }
    }
}

export async function startAfrLoop(): Promise<never> {
    logger.info('Starting Ache Flux Regulator (AFR) loop');
    const worker = new AcheFluxRegulatorWorker();
    while (true) {
        await worker.runCycle();
        await delay(env.SCAN_INTERVAL_MS || 15000); // Default 15s
    }
}
