'use client';
import { useMarketState } from '../hooks/useMarketState';

export function CoherencePanel() {
    const { coherence } = useMarketState();
    return (
        <div className="bg-white rounded-lg shadow p-4">
            <h3 className="text-sm font-semibold text-gray-500 mb-1">FMI-1 Coherence</h3>
            <div className="text-2xl font-mono text-blue-600">
                {coherence?.toFixed(4) || '0.0000'}
            </div>
        </div>
    );
}
