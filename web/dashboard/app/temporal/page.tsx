'use client';

import React from 'react';
import { useTemporalDrift, DriftEntry } from '../../hooks/useTemporalDrift';

export default function TemporalPage() {
    const { entries, loading } = useTemporalDrift();

    const getSeverityColor = (severity: string) => {
        switch (severity) {
            case 'GREEN': return 'text-green-500 border-green-800';
            case 'YELLOW': return 'text-yellow-500 border-yellow-800';
            case 'RED': return 'text-red-500 border-red-800';
            default: return 'text-gray-500 border-gray-800';
        }
    };

    return (
        <div className="p-8 bg-black min-h-screen text-green-500 font-mono">
            <h1 className="text-3xl mb-6 border-b border-green-800 pb-2">Ω.5 TEMPORAL COHERENCE</h1>

            <div className="grid grid-cols-1 gap-6">
                <div className="bg-gray-900 border border-green-900 p-4 rounded">
                    <h2 className="text-xl mb-4">Drift Log</h2>
                    {loading ? (
                        <div>Synchronizing Chronometers...</div>
                    ) : (
                        <div className="space-y-2">
                            <div className="grid grid-cols-6 text-xs text-gray-400 border-b border-gray-800 pb-2 mb-2">
                                <div className="col-span-1">TIME (UTC)</div>
                                <div className="col-span-1">SOURCE</div>
                                <div className="col-span-1">DELTA (ms)</div>
                                <div className="col-span-1">SEVERITY</div>
                                <div className="col-span-2">PHASE HASH</div>
                            </div>
                            {entries.map((entry) => (
                                <div key={entry.id} className={`grid grid-cols-6 text-sm py-1 border-b border-gray-800/50 ${getSeverityColor(entry.severity)}`}>
                                    <div className="col-span-1 truncate">{new Date(entry.created_at).toLocaleTimeString()}</div>
                                    <div className="col-span-1">{entry.source}</div>
                                    <div className="col-span-1">{entry.drift_delta_ms !== null ? `${entry.drift_delta_ms}ms` : '-'}</div>
                                    <div className="col-span-1 font-bold">{entry.severity}</div>
                                    <div className="col-span-2 font-mono text-xs text-gray-500 truncate">{entry.phase_lock_hash || 'NULL'}</div>
                                </div>
                            ))}
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
}
