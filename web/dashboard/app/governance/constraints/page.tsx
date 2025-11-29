'use client';

import { useConstraints } from '@/hooks/useConstraints';
import { formatDistanceToNow } from 'date-fns';

export default function ConstraintsPage() {
    const { constraints, violations, isLoading, isError } = useConstraints();

    if (isLoading) return <div className="p-8 text-zinc-400">Loading Constraints...</div>;
    if (isError) return <div className="p-8 text-red-400">Failed to load Constraints.</div>;

    return (
        <div className="p-8 max-w-6xl mx-auto">
            <h1 className="text-3xl font-bold mb-2 text-zinc-100">Guardian Constraints</h1>
            <p className="text-zinc-400 mb-8">Active operational boundaries and violation logs.</p>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                {/* Active Constraints */}
                <div>
                    <h2 className="text-xl font-semibold mb-4 text-emerald-400">Active Constraints</h2>
                    <div className="space-y-4">
                        {constraints?.map((c: any) => (
                            <div key={c.id} className="bg-zinc-900/50 border border-zinc-800 p-4 rounded-lg">
                                <div className="flex justify-between items-start mb-2">
                                    <span className="font-mono text-yellow-400 font-bold">{c.constraint_code}</span>
                                    <span className="text-xs uppercase tracking-wider bg-zinc-800 px-2 py-1 rounded text-zinc-400">{c.scope}</span>
                                </div>
                                <p className="text-zinc-300 text-sm mb-2">{c.description}</p>
                                <div className="bg-black/30 p-2 rounded font-mono text-xs text-zinc-500 overflow-x-auto">
                                    {c.rule_expression}
                                </div>
                            </div>
                        ))}
                    </div>
                </div>

                {/* Violation Log */}
                <div>
                    <h2 className="text-xl font-semibold mb-4 text-red-400">Recent Violations</h2>
                    <div className="space-y-4">
                        {violations?.length === 0 && (
                            <div className="text-zinc-500 italic">No recent violations recorded.</div>
                        )}
                        {violations?.map((v: any) => (
                            <div key={v.id} className="bg-red-950/20 border border-red-900/30 p-4 rounded-lg">
                                <div className="flex justify-between items-center mb-2">
                                    <span className="font-mono text-red-400 font-bold">{v.violated_constraint}</span>
                                    <span className="text-xs text-zinc-500">
                                        {formatDistanceToNow(new Date(v.created_at), { addSuffix: true })}
                                    </span>
                                </div>
                                <div className="flex gap-2 mb-2">
                                    <span className={`text-xs px-2 py-0.5 rounded uppercase font-bold ${v.severity === 'critical' ? 'bg-red-600 text-white' :
                                            v.severity === 'error' ? 'bg-orange-600 text-white' :
                                                'bg-zinc-700 text-zinc-300'
                                        }`}>
                                        {v.severity}
                                    </span>
                                </div>
                                <p className="text-zinc-300 text-sm">{v.notes}</p>
                                {v.guardian_action_id && (
                                    <div className="mt-2 text-xs font-mono text-zinc-600">
                                        Action ID: {v.guardian_action_id}
                                    </div>
                                )}
                            </div>
                        ))}
                    </div>
                </div>
            </div>
        </div>
    );
}
