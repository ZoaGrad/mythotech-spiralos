// web/dashboard/app/collapse/page.tsx
"use client";

import { useCollapseHorizon } from "../../hooks/useCollapseHorizon";

const bandClass = (band?: string | null) => {
    switch (band) {
        case "CRITICAL":
            return "text-red-500 font-bold";
        case "HIGH":
            return "text-orange-500 font-semibold";
        case "MEDIUM":
            return "text-yellow-400";
        case "LOW":
            return "text-green-400";
        default:
            return "text-gray-400";
    }
};

export default function CollapsePage() {
    const { data, error, loading } = useCollapseHorizon();

    return (
        <div className="p-8 max-w-7xl mx-auto">
            <h1 className="text-3xl font-bold mb-4 text-rose-500">
                Collapse Horizon
            </h1>
            <p className="text-sm text-gray-400 mb-6">
                Projected collapse envelopes derived from high-risk paradox maps.
            </p>

            {error && (
                <div className="mb-4 text-red-400 text-sm">
                    Error loading collapse horizon: {error.message}
                </div>
            )}

            {loading && !data && (
                <div className="text-gray-400 text-sm">Loading collapse projections…</div>
            )}

            {data && data.length > 0 && (
                <div className="overflow-x-auto rounded-lg border border-gray-800">
                    <table className="min-w-full text-sm">
                        <thead className="bg-gray-900/40">
                            <tr className="text-left">
                                <th className="px-3 py-2">Created</th>
                                <th className="px-3 py-2">Collapse Risk</th>
                                <th className="px-3 py-2">Band</th>
                                <th className="px-3 py-2">Kind</th>
                                <th className="px-3 py-2">Horizon Window</th>
                                <th className="px-3 py-2">Paradox Risk</th>
                                <th className="px-3 py-2">Status</th>
                                <th className="px-3 py-2">Outcome</th>
                            </tr>
                        </thead>
                        <tbody>
                            {data.map((n) => (
                                <tr
                                    key={n.id}
                                    className="border-t border-gray-800 hover:bg-gray-900/40"
                                >
                                    <td className="px-3 py-2">
                                        {new Date(n.created_at).toLocaleString()}
                                    </td>
                                    <td className="px-3 py-2">
                                        {n.collapse_risk.toFixed(3)}
                                    </td>
                                    <td className={`px-3 py-2 ${bandClass(n.collapse_band)}`}>
                                        {n.collapse_band}
                                    </td>
                                    <td className="px-3 py-2 text-xs font-mono text-blue-300">
                                        {n.envelope_kind}
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
                                        {n.paradox_risk.toFixed(2)} <span className="text-gray-500">({n.paradox_risk_band})</span>
                                    </td>
                                    <td className="px-3 py-2 text-xs uppercase">
                                        {n.status}
                                    </td>
                                    <td className="px-3 py-2 text-xs">
                                        {n.realized_outcome ? (
                                            <span className={n.realized_outcome === 'collapse' ? 'text-red-500' : 'text-green-500'}>
                                                {n.realized_outcome}
                                            </span>
                                        ) : "—"}
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            )}

            {data && data.length === 0 && (
                <div className="text-gray-400 text-sm">
                    No collapse envelopes projected yet.
                </div>
            )}
        </div>
    );
}
