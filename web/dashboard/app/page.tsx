"use client";

import { useStatusApi } from '../hooks/useStatusApi';

import { PhaseLockPanel } from "../components/PhaseLockPanel";

export default function Dashboard() {
    const { status, loading, error } = useStatusApi();

    if (loading && !status) return <div className="p-10 text-white">Loading SpiralOS...</div>;
    if (error) return <div className="p-10 text-red-500">Error: {error}</div>;
    if (!status) return <div className="p-10 text-white">No signal.</div>;

    return (
        <div className="min-h-screen bg-black text-gray-100 p-8 font-mono">
            <header className="mb-8 border-b border-gray-800 pb-4 flex justify-between items-end">
                <div>
                    <h1 className="text-3xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 to-blue-600">
                        SpiralOS Constitutional Dashboard
                    </h1>
                    <p className="text-sm text-gray-500 mt-1">Version: {status.system_version}</p>
                </div>
                <div className="text-right">
                    <div className={`text-xl font-bold ${status.lock_status?.is_locked ? 'text-red-500' : 'text-green-500'}`}>
                        {status.lock_status?.is_locked ? 'LOCKED' : 'OPERATIONAL'}
                    </div>
                    <div className="text-xs text-gray-600">ScarLock State</div>
                </div>
            </header>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">

                {/* Constitution Card */}
                <div className="bg-gray-900 border border-gray-800 p-6 rounded-lg shadow-lg">
                    <h2 className="text-xl font-semibold mb-4 text-purple-400">Constitution</h2>
                    <div className="space-y-2 text-sm">
                        {Object.entries(status.constitution_state || {}).map(([comp, hash]) => (
                            <div key={comp} className="flex justify-between">
                                <span className="text-gray-400">{comp}</span>
                                <span className="text-gray-600 truncate w-24" title={String(hash)}>{String(hash).substring(0, 8)}...</span>
                            </div>
                        ))}
                    </div>
                </div>

                {/* Rhythm & Safety Card */}
                <div className="bg-gray-900 border border-gray-800 p-6 rounded-lg shadow-lg">
                    <h2 className="text-xl font-semibold mb-4 text-yellow-400">Safety & Rhythm</h2>
                    <div className="space-y-4">
                        <div>
                            <div className="text-gray-400 text-sm">Safety Policies</div>
                            <div className="text-2xl">{status.safety_state?.policy_count}</div>
                        </div>
                        <div>
                            <div className="text-gray-400 text-sm">Whitelist Entries</div>
                            <div className="text-2xl">{status.safety_state?.whitelist_count}</div>
                        </div>
                        <div>
                            <div className="text-gray-400 text-sm">Guardian Vows</div>
                            <div className="flex gap-2 mt-1">
                                {status.guardian_vows?.map(v => (
                                    <div key={v.subsystem} className={`w-3 h-3 rounded-full ${v.active ? 'bg-green-500' : 'bg-red-500'}`} title={v.subsystem}></div>
                                ))}
                            </div>
                        </div>
                    </div>
                </div>

                {/* Event Stream Card */}
                <div className="bg-gray-900 border border-gray-800 p-6 rounded-lg shadow-lg col-span-1 md:col-span-2 lg:col-span-1">
                    <h2 className="text-xl font-semibold mb-4 text-blue-400">Latest Event</h2>
                    {status.latest_event ? (
                        <div className="space-y-2">
                            <div className="text-lg font-bold">{status.latest_event.event_type}</div>
                            <div className="text-xs text-gray-500">{new Date(status.latest_event.created_at).toLocaleString()}</div>
                            <pre className="text-xs bg-black p-2 rounded overflow-x-auto text-green-300">
                                {JSON.stringify(status.latest_event.payload, null, 2)}
                            </pre>
                        </div>
                    ) : (
                        <div className="text-gray-500">No events logged.</div>
                    )}
                    <div className="mt-4 text-xs text-gray-600">Total Events: {status.event_stats?.total_events}</div>
                </div>

            </div>

            <PhaseLockPanel />
        </div>
    );
}
