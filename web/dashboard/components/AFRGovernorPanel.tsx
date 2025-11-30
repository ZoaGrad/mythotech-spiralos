'use client';

import { useAFRState } from '../hooks/useAFRState';

export function AFRGovernorPanel() {
    const { afrState, adjustmentLevel, fluxLevel, status, isLoading } = useAFRState();

    if (isLoading) {
        return (
            <div className="p-4 bg-gray-100 rounded-lg">
                Loading AFR Thermodynamic Governor…
            </div>
        );
    }

    const imperativeColor = (n: number) => {
        if (n < 0.3) return 'text-green-600';
        if (n < 0.7) return 'text-yellow-600';
        return 'text-red-600';
    };

    return (
        <div className="bg-white p-6 rounded-xl shadow border-l-4 border-blue-500">
            <h3 className="text-lg font-semibold mb-4">
                Ache Flux Regulator (AFR) — Thermodynamic Governor
            </h3>

            <div className="grid grid-cols-2 gap-4 mb-4">
                <div>
                    <div className="text-sm text-gray-500">Adjustment Imperative</div>
                    <div className={`text-2xl font-mono ${imperativeColor(adjustmentLevel)}`}>
                        {adjustmentLevel.toFixed(3)}
                    </div>
                </div>
                <div>
                    <div className="text-sm text-gray-500">Flux Vector Norm</div>
                    <div className="text-2xl font-mono text-blue-700">
                        {fluxLevel.toFixed(4)}
                    </div>
                </div>
            </div>

            <div className="text-sm text-gray-600">
                Status:{' '}
                <span className={status === 'operational' ? 'text-green-600' : 'text-red-600'}>
                    {status.toUpperCase()}
                </span>
            </div>

            {afrState?.recent_adjustments?.length > 0 && (
                <div className="mt-4 space-y-1 max-h-40 overflow-y-auto">
                    <h4 className="text-sm font-medium">Recent Adjustments</h4>
                    {afrState.recent_adjustments.map((adj: any, i: number) => (
                        <div
                            key={i}
                            className="text-xs border-l-2 border-amber-500 pl-2"
                        >
                            <div className="font-semibold">
                                {adj.payload?.adjustment_type ?? 'Unknown'}
                            </div>
                            <div className="text-gray-500">
                                {adj.payload?.reason ?? 'No reason provided'}
                            </div>
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
}
