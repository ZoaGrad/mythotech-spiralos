'use client';
import { useMarketState } from '../hooks/useMarketState';

export function MarketControllerPanel() {
    const { controllerState, coherence } = useMarketState();

    return (
        <div className="bg-white rounded-lg shadow p-6 border-l-4 border-l-emerald-500">
            <h3 className="text-lg font-semibold mb-4">Autonomous Market Controller</h3>

            <div className="space-y-3">
                <div className="flex justify-between">
                    <span>Current Phase:</span>
                    <span className="font-mono">{controllerState?.current_phase || 'STABLE'}</span>
                </div>

                <div className="flex justify-between">
                    <span>Liquidity Band:</span>
                    <span className="font-mono">{controllerState?.liquidity_band?.toFixed(4) || '0.0000'}</span>
                </div>

                <div className="flex justify-between">
                    <span>FMI1 Coherence:</span>
                    <span className="font-mono">{coherence?.toFixed(4) || '0.0000'}</span>
                </div>
            </div>
        </div>
    );
}
