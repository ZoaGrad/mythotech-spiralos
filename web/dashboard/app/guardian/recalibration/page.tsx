'use client';

import React from 'react';
import { useRecalibrationLog } from '@/hooks/useRecalibrationLog';
import { format } from 'date-fns';

export default function RecalibrationPage() {
    const { logs, isLoading, isError } = useRecalibrationLog();

    if (isLoading) return <div className="p-8 text-zinc-400">Loading recalibration data...</div>;
    if (isError) return <div className="p-8 text-red-400">Failed to load recalibration data.</div>;

    return (
        <div className="p-8 max-w-7xl mx-auto space-y-8">
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-3xl font-bold text-zinc-100 tracking-tight">Adaptive Recalibration Log</h1>
                    <p className="text-zinc-400 mt-2">History of Guardian trust index adjustments and calibration errors.</p>
                </div>
                <div className="bg-zinc-900/50 border border-zinc-800 rounded-lg px-4 py-2">
                    <span className="text-zinc-500 text-sm uppercase tracking-wider mr-2">Latest Trust Index</span>
                    <span className="text-emerald-400 font-mono text-xl">
                        {logs && logs.length > 0 ? logs[0].new_trust_index.toFixed(3) : 'N/A'}
                    </span>
                </div>
            </div>

            <div className="border border-zinc-800 rounded-xl overflow-hidden bg-zinc-900/30">
                <table className="w-full text-left text-sm">
                    <thead className="bg-zinc-900/80 text-zinc-400 uppercase tracking-wider text-xs border-b border-zinc-800">
                        <tr>
                            <th className="px-6 py-4 font-medium">Recalibrated At</th>
                            <th className="px-6 py-4 font-medium">Window</th>
                            <th className="px-6 py-4 font-medium">Trust Index Δ</th>
                            <th className="px-6 py-4 font-medium">Error</th>
                            <th className="px-6 py-4 font-medium">Reason</th>
                            <th className="px-6 py-4 font-medium">Notes</th>
                        </tr>
                    </thead>
                    <tbody className="divide-y divide-zinc-800/50">
                        {logs?.map((log) => (
                            <tr key={log.id} className="hover:bg-zinc-800/20 transition-colors">
                                <td className="px-6 py-4 font-mono text-zinc-300">
                                    {format(new Date(log.recalibrated_at), 'MMM dd HH:mm:ss')}
                                </td>
                                <td className="px-6 py-4 text-zinc-400 text-xs">
                                    {format(new Date(log.window_start), 'HH:mm')} - {format(new Date(log.window_end), 'HH:mm')}
                                </td>
                                <td className="px-6 py-4 font-mono">
                                    <span className="text-zinc-500">{log.previous_trust_index.toFixed(3)}</span>
                                    <span className="mx-2 text-zinc-600">→</span>
                                    <span className={log.new_trust_index >= log.previous_trust_index ? 'text-emerald-400' : 'text-amber-400'}>
                                        {log.new_trust_index.toFixed(3)}
                                    </span>
                                </td>
                                <td className="px-6 py-4 font-mono text-zinc-300">
                                    {log.calibration_error.toFixed(4)}
                                </td>
                                <td className="px-6 py-4 text-zinc-400">
                                    <span className="px-2 py-1 rounded-full bg-zinc-800 text-xs border border-zinc-700">
                                        {log.trigger_reason}
                                    </span>
                                </td>
                                <td className="px-6 py-4 text-zinc-500 italic truncate max-w-xs">
                                    {log.notes}
                                </td>
                            </tr>
                        ))}
                        {logs?.length === 0 && (
                            <tr>
                                <td colSpan={6} className="px-6 py-8 text-center text-zinc-500">
                                    No recalibration logs found.
                                </td>
                            </tr>
                        )}
                    </tbody>
                </table>
            </div>
        </div>
    );
}
