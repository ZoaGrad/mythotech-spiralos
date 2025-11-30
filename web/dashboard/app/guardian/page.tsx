// web/dashboard/app/guardian/page.tsx
"use client";

import { useGuardianActions } from "../../hooks/useGuardianActions";
import { useAFRState } from "../../hooks/useAFRState";
import { useGuardianEffectiveness, EffectivenessRecord } from "../../hooks/useGuardianEffectiveness";

// ...

export default function GuardianPage() {
    const { data, error, loading } = useGuardianActions();
    const { afrMetrics } = useAFRState();
    const { records } = useGuardianEffectiveness();

    const effectiveness = records && records.length > 0
        ? records.reduce((acc: number, r: EffectivenessRecord) => acc + r.effectiveness_score, 0) / records.length
        : 0.85;

    return (
        <div className="p-8 max-w-7xl mx-auto">
            <h1 className="text-3xl font-bold mb-4 text-blue-400">
                Guardian Console (Ω.7.1)
            </h1>
            <p className="text-sm text-gray-400 mb-6">
                Action layer binding Integration Lattice to operational decisions.
            </p>

            <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
                {/* Existing metrics */}
                <EffectivenessCard effectiveness={effectiveness || 0.85} />

                {/* NEW: AFR Thermodynamic Governor */}
                <div className="bg-gray-900/50 border border-gray-800 rounded-lg p-4">
                    <h3 className="font-semibold text-lg mb-2 text-gray-300">AFR Governor</h3>
                    <div className="space-y-2 text-sm">
                        <div className="flex justify-between">
                            <span className="text-gray-400">Flux Vector:</span>
                            <span className="font-mono text-blue-300">{afrMetrics.fluxVectorNorm?.toFixed(4)}</span>
                        </div>
                        <div className="flex justify-between">
                            <span className="text-gray-400">Imperative:</span>
                            <span className={`font-mono ${afrMetrics.adjustmentImperative > 0.9 ? "text-red-500 font-bold" :
                                afrMetrics.adjustmentImperative > 0.7 ? "text-orange-400" : "text-green-400"
                                }`}>
                                {afrMetrics.adjustmentImperative?.toFixed(3)}
                            </span>
                        </div>
                    </div>
                </div>
            </div>

            {error && (
                <div className="mb-4 text-red-400 text-sm">
                    Error loading actions: {error.message}
                </div>
            )}

            {loading && !data && (
                <div className="text-gray-400 text-sm">Loading guardian actions…</div>
            )}

            {data && data.length > 0 && (
                <div className="overflow-x-auto rounded-lg border border-gray-800">
                    <table className="min-w-full text-sm">
                        <thead className="bg-gray-900/40">
                            <tr className="text-left">
                                <th className="px-3 py-2">Time</th>
                                <th className="px-3 py-2">Action</th>
                                <th className="px-3 py-2">Severity</th>
                                <th className="px-3 py-2">Lattice State</th>
                                <th className="px-3 py-2">Collapse Prob</th>
                                <th className="px-3 py-2">Recommendation</th>
                                <th className="px-3 py-2">Status</th>
                            </tr>
                        </thead>
                        <tbody>
                            {data.map((a) => (
                                <tr
                                    key={a.id}
                                    className="border-t border-gray-800 hover:bg-gray-900/40"
                                >
                                    <td className="px-3 py-2 text-xs text-gray-500">
                                        {new Date(a.created_at).toLocaleString()}
                                    </td>
                                    <td className="px-3 py-2">
                                        <span className={`px-2 py-0.5 rounded border text-xs uppercase ${actionClass(a.chosen_action)}`}>
                                            {a.chosen_action}
                                        </span>
                                    </td>
                                    <td className={`px-3 py-2 ${severityClass(a.severity)}`}>
                                        {a.severity}
                                    </td>
                                    <td className="px-3 py-2 uppercase text-xs font-mono">
                                        {a.lattice_state}
                                    </td>
                                    <td className="px-3 py-2 font-mono">
                                        {(a.collapse_probability * 100).toFixed(1)}%
                                    </td>
                                    <td className="px-3 py-2 text-xs italic text-gray-300">
                                        "{a.guardian_recommendation}"
                                    </td>
                                    <td className="px-3 py-2 text-xs text-gray-400 uppercase">
                                        {a.status}
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            )}

            {data && data.length === 0 && (
                <div className="text-gray-400 text-sm">
                    No guardian actions recorded yet.
                </div>
            )}
        </div>
    );
}
