'use client';

import { useEffect, useState } from 'react';

interface ContinuationData {
    metrics: {
        total_realizations: number;
        average_accuracy: number;
        guardian_trust_index: number;
    };
    recent_events: Array<{
        chain_id: string;
        predicted_at: string;
        predicted_probability: number;
        guardian_influence: string | null;
        realized_state: string;
        realized_collapse: boolean;
        accuracy_score: number;
    }>;
}

export default function ContinuationPage() {
    const [data, setData] = useState<ContinuationData | null>(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchData = async () => {
            try {
                const res = await fetch('/api/continuation-health');
                const json = await res.json();
                setData(json);
            } catch (e) {
                console.error(e);
            } finally {
                setLoading(false);
            }
        };

        fetchData();
        const interval = setInterval(fetchData, 5000);
        return () => clearInterval(interval);
    }, []);

    if (loading) return <div className="p-8 text-white">Loading Continuation Engine...</div>;
    if (!data) return <div className="p-8 text-red-400">Failed to load data.</div>;

    return (
        <div className="min-h-screen bg-black text-white p-8 font-mono">
            <h1 className="text-3xl font-bold mb-2 text-cyan-400">Ω.9 Continuation Engine</h1>
            <p className="text-gray-400 mb-8">Calibration & Realization Loop</p>

            {/* Metrics Cards */}
            <div className="grid grid-cols-3 gap-6 mb-8">
                <div className="bg-gray-900/50 border border-gray-800 p-6 rounded-lg">
                    <div className="text-sm text-gray-500 uppercase">Guardian Trust Index</div>
                    <div className={`text-4xl font-bold mt-2 ${data.metrics.guardian_trust_index > 0.8 ? 'text-green-400' :
                            data.metrics.guardian_trust_index > 0.5 ? 'text-yellow-400' : 'text-red-400'
                        }`}>
                        {(data.metrics.guardian_trust_index * 100).toFixed(1)}%
                    </div>
                </div>
                <div className="bg-gray-900/50 border border-gray-800 p-6 rounded-lg">
                    <div className="text-sm text-gray-500 uppercase">Avg Accuracy</div>
                    <div className="text-4xl font-bold mt-2 text-blue-400">
                        {(data.metrics.average_accuracy * 100).toFixed(1)}%
                    </div>
                </div>
                <div className="bg-gray-900/50 border border-gray-800 p-6 rounded-lg">
                    <div className="text-sm text-gray-500 uppercase">Realizations</div>
                    <div className="text-4xl font-bold mt-2 text-purple-400">
                        {data.metrics.total_realizations}
                    </div>
                </div>
            </div>

            {/* Recent Realizations Table */}
            <div className="border border-gray-800 rounded-lg overflow-hidden">
                <table className="w-full text-sm text-left">
                    <thead className="bg-gray-900 text-gray-400 uppercase text-xs">
                        <tr>
                            <th className="px-6 py-3">Predicted At</th>
                            <th className="px-6 py-3">Prediction</th>
                            <th className="px-6 py-3">Influence</th>
                            <th className="px-6 py-3">Outcome</th>
                            <th className="px-6 py-3">Accuracy</th>
                        </tr>
                    </thead>
                    <tbody className="divide-y divide-gray-800">
                        {data.recent_events.map((event) => (
                            <tr key={event.chain_id} className="bg-black/50 hover:bg-gray-900/50">
                                <td className="px-6 py-4 text-gray-400">
                                    {new Date(event.predicted_at).toLocaleTimeString()}
                                </td>
                                <td className="px-6 py-4">
                                    <span className="text-gray-300">{(event.predicted_probability * 100).toFixed(0)}% Risk</span>
                                </td>
                                <td className="px-6 py-4 text-blue-300">
                                    {event.guardian_influence || '-'}
                                </td>
                                <td className="px-6 py-4">
                                    <span className={`px-2 py-1 rounded text-xs ${event.realized_collapse ? 'bg-red-900 text-red-300' : 'bg-green-900 text-green-300'
                                        }`}>
                                        {event.realized_state}
                                    </span>
                                </td>
                                <td className="px-6 py-4 font-bold">
                                    {(event.accuracy_score * 100).toFixed(0)}%
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>
        </div>
    );
}
