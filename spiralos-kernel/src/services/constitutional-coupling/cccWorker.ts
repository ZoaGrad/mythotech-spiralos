import { Worker, Job } from 'bullmq';
import { supabase } from '../../shared/supabaseClient.js';
import { connection } from '../../shared/redisClient.js';
import { ARIAService } from '../../aria/ariaService.js';
import { AFRService } from '../ache-flux-regulator/afrService.js';

export class ConstitutionalCouplingWorker {
    private worker: Worker;
    private ariaService: ARIAService;
    private afrService: AFRService;

    constructor() {
        this.worker = new Worker(
            'ConstitutionalCoupling',
            this.jobHandler.bind(this),
            { connection, autorun: false }
        );
        this.ariaService = new ARIAService();
        this.afrService = new AFRService();
    }

    private async jobHandler(job: Job): Promise<void> {
        console.log(`CCC Worker: Generating Constitutional Cognitive Context... [Mode: ${job.data.mode || 'standard'}]`);

        try {
            // 1. Gather ARIA's perceptual frame
            const ariaFrame = await this.ariaService.getCurrentPerceptualFrame();

            // 2. Gather AFR's thermodynamic state
            const afrState = await this.afrService.getCurrentState();

            // 3. Synthesize Constitutional Cognitive Context (with potential overrides)
            const ccc = await this.synthesizeCCC(ariaFrame, afrState, job.data.overrides);

            // 4. Store CCC
            const savedCCC = await this.storeCCC(ccc);

            // 5. Evaluate and draft amendments if triggered
            if (savedCCC.proposed_amendment_type) {
                await this.draftAmendment(savedCCC);
            }

            console.log('CCC Worker: Cycle complete');

        } catch (error) {
            console.error('CCC Worker Error:', error);
            throw error;
        }
    }

    private async synthesizeCCC(ariaFrame: any, afrState: any, overrides: any = {}) {
        // Apply overrides if present
        if (overrides.afr_adjustment_imperative) afrState.adjustment_imperative = overrides.afr_adjustment_imperative;
        if (overrides.paradox_density) ariaFrame.paradox_density = overrides.paradox_density;

        const currentAche = await this.getCurrentAcheLevel(afrState, ariaFrame);
        const scarIndexDerivative = await this.calculateScarIndexDerivative();

        return {
            aria_perceptual_frame: ariaFrame,
            noticed_patterns: ariaFrame.patterns || [],
            framing_narrative: ariaFrame.narrative,
            afr_adjustment_imperative: afrState.adjustment_imperative,
            afr_flux_vector_norm: afrState.flux_vector_norm,
            predicted_entropy_at_horizon: afrState.predicted_entropy_at_horizon,
            current_ache_level: currentAche,
            entropy_horizon_cycles: afrState.horizon_cycles,
            liquidity_regime: await this.getLiquidityRegime(afrState),
            civic_telemetry: await this.getCivicTelemetry(),
            risk_envelope: await this.calculateRiskEnvelope(afrState),
            ...await this.evaluateConstitutionalImplications(afrState, scarIndexDerivative, ariaFrame)
        };
    }

    private async evaluateConstitutionalImplications(afrState: any, scarDerivative: number, ariaFrame: any) {
        const implications = {
            proposed_amendment_type: null as string | null,
            constitutional_rationale: '',
            impact_projection: {}
        };

        // AFR-based constitutional triggers
        if (afrState.adjustment_imperative >= 0.9) {
            implications.proposed_amendment_type = 'emergency_thermodynamic';
            implications.constitutional_rationale = `AFR adjustment imperative (${afrState.adjustment_imperative}) exceeds constitutional threshold of 0.9. System requires structural amendment to maintain coherence.`;
        }

        // ScarIndex derivative triggers
        if (Math.abs(scarDerivative) > 0.1) {
            implications.proposed_amendment_type = 'stability_correction';
            implications.constitutional_rationale = `ScarIndex derivative (${scarDerivative}) indicates accelerating systemic stress requiring constitutional intervention.`;
        }

        // ARIA pattern-based triggers
        if (ariaFrame.paradox_density > 0.7) {
            implications.proposed_amendment_type = 'paradox_resolution';
            implications.constitutional_rationale = `High paradox density (${ariaFrame.paradox_density}) detected. Constitutional clarification required.`;
        }

        return implications;
    }

    // Fusion Logic Implementation
    private async getCurrentAcheLevel(afrState?: any, ariaFrame?: any) {
        const afr = afrState || await this.afrService.getCurrentState();
        const aria = ariaFrame || await this.ariaService.getCurrentPerceptualFrame();

        // Weighted fusion: 60% AFR (thermodynamics), 40% ARIA (perception)
        const ache = (afr.adjustment_imperative * 0.6) + (aria.paradox_density * 0.4);
        return parseFloat(ache.toFixed(3));
    }

    private async calculateScarIndexDerivative() {
        const { data } = await supabase
            .from('scarindex_calculations')
            .select('scarindex, created_at')
            .order('created_at', { ascending: false })
            .limit(2);

        if (!data || data.length < 2) return 0;

        const current = data[0].scarindex;
        const previous = data[1].scarindex;
        return parseFloat((current - previous).toFixed(4));
    }

    private async getLiquidityRegime(afrState?: any) {
        const afr = afrState || await this.afrService.getCurrentState();
        const flux = afr.flux_vector_norm;

        if (flux > 0.8) return 'hyper_fluid';
        if (flux > 0.5) return 'volatile';
        if (flux > 0.2) return 'dynamic';
        return 'stable';
    }

    private async getCivicTelemetry() {
        return { participation_rate: 0.85, coherence_score: 0.92 };
    }

    private async calculateRiskEnvelope(afrState?: any) {
        const afr = afrState || await this.afrService.getCurrentState();
        return {
            overall_risk: parseFloat((afr.adjustment_imperative * 0.8).toFixed(2)),
            thermodynamic_risk: afr.adjustment_imperative,
            liquidity_risk: afr.flux_vector_norm
        };
    }

    private async storeCCC(ccc: any) {
        const { data, error } = await supabase
            .from('constitutional_cognitive_context')
            .insert({
                timestamp: new Date().toISOString(),
                afr_adjustment_imperative: ccc.afr_adjustment_imperative,
                afr_flux_vector_norm: ccc.afr_flux_vector_norm,
                predicted_entropy_at_horizon: ccc.predicted_entropy_at_horizon,
                current_ache_level: ccc.current_ache_level,
                liquidity_regime: ccc.liquidity_regime,
                risk_envelope: ccc.risk_envelope,
                proposed_amendment_type: ccc.proposed_amendment_type,
                constitutional_rationale: ccc.constitutional_rationale
            })
            .select()
            .single();

        if (error) {
            throw new Error(`Supabase insert failed: ${error.message}`);
        }

        return data;
    }

    private async draftAmendment(ccc: any) {
        const amendment = {
            title: `Constitutional Amendment: ${ccc.proposed_amendment_type}`,
            description: ccc.constitutional_rationale,
            rationale: ccc.constitutional_rationale,
            trigger_event_id: ccc.id,
            status: 'proposed',
            impact_analysis: ccc.impact_projection
        };

        const { error } = await supabase
            .from('constitutional_amendments')
            .insert(amendment);

        if (error) {
            console.error('Failed to draft amendment:', error);
        } else {
            console.log('Drafted amendment for', ccc.proposed_amendment_type);
        }
    }

    async start(): Promise<void> {
        await this.worker.run();
        console.log('CCC Worker started');
    }

    async stop(): Promise<void> {
        await this.worker.close();
    }
}

// Start the worker if this file is run directly
new ConstitutionalCouplingWorker().start().catch(err => {
    console.error('Failed to start CCC Worker:', err);
    process.exit(1);
});
