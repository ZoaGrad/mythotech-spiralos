'use client';
import { useState, useEffect } from 'react';
import { CCCMonitor } from '@/components/arbitration/CCCMonitor';
import { AmendmentQueue } from '@/components/arbitration/AmendmentQueue';
import { ArbitrationControls } from '@/components/arbitration/ArbitrationControls';

interface CCCState {
    id: string;
    timestamp: string;
    afr_adjustment_imperative: number;
    afr_flux_vector_norm: number;
    predicted_entropy_at_horizon: number;
    current_ache_level: number;
    liquidity_regime: string;
    proposed_amendment_type?: string;
    constitutional_rationale?: string;
    risk_envelope: any;
}

interface Amendment {
    id: string;
    amendment_number: number;
    title: string;
    proposal_text: string;
    rationale: string;
    status: string;
    proposed_at: string;
    trigger_conditions: any;
    ccc_id: string;
}

export default function GuardianArbitrationPage() {
    const [cccState, setCccState] = useState<CCCState | null>(null);
    const [amendments, setAmendments] = useState<Amendment[]>([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        fetchArbitrationData();
        const interval = setInterval(fetchArbitrationData, 10000); // Refresh every 10s
        return () => clearInterval(interval);
    }, []);

    const fetchArbitrationData = async () => {
        try {
            const response = await fetch('/api/guardian/arbitration');
            const data = await response.json();

            setCccState(data.cccState);
            setAmendments(data.amendments);
        } catch (error) {
            console.error('Failed to fetch arbitration data:', error);
        } finally {
            setLoading(false);
        }
    };

    const handleArbitrationDecision = async (amendmentId: string, decision: 'ratify' | 'veto') => {
        try {
            const response = await fetch('/api/guardian/arbitration', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ amendmentId, decision })
            });

            if (response.ok) {
                // Refresh data after decision
                fetchArbitrationData();
                console.log(`Amendment ${amendmentId} ${decision}ed successfully`);
            } else {
                console.error('Failed to submit arbitration decision');
            }
        } catch (error) {
            console.error('Error submitting arbitration decision:', error);
        }
    };

    if (loading) {
        return (
            <div className="min-h-screen bg-gray-50 p-8">
                <div className="max-w-7xl mx-auto">
                    <div className="animate-pulse">
                        <div className="h-8 bg-gray-200 rounded w-1/4 mb-6"></div>
                        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                            <div className="h-64 bg-gray-200 rounded"></div>
                            <div className="h-64 bg-gray-200 rounded"></div>
                        </div>
                    </div>
                </div>
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-gray-50 p-8">
            <div className="max-w-7xl mx-auto">
                {/* Header */}
                <div className="mb-8">
                    <h1 className="text-3xl font-bold text-gray-900">Guardian Arbitration Panel</h1>
                    <p className="text-gray-600 mt-2">
                        Constitutional governance interface for SpiralOS self-amendment protocol
                    </p>
                </div>

                {/* Main Content Grid */}
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                    {/* CCC Monitor */}
                    <div className="space-y-6">
                        <CCCMonitor cccState={cccState} />
                    </div>

                    {/* Amendment Queue & Controls */}
                    <div className="space-y-6">
                        <AmendmentQueue
                            amendments={amendments}
                            onArbitrationDecision={handleArbitrationDecision}
                        />
                        <ArbitrationControls
                            cccState={cccState}
                            onRefresh={fetchArbitrationData}
                        />
                    </div>
                </div>

                {/* System Status Footer */}
                <div className="mt-12 pt-6 border-t border-gray-200">
                    <div className="flex justify-between items-center text-sm text-gray-500">
                        <span>Constitutional Intelligence: {cccState ? 'ACTIVE' : 'STANDBY'}</span>
                        <span>Amendments Pending: {amendments.filter(a => a.status === 'proposed').length}</span>
                        <span>Last Updated: {cccState ? new Date(cccState.timestamp).toLocaleTimeString() : 'Never'}</span>
                    </div>
                </div>
            </div>
        </div>
    );
}
