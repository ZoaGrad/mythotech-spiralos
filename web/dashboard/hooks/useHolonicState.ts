'use client';
import { useState, useEffect } from 'react';
import { createClient } from '@/lib/supabase/client';

interface HolonicAgent {
    id: string;
    // ... other agent fields
}

interface LiquidityEquilibriumState {
    id: string;
    stability_index: number;
    // ... other equilibrium fields
}

interface ParadoxStressEvent {
    id: string;
    type: string;
    created_at: string;
    // ... other stress event fields
}

export function useHolonicState() {
    const [agents, setAgents] = useState<HolonicAgent[] | null>(null);
    const [equilibrium, setEquilibrium] = useState<LiquidityEquilibriumState | null>(null);
    const [stressEvents, setStressEvents] = useState<ParadoxStressEvent[] | null>(null);
    const supabase = createClient();

    useEffect(() => {
        const fetchHolonicData = async () => {
            // Fetch Holonic Agents
            const { data: agentsData, error: agentsError } = await supabase
                .from('holonic_liquidity_agents')
                .select('*');
            if (agentsError) console.error('Error fetching agents:', agentsError);
            setAgents(agentsData);

            // Fetch latest Liquidity Equilibrium State
            const { data: equilibriumData, error: equilibriumError } = await supabase
                .from('liquidity_equilibrium_state')
                .select('*')
                .order('created_at', { ascending: false })
                .limit(1)
                .single();
            if (equilibriumError) console.error('Error fetching equilibrium:', equilibriumError);
            setEquilibrium(equilibriumData);

            // Fetch recent Paradox Stress Events
            const { data: stressData, error: stressError } = await supabase
                .from('paradox_stress_events')
                .select('*')
                .order('created_at', { ascending: false })
                .limit(10); // Last 10 events
            if (stressError) console.error('Error fetching stress events:', stressError);
            setStressEvents(stressData);
        };

        fetchHolonicData();
        const interval = setInterval(fetchHolonicData, 5000); // Poll every 5 seconds
        return () => clearInterval(interval);
    }, []);

    return { agents, equilibrium, stressEvents };
}
