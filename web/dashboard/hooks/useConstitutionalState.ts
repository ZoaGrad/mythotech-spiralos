'use client';
import { useState, useEffect } from 'react';
import { createClient } from '@/lib/supabase/client';

interface ConstitutionalAmendment {
    id: string;
    amendment_number: number;
    title: string;
    proposal_text: string;
    rationale: string;
    status: string;
    proposed_at: string;
    trigger_conditions: any;
}

interface CCCSnapshot {
    id: string;
    timestamp: string;
    afr_adjustment_imperative: number;
    proposed_amendment_type?: string;
    constitutional_rationale?: string;
}

export function useConstitutionalState() {
    const [proposedAmendments, setProposedAmendments] = useState<ConstitutionalAmendment[]>([]);
    const [cccSnapshots, setCccSnapshots] = useState<CCCSnapshot[]>([]);
    const supabase = createClient();

    useEffect(() => {
        const fetchConstitutionalData = async () => {
            // Fetch proposed amendments
            const { data: amendments, error: amendmentsError } = await supabase
                .from('constitutional_amendments')
                .select('*')
                .eq('status', 'proposed')
                .order('proposed_at', { ascending: false });

            if (!amendmentsError) setProposedAmendments(amendments || []);

            // Fetch recent CCC snapshots
            const { data: cccData, error: cccError } = await supabase
                .from('constitutional_cognitive_context')
                .select('id, timestamp, afr_adjustment_imperative, proposed_amendment_type, constitutional_rationale')
                .order('timestamp', { ascending: false })
                .limit(10);

            if (!cccError) setCccSnapshots(cccData || []);
        };

        fetchConstitutionalData();
        const interval = setInterval(fetchConstitutionalData, 10000);
        return () => clearInterval(interval);
    }, []);

    return { proposedAmendments, cccSnapshots };
}
