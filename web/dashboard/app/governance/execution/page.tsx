'use client';

import useSWR from 'swr';
import { formatDistanceToNow } from 'date-fns';
import { useState } from 'react';

const fetcher = (url: string) => fetch(url).then((res) => res.json());

export default function ExecutionPage() {
    const { data: logs, error, isLoading } = useSWR('/api/governance/execution', fetcher, { refreshInterval: 5000 });
    const [selectedLog, setSelectedLog] = useState<any>(null);

    if (isLoading) return <div className="p-8 text-zinc-400">Loading Execution Logs...</div>;
    if (error) return <div className="p-8 text-red-400">Failed to load logs.</div>;

    return (
        <div className="p-8 max-w-7xl mx-auto">
            <h1 className="text-3xl font-bold mb-2 text-zinc-100">Constitutional Execution Engine</h1>
            <p className="text-zinc-400 mb-8">Real-time enforcement of constitutional law.</p>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                {/* Execution Log List */}
                <div className="lg:col-span-1 space-y-4 h-[80vh] overflow-y-auto pr-2">
                    <h2 className="text-xl font-semibold mb-4 text-zinc-200">Execution Log</h2>
                    {logs?.map((log: any) => (
                        <div
                            key={log.id}
                            onClick={() => setSelectedLog(log)}
                            className={`p-4 rounded-lg border cursor-pointer transition-colors ${selectedLog?.id === log.id
                                    ? 'bg-zinc-800 border-emerald-500'
                                    : 'bg-zinc-900/50 border-zinc-800 hover:bg-zinc-800'
                                }`}
                        >
                            <div className="flex justify-between items-center mb-2">
                                <span className={`text-xs font-bold px-2 py-0.5 rounded uppercase ${log.vetoed ? 'bg-red-900 text-red-400' :
                                        log.rewritten ? 'bg-yellow-900 text-yellow-400' :
                                            'bg-emerald-900 text-emerald-400'
                                    }`}>
                                    {log.vetoed ? 'VETOED' : log.rewritten ? 'REWRITTEN' : 'EXECUTED'}
                                </span>
                                <span className="text-xs text-zinc-500">
                                    {formatDistanceToNow(new Date(log.timestamp), { addSuffix: true })}
                                </span>
                            </div>
                            <div className="text-xs font-mono text-zinc-600 truncate mb-1">
                                ID: {log.action_id}
                            </div>
                            {log.notes && (
                                <p className="text-sm text-zinc-400 line-clamp-2">{log.notes}</p>
                            )}
                        </div>
                    ))}
                </div>

                {/* Trace Explorer */}
                <div className="lg:col-span-2 bg-zinc-900 border border-zinc-800 rounded-lg p-6 h-[80vh] overflow-y-auto">
                    <h2 className="text-xl font-semibold mb-6 text-zinc-200">Constitutional Trace Explorer</h2>

                    {selectedLog ? (
                        <div className="space-y-8">
                            {/* Header Info */}
                            <div className="flex gap-4 items-center pb-6 border-b border-zinc-800">
                                <div className={`w-16 h-16 rounded-full flex items-center justify-center text-2xl ${selectedLog.vetoed ? 'bg-red-900/20 text-red-500' :
                                        selectedLog.rewritten ? 'bg-yellow-900/20 text-yellow-500' :
                                            'bg-emerald-900/20 text-emerald-500'
                                    }`}>
                                    {selectedLog.vetoed ? '🚫' : selectedLog.rewritten ? '✏️' : '✅'}
                                </div>
                                <div>
                                    <div className="text-sm text-zinc-500 uppercase tracking-wider font-bold">Outcome</div>
                                    <div className="text-2xl font-bold text-zinc-100">
                                        {selectedLog.vetoed ? 'Action Vetoed' : selectedLog.rewritten ? 'Action Rewritten' : 'Action Allowed'}
                                    </div>
                                    <div className="text-zinc-400 text-sm mt-1">{selectedLog.notes}</div>
                                </div>
                            </div>

                            {/* Applied Constraints */}
                            <div>
                                <h3 className="text-sm font-bold text-zinc-500 uppercase mb-3">Applied Constraints</h3>
                                <div className="space-y-2">
                                    {JSON.parse(selectedLog.applied_constraints || '[]').length === 0 ? (
                                        <div className="text-zinc-600 italic">No constraints violated.</div>
                                    ) : (
                                        JSON.parse(selectedLog.applied_constraints || '[]').map((c: any, i: number) => (
                                            <div key={i} className="bg-red-950/30 border border-red-900/50 p-3 rounded flex gap-3 items-start">
                                                <span className="font-mono text-red-400 font-bold">{c.constraint_code}</span>
                                                <span className="text-zinc-300 text-sm">{c.description}</span>
                                            </div>
                                        ))
                                    )}
                                </div>
                            </div>

                            {/* Validation Path */}
                            <div>
                                <h3 className="text-sm font-bold text-zinc-500 uppercase mb-3">Validation Path</h3>
                                <div className="bg-black/30 p-4 rounded font-mono text-xs text-zinc-400 overflow-x-auto">
                                    {selectedLog.validation_path}
                                </div>
                            </div>

                            {/* Raw Data */}
                            <div>
                                <h3 className="text-sm font-bold text-zinc-500 uppercase mb-3">Raw Log Data</h3>
                                <pre className="bg-black/30 p-4 rounded font-mono text-xs text-zinc-500 overflow-x-auto">
                                    {JSON.stringify(selectedLog, null, 2)}
                                </pre>
                            </div>
                        </div>
                    ) : (
                        <div className="h-full flex flex-col items-center justify-center text-zinc-600">
                            <div className="text-4xl mb-4">🔍</div>
                            <p>Select an execution event to trace its constitutional path.</p>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
}
