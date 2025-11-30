'use client';

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

interface CCCMonitorProps {
    cccState: CCCState | null;
}

export function CCCMonitor({ cccState }: CCCMonitorProps) {
    const getImperativeColor = (imperative: number) => {
        if (imperative < 0.3) return 'text-green-600 bg-green-50';
        if (imperative < 0.7) return 'text-yellow-600 bg-yellow-50';
        return 'text-red-600 bg-red-50';
    };

    const getRiskLevel = (envelope: any) => {
        if (!envelope) return 'UNKNOWN';
        const overall = envelope.overall_risk || 0;
        if (overall < 0.3) return 'LOW';
        if (overall < 0.7) return 'MEDIUM';
        return 'HIGH';
    };

    if (!cccState) {
        return (
            <div className="bg-white rounded-lg shadow p-6">
                <h3 className="text-lg font-semibold mb-4">Constitutional Cognitive Context</h3>
                <div className="text-center py-8 text-gray-500">
                    <p>No CCC data available</p>
                    <p className="text-sm mt-2">Waiting for Constitutional Coupling Worker...</p>
                </div>
            </div>
        );
    }

    return (
        <div className="bg-white rounded-lg shadow p-6">
            <div className="flex justify-between items-start mb-6">
                <h3 className="text-lg font-semibold">Constitutional Cognitive Context</h3>
                <span className="text-xs bg-blue-100 text-blue-800 px-2 py-1 rounded">
                    {new Date(cccState.timestamp).toLocaleTimeString()}
                </span>
            </div>

            {/* Key Metrics Grid */}
            <div className="grid grid-cols-2 gap-4 mb-6">
                <div className={`p-3 rounded-lg ${getImperativeColor(cccState.afr_adjustment_imperative)}`}>
                    <div className="text-sm font-medium">AFR Imperative</div>
                    <div className="text-2xl font-bold">{cccState.afr_adjustment_imperative.toFixed(3)}</div>
                </div>

                <div className="p-3 rounded-lg bg-blue-50 text-blue-600">
                    <div className="text-sm font-medium">Flux Vector</div>
                    <div className="text-2xl font-bold">{cccState.afr_flux_vector_norm.toFixed(4)}</div>
                </div>

                <div className="p-3 rounded-lg bg-purple-50 text-purple-600">
                    <div className="text-sm font-medium">Ache Level</div>
                    <div className="text-2xl font-bold">{cccState.current_ache_level.toFixed(3)}</div>
                </div>

                <div className="p-3 rounded-lg bg-gray-50 text-gray-600">
                    <div className="text-sm font-medium">Risk Level</div>
                    <div className="text-2xl font-bold">{getRiskLevel(cccState.risk_envelope)}</div>
                </div>
            </div>

            {/* Additional Context */}
            <div className="space-y-3 text-sm">
                <div className="flex justify-between">
                    <span className="text-gray-600">Predicted Entropy:</span>
                    <span className="font-mono">{cccState.predicted_entropy_at_horizon.toFixed(4)}</span>
                </div>

                <div className="flex justify-between">
                    <span className="text-gray-600">Liquidity Regime:</span>
                    <span className="font-medium">{cccState.liquidity_regime || 'STABLE'}</span>
                </div>

                {cccState.proposed_amendment_type && (
                    <div className="mt-4 p-3 bg-amber-50 border border-amber-200 rounded-lg">
                        <div className="font-medium text-amber-800">Amendment Triggered</div>
                        <div className="text-amber-700 text-sm mt-1">{cccState.proposed_amendment_type}</div>
                        {cccState.constitutional_rationale && (
                            <div className="text-amber-600 text-xs mt-2">{cccState.constitutional_rationale}</div>
                        )}
                    </div>
                )}
            </div>
        </div>
    );
}
