"use client";

import { useFusion } from "@/hooks/useFusion";

export default function FusionPage() {
    const { data, error } = useFusion();

    if (error) return <div className="p-8 text-red-500">Failed to load fusion data.</div>;
    if (!data) return <div className="p-8 text-gray-400">Loading fusion matrix...</div>;

    return (
        <div className="p-8 max-w-7xl mx-auto">
            <h1 className="text-3xl font-bold mb-6 text-purple-400">Mesh Temporal Fusion</h1>

            <div className="bg-gray-900/50 border border-gray-800 rounded-lg overflow-hidden">
                <table className="w-full text-left text-sm text-gray-400">
                    <thead className="bg-gray-800 text-gray-200 uppercase font-medium">
                        <tr>
                            <th className="px-6 py-3">Timestamp</th>
                            <th className="px-6 py-3">Fusion ID</th>
                            <th className="px-6 py-3">Strength</th>
                            <th className="px-6 py-3">Drift (ms)</th>
                            <th className="px-6 py-3">Tension</th>
                            <th className="px-6 py-3">Severity</th>
                        </tr>
                    </thead>
                    <tbody className="divide-y divide-gray-800">
                        {data.map((row: any) => (
                            <tr key={row.id} className="hover:bg-gray-800/50 transition-colors">
                                <td className="px-6 py-4 font-mono text-xs text-gray-500">
                                    {new Date(row.created_at).toLocaleString()}
                                </td>
                                <td className="px-6 py-4 font-mono text-xs text-blue-400">
                                    {row.id.slice(0, 8)}...
                                </td>
                                <td className="px-6 py-4 font-mono text-purple-400">
                                    {Number(row.fusion_strength).toFixed(2)}
                                </td>
                                <td className="px-6 py-4 font-mono text-yellow-400">
                                    {Number(row.predicted_drift_ms).toFixed(2)}
                                </td>
                                <td className="px-6 py-4 font-mono text-red-400">
                                    {Number(row.predicted_tension).toFixed(2)}
                                </td>
                                <td className="px-6 py-4">
                                    <span className={`px-2 py-1 rounded text-xs font-bold ${row.severity === 'RED' ? 'bg-red-900/50 text-red-400' :
                                            row.severity === 'AMBER' ? 'bg-yellow-900/50 text-yellow-400' :
                                                'bg-green-900/50 text-green-400'
                                        }`}>
                                        {row.severity || 'UNKNOWN'}
                                    </span>
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>
        </div>
    );
}
