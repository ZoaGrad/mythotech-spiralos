'use client';

interface CCCState {
    id: string;
    timestamp: string;
    afr_adjustment_imperative: number;
}

interface ArbitrationControlsProps {
    cccState: CCCState | null;
    onRefresh: () => void;
}

export function ArbitrationControls({ cccState, onRefresh }: ArbitrationControlsProps) {
    return (
        <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-semibold mb-4">Arbitration Controls</h3>

            <div className="space-y-4">
                <div className="flex space-x-3">
                    <button
                        onClick={onRefresh}
                        className="flex-1 bg-blue-500 text-white py-2 px-4 rounded text-sm font-medium hover:bg-blue-600 transition-colors"
                    >
                        Refresh Data
                    </button>
                    <button
                        onClick={() => console.log('Manual override - not yet implemented')}
                        className="flex-1 bg-gray-500 text-white py-2 px-4 rounded text-sm font-medium hover:bg-gray-600 transition-colors opacity-50 cursor-not-allowed"
                        disabled
                    >
                        Manual Override
                    </button>
                </div>

                <div className="p-3 bg-gray-50 rounded-lg">
                    <div className="text-sm text-gray-600">
                        <div className="font-medium">System Status</div>
                        <div className="mt-1 space-y-1 text-xs">
                            <div>CCC: {cccState ? 'ACTIVE' : 'INACTIVE'}</div>
                            <div>Last Signal: {cccState ? new Date(cccState.timestamp).toLocaleTimeString() : 'Never'}</div>
                            <div>AFR Imperative: {cccState?.afr_adjustment_imperative.toFixed(3) || 'N/A'}</div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}
