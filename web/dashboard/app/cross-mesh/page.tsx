"use client";

import React from 'react';
import { useCrossMesh } from "../../hooks/useCrossMesh";

export default function CrossMeshPage() {
    const { data, error, loading } = useCrossMesh();

    return (
        <div className="p-8 bg-gray-900 min-h-screen text-white font-mono">
            <h1 className="text-3xl font-bold mb-6 text-purple-400 border-b border-purple-800 pb-2">
                Ω.6-C Cross-Mesh Reconciliation Surface
            </h1>

            {error && (
                <div className="bg-red-900/50 border border-red-500 p-4 mb-6 rounded text-red-200">
                    Error loading mesh data: {JSON.stringify(error)}
                </div>
            )}

            {loading && (
                <div className="text-gray-400 animate-pulse">Loading surface data...</div>
            )}

            {!loading && data && (
                <div className="overflow-x-auto bg-gray-800 rounded-lg border border-gray-700 shadow-xl">
                    <table className="w-full text-left text-sm">
                        <thead className="bg-gray-900 text-gray-400 uppercase tracking-wider">
                            <tr>
                                <th className="px-6 py-3 border-b border-gray-700">Time</th>
                                <th className="px-6 py-3 border-b border-gray-700">Type</th>
                                <th className="px-6 py-3 border-b border-gray-700">Source</th>
                                <th className="px-6 py-3 border-b border-gray-700">Tension</th>
                                <th className="px-6 py-3 border-b border-gray-700">Severity</th>
                                <th className="px-6 py-3 border-b border-gray-700">Payload</th>
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-gray-700">
                            {data.map((row: any) => (
                                <tr key={row.id} className="hover:bg-gray-750 transition-colors">
                                    <td className="px-6 py-4 whitespace-nowrap text-gray-300">
                                        {new Date(row.created_at).toLocaleString()}
                                    </td>
                                    <td className="px-6 py-4 whitespace-nowrap font-bold text-blue-400">
                                        {row.resolved_type || row.event_type}
                                    </td>
                                    <td className="px-6 py-4 whitespace-nowrap text-gray-400">
                                        {row.source_table}::{row.source_id.substring(0, 8)}...
                                    </td>
                                    <td className="px-6 py-4 whitespace-nowrap">
                                        <span className={`px-2 py-1 rounded text-xs ${Number(row.mesh_tension) > 0.7 ? 'bg-red-900 text-red-200' :
                                                Number(row.mesh_tension) > 0.3 ? 'bg-yellow-900 text-yellow-200' :
                                                    'bg-green-900 text-green-200'
                                            }`}>
                                            {Number(row.mesh_tension).toFixed(3)}
                                        </span>
                                    </td>
                                    <td className="px-6 py-4 whitespace-nowrap">
                                        <span className={`font-bold ${row.severity === 'RED' ? 'text-red-500' :
                                                row.severity === 'YELLOW' ? 'text-yellow-500' :
                                                    'text-green-500'
                                            }`}>
                                            {row.severity}
                                        </span>
                                    </td>
                                    <td className="px-6 py-4 text-gray-500 truncate max-w-xs">
                                        {JSON.stringify(row.payload)}
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            )}
        </div>
    );
}
