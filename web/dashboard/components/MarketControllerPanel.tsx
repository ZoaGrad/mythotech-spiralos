'use client';
import { useMarketState } from '../hooks/useMarketState';

export function MarketControllerPanel() {
    const { controllerState, coherence, scarcoinSupply, activeVaultNodes } = useMarketState();

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

                <div className="border-t border-gray-200 pt-2 mt-2">
                    <div className="flex justify-between text-emerald-600 font-medium">
                        <span>ScarCoin Supply:</span>
                        <span className="font-mono">{scarcoinSupply?.toFixed(2) || '0.00'} SCR</span>
                    </div>
                    <div className="flex justify-between text-blue-600 font-medium">
                        <span>Active VaultNodes:</span>
                        <span className="font-mono">{activeVaultNodes || '0'}</span>
                    </div>
                </div>
            </div>
        </div>
    );
}
