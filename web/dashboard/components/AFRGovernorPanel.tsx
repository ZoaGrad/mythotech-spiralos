'use client';
import { useAFRState } from '../hooks/useAFRState';

export function AFRGovernorPanel() {
    const afrState = useAFRState();

    const imperativeZone = afrState?.adjustment_imperative;
    const zoneColor =
        imperativeZone === undefined
            ? 'gray'
            : imperativeZone >= 0.9
                ? 'rose' // Proposal Zone
                : imperativeZone >= 0.7
                    ? 'orange' // Adjustment Zone
                    : 'green'; // Stable Zone

    return (
        <div className={`bg-white rounded-lg shadow p-6 border-l-4 border-l-${zoneColor}-500`}>
            <h3 className="text-lg font-semibold mb-4">Ache-Flux Regulator (AFR)</h3>

            <div className="space-y-3">
                <div className="flex justify-between">
                    <span>Adjustment Imperative:</span>
                    <span className={`font-mono text-${zoneColor}-600 font-bold`}>
                        {imperativeZone?.toFixed(4) || '0.0000'}
                    </span>
                </div>
                <div className="flex justify-between">
                    <span>Flux Vector Norm:</span>
                    <span className="font-mono">{afrState?.flux_vector_norm?.toFixed(4) || '0.0000'}</span>
                </div>
                <div className="flex justify-between">
                    <span>Predicted Entropy:</span>
                    <span className="font-mono">{afrState?.predicted_entropy?.toFixed(4) || '0.0000'}</span>
                </div>
                <div className="flex justify-between">
                    <span>Horizon Cycles:</span>
                    <span className="font-mono">{afrState?.horizon_cycles || 'N/A'}</span>
                </div>
            </div>

            <div className="mt-4 text-sm text-gray-600">
                <p>
                    Zone: {imperativeZone === undefined ? 'Unknown' :
                        imperativeZone >= 0.9 ? 'Constitutional Proposal (>=0.9)' :
                            imperativeZone >= 0.7 ? 'Automatic Adjustment (0.7-0.89)' :
                                'Stable (<0.7)'}
                </p>
            </div>
        </div>
    );
}
