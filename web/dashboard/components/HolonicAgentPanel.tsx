'use client';
import { useHolonicState } from '../hooks/useHolonicState';

export function HolonicAgentPanel() {
    const { agents, equilibrium, stressEvents } = useHolonicState();

    return (
        <div className="bg-white rounded-lg shadow p-6 border-l-4 border-l-purple-500">
            <h3 className="text-lg font-semibold mb-4">Holonic Liquidity Agents</h3>

            <div className="grid grid-cols-3 gap-4 mb-4">
                <div className="text-center">
                    <div className="text-2xl font-bold text-purple-600">{agents?.length || 0}</div>
                    <div className="text-sm text-gray-600">Active Agents</div>
                </div>

                <div className="text-center">
                    <div className="text-2xl font-bold text-green-600">
                        {equilibrium?.stability_index?.toFixed(3) || '0.000'}
                    </div>
                    <div className="text-sm text-gray-600">Stability Index</div>
                </div>

                <div className="text-center">
                    <div className="text-2xl font-bold text-amber-600">
                        {stressEvents?.length || 0}
                    </div>
                    <div className="text-sm text-gray-600">Stress Events</div>
                </div>
            </div>

            {/* Agent activity stream */}
            <div className="mt-4">
                <h4 className="text-sm font-medium mb-2">Recent Agent Actions</h4>
                {stressEvents && stressEvents.length > 0 ? (
                    <ul className="text-xs text-gray-700 space-y-1 max-h-24 overflow-y-auto">
                        {stressEvents.map((event) => (
                            <li key={event.id} className="truncate">
                                [{new Date(event.created_at).toLocaleTimeString()}] Stress: {event.type}
                            </li>
                        ))}
                    </ul>
                ) : (
                    <p className="text-xs text-gray-500">No recent stress events.</p>
                )}
            </div>
        </div>
    );
}
