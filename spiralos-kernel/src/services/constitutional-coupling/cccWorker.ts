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
        console.log('CCC Worker: Generating Constitutional Cognitive Context...');

        try {
            // 1. Gather ARIA's perceptual frame
            const ariaFrame = await this.ariaService.getCurrentPerceptualFrame();

            // 2. Gather AFR's thermodynamic state
            const afrState = await this.afrService.getCurrentState();

            // 3. Synthesize Constitutional Cognitive Context
            const ccc = await this.synthesizeCCC(ariaFrame, afrState);

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

    private async synthesizeCCC(ariaFrame: any, afrState: any) {
        const currentAche = await this.getCurrentAcheLevel();
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
            liquidity_regime: await this.getLiquidityRegime(),
            civic_telemetry: await this.getCivicTelemetry(),
            risk_envelope: await this.calculateRiskEnvelope(),
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

    // Mock helper methods for now
    private async getCurrentAcheLevel() { return 0.5; }
    private async calculateScarIndexDerivative() { return 0.05; }
    private async getLiquidityRegime() { return 'stable'; }
    private async getCivicTelemetry() { return {}; }
    private async calculateRiskEnvelope() { return {}; }
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
