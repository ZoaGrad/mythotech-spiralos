'use client';

import React from 'react';
import { useAuditSurface, AuditEvent } from '../../hooks/useAuditSurface';

export default function AuditPage() {
    const { events, loading } = useAuditSurface();

    return (
        <div className="p-8 bg-black min-h-screen text-green-500 font-mono">
            <h1 className="text-3xl mb-6 border-b border-green-800 pb-2">Ω.4 GLOBAL AUDIT SURFACE</h1>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                <div className="lg:col-span-2">
                    <div className="bg-gray-900 border border-green-900 p-4 rounded">
                        <h2 className="text-xl mb-4">Event Stream</h2>
                        {loading ? (
                            <div>Initializing Uplink...</div>
                        ) : (
                            <div className="space-y-2 h-[600px] overflow-y-auto">
                                {events.map((evt) => (
                                    <div key={evt.id} className="border-l-2 border-green-700 pl-3 py-1 text-sm hover:bg-green-900/20 transition-colors">
                                        <div className="flex justify-between text-xs text-green-400">
                                            <span>{new Date(evt.created_at).toLocaleTimeString()}</span>
                                            <span>{evt.component}</span>
                                        </div>
                                        <div className="font-bold">{evt.event_type}</div>
                                        <div className="text-xs text-gray-500 truncate">{JSON.stringify(evt.payload)}</div>
                                        {evt.phase_lock_hash && (
                                            <div className="text-[10px] text-blue-400 mt-1">LOCK: {evt.phase_lock_hash.substring(0, 12)}...</div>
                                        )}
                                    </div>
                                ))}
                            </div>
                        )}
                    </div>
                </div>

                <div>
                    <div className="bg-gray-900 border border-green-900 p-4 rounded mb-6">
                        <h2 className="text-xl mb-2">Hash Delta</h2>
                        <div className="text-4xl font-bold text-blue-500">SYNC</div>
                        <div className="text-xs text-gray-400 mt-2">Baseline vs Runtime</div>
                    </div>

                    <div className="bg-gray-900 border border-green-900 p-4 rounded">
                        <h2 className="text-xl mb-2">Metrics</h2>
                        <div className="grid grid-cols-2 gap-4">
                            <div>
                                <div className="text-xs text-gray-400">Events/Min</div>
                                <div className="text-2xl">--</div>
                            </div>
                            <div>
                                <div className="text-xs text-gray-400">Components</div>
                                <div className="text-2xl">4</div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}
