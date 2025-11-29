// web/dashboard/app/lattice/page.tsx
"use client";

import { useFutureLattice } from "../../hooks/useFutureLattice";

const stateClass = (state: string) => {
    switch (state) {
        case "collapsed":
            return "text-red-600 font-black uppercase";
        case "critical":
            return "text-orange-500 font-bold uppercase";
        case "strained":
            return "text-yellow-400 font-semibold uppercase";
        case "stable":
            return "text-green-400 font-medium uppercase";
        default:
            return "text-gray-400";
    }
};

export default function LatticePage() {
    const { data, error, loading } = useFutureLattice();

    return (
        <div className="p-8 max-w-7xl mx-auto">
            <h1 className="text-3xl font-bold mb-4 text-purple-400">
                Integration Lattice (Ω.7)
            </h1>
            <p className="text-sm text-gray-400 mb-6">
                Unified recursive predictive continuum. Fusion → Paradox → Collapse → Future.
            </p>

            {error && (
                <div className="mb-4 text-red-400 text-sm">
                    Error loading lattice: {error.message}
                </div>
            )}

            {loading && !data && (
                <div className="text-gray-400 text-sm">Loading integration lattice…</div>
            )}

            {data && data.length > 0 && (
                <div className="overflow-x-auto rounded-lg border border-gray-800">
                    <table className="min-w-full text-sm">
                        <thead className="bg-gray-900/40">
                            <tr className="text-left">
                                <th className="px-3 py-2">Created</th>
                                <th className="px-3 py-2">Lattice State</th>
                                <th className="px-3 py-2">Collapse Prob</th>
                                <th className="px-3 py-2">Curvature</th>
                                <th className="px-3 py-2">Continuation</th>
                                <th className="px-3 py-2">Recommendation</th>
                                <th className="px-3 py-2">Horizon Window</th>
                                <th className="px-3 py-2">Paradox / Collapse</th>
                            </tr>
                        </thead>
                        <tbody>
                            {data.map((n) => (
                                <tr
                                    key={n.id}
                                    className="border-t border-gray-800 hover:bg-gray-900/40"
                                >
                                    <td className="px-3 py-2 text-xs text-gray-500">
                                        {new Date(n.created_at).toLocaleString()}
                                    </td>
                                    <td className={`px-3 py-2 ${stateClass(n.lattice_state)}`}>
                                        {n.lattice_state}
                                    </td>
                                    <td className="px-3 py-2 font-mono">
                                        {(n.collapse_probability * 100).toFixed(1)}%
                                    </td>
                                    <td className="px-3 py-2 font-mono text-xs">
                                        {n.curvature_risk.toFixed(3)}
                                    </td>
                                    <td className="px-3 py-2 font-mono text-xs text-blue-300">
                                        {(n.continuation_score * 100).toFixed(1)}%
                                    </td>
                                    <td className="px-3 py-2 text-xs italic text-gray-300">
                                        "{n.guardian_recommendation}"
                                    </td>
                                    <td className="px-3 py-2">
                                        <div className="flex flex-col">
                                            <span className="text-xs">
                                                {new Date(n.horizon_start).toLocaleTimeString()}
                                            </span>
                                            <span className="text-xs text-gray-500">
                                                → {new Date(n.horizon_end).toLocaleTimeString()}
                                            </span>
                                        </div>
                                    </td>
                                    <td className="px-3 py-2 text-xs">
                                        <div className="flex flex-col gap-1">
                                            {n.paradox_risk !== null && (
                                                <span className="text-gray-400">P: {n.paradox_risk.toFixed(2)} ({n.paradox_band})</span>
                                            )}
                                            {n.collapse_risk !== null && (
                                                <span className="text-gray-400">C: {n.collapse_risk.toFixed(2)} ({n.collapse_band})</span>
                                            )}
                                        </div>
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            )}

            {data && data.length === 0 && (
                <div className="text-gray-400 text-sm">
                    No lattice nodes integrated yet.
                </div>
            )}
        </div>
    );
}
