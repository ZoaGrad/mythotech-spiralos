'use client';

import React from 'react';
import { useGuardianEffectiveness } from '@/hooks/useGuardianEffectiveness';
import { format } from 'date-fns';

export default function EffectivenessPage() {
    const { records, isLoading, isError } = useGuardianEffectiveness();

    if (isLoading) return <div className="p-8 text-zinc-400">Loading effectiveness data...</div>;
    if (isError) return <div className="p-8 text-red-400">Failed to load effectiveness data.</div>;

    // Calculate summary stats
    const totalInterventions = records?.length || 0;
    const preventedCollapses = records?.filter(r => r.intervention_prevented_collapse).length || 0;
    const avgEffectiveness = totalInterventions > 0
        ? (records?.reduce((acc, curr) => acc + curr.effectiveness_score, 0) || 0) / totalInterventions
        : 0;

    return (
        <div className="p-8 max-w-7xl mx-auto space-y-8">
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-3xl font-bold text-zinc-100 tracking-tight">Intervention Effectiveness</h1>
                    <p className="text-zinc-400 mt-2">Analysis of Guardian actions vs. actual outcomes.</p>
                </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div className="bg-zinc-900/50 border border-zinc-800 p-6 rounded-xl">
                    <div className="text-zinc-500 text-sm uppercase tracking-wider mb-2">Total Interventions</div>
                    <div className="text-3xl font-mono text-zinc-100">{totalInterventions}</div>
                </div>
                <div className="bg-zinc-900/50 border border-zinc-800 p-6 rounded-xl">
                    <div className="text-zinc-500 text-sm uppercase tracking-wider mb-2">Collapses Prevented</div>
                    <div className="text-3xl font-mono text-emerald-400">{preventedCollapses}</div>
                </div>
                <div className="bg-zinc-900/50 border border-zinc-800 p-6 rounded-xl">
                    <div className="text-zinc-500 text-sm uppercase tracking-wider mb-2">Avg Effectiveness</div>
                    <div className="text-3xl font-mono text-blue-400">{(avgEffectiveness * 100).toFixed(1)}%</div>
                </div>
            </div>

            <div className="border border-zinc-800 rounded-xl overflow-hidden bg-zinc-900/30">
                <table className="w-full text-left text-sm">
                    <thead className="bg-zinc-900/80 text-zinc-400 uppercase tracking-wider text-xs border-b border-zinc-800">
                        <tr>
                            <th className="px-6 py-4 font-medium">Action</th>
                            <th className="px-6 py-4 font-medium">Predicted State</th>
                            <th className="px-6 py-4 font-medium">Actual State</th>
                            <th className="px-6 py-4 font-medium">Outcome</th>
                            <th className="px-6 py-4 font-medium">Score</th>
                            <th className="px-6 py-4 font-medium">Time</th>
                        </tr>
                    </thead>
                    <tbody className="divide-y divide-zinc-800/50">
                        {records?.map((record) => (
                            <tr key={record.action_id} className="hover:bg-zinc-800/20 transition-colors">
                                <td className="px-6 py-4">
                                    <div className="font-medium text-zinc-200">{record.chosen_action}</div>
                                    <div className="text-xs text-zinc-500 mt-1">Sev: {record.severity}</div>
                                </td>
                                <td className="px-6 py-4 font-mono text-zinc-400 text-xs">
                                    {record.predicted_state}
                                </td>
                                <td className="px-6 py-4 font-mono text-zinc-400 text-xs">
                                    {record.actual_state}
                                </td>
                                <td className="px-6 py-4">
                                    {record.intervention_prevented_collapse ? (
                                        <span className="px-2 py-1 rounded-full bg-emerald-900/30 text-emerald-400 text-xs border border-emerald-800">
                                            Collapse Prevented
                                        </span>
                                    ) : (
                                        <span className="text-zinc-500 text-xs">Recorded</span>
                                    )}
                                </td>
                                <td className="px-6 py-4 font-mono">
                                    <div className="flex items-center gap-2">
                                        <div className="w-16 h-1.5 bg-zinc-800 rounded-full overflow-hidden">
                                            <div
                                                className={`h-full ${record.effectiveness_score > 0.7 ? 'bg-emerald-500' : record.effectiveness_score > 0.3 ? 'bg-amber-500' : 'bg-red-500'}`}
                                                style={{ width: `${record.effectiveness_score * 100}%` }}
                                            />
                                        </div>
                                        <span className="text-zinc-300">{record.effectiveness_score.toFixed(2)}</span>
                                    </div>
                                </td>
                                <td className="px-6 py-4 text-zinc-500 text-xs">
                                    {format(new Date(record.action_taken_at), 'MMM dd HH:mm')}
                                </td>
                            </tr>
                        ))}
                        {records?.length === 0 && (
                            <tr>
                                <td colSpan={6} className="px-6 py-8 text-center text-zinc-500">
                                    No effectiveness records found.
                                </td>
                            </tr>
                        )}
                    </tbody>
                </table>
            </div>
        </div>
    );
}
