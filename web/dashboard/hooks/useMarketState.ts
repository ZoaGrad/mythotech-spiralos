'use client';
import { useState, useEffect } from 'react';
import { createClient } from '@/lib/supabase/client';

interface AutonomousMarketControllerState {
    id: string;
    current_phase: string;
    liquidity_band: number;
    // ... other controller state fields
}

interface FMI1CoherenceMetric {
    id: string;
    coherence_score: number;
    // ... other coherence fields
}

export function useMarketState() {
    const [controllerState, setControllerState] = useState<AutonomousMarketControllerState | null>(null);
    const [coherence, setCoherence] = useState<number | null>(null);
    const [scarcoinSupply, setScarcoinSupply] = useState<number>(0);
    const [activeVaultNodes, setActiveVaultNodes] = useState<number>(0);
    const supabase = createClient();

    useEffect(() => {
        const fetchMarketData = async () => {
            // Fetch latest Autonomous Market Controller State
            const { data: controllerData, error: controllerError } = await supabase
                .from('autonomous_market_controller_state')
                .select('*')
                .order('created_at', { ascending: false })
                .limit(1)
                .single();
            if (controllerError) console.error('Error fetching controller state:', controllerError);
            setControllerState(controllerData);

            // Fetch latest FMI1 Coherence Metric
            const { data: coherenceData, error: coherenceError } = await supabase
                .from('fmi1_coherence_metrics')
                .select('coherence_score')
                .order('created_at', { ascending: false })
                .limit(1)
                .single();
            if (coherenceError) console.error('Error fetching coherence:', coherenceError);
            setCoherence(coherenceData?.coherence_score || null);

            // Fetch ScarCoin Supply
            const { data: mints, error: mintError } = await supabase
                .from('scarcoin_mints')
                .select('amount');
            if (mintError) console.error('Error fetching mints:', mintError);
            const supply = mints?.reduce((acc, curr) => acc + Number(curr.amount), 0) || 0;
            setScarcoinSupply(supply);

            // Fetch Active VaultNodes
            const { count, error: nodeError } = await supabase
                .from('vaultnode_registry')
                .select('*', { count: 'exact', head: true })
                .eq('status', 'active');
            if (nodeError) console.error('Error fetching nodes:', nodeError);
            setActiveVaultNodes(count || 0);
        };

        fetchMarketData();
        const interval = setInterval(fetchMarketData, 5000); // Poll every 5 seconds
        return () => clearInterval(interval);
    }, []);

    return { controllerState, coherence, scarcoinSupply, activeVaultNodes, mintBurnEvents: [] };
}
