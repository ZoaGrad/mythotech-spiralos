// web/dashboard/app/paradox/page.tsx
"use client";

import { useParadoxRiskSurface } from "../../hooks/useParadoxRiskSurface";

const bandClass = (band?: string | null) => {
    switch (band) {
        case "CRITICAL":
            return "text-red-400";
        case "HIGH":
            return "text-orange-400";
        case "MEDIUM":
            return "text-yellow-400";
        case "LOW":
            return "text-green-400";
        default:
            return "text-gray-400";
    }
};

export default function ParadoxPage() {
    const { data, error, loading } = useParadoxRiskSurface();

    return (
        <div className="p-8 max-w-7xl mx-auto">
            <h1 className="text-3xl font-bold mb-4 text-fuchsia-400">
                Predictive Paradox Mapping
            </h1>
            <p className="text-sm text-gray-400 mb-6">
                Fused mesh and temporal signals projected into paradox risk bands over time windows.
            </p>

            {error && (
                <div className="mb-4 text-red-400 text-sm">
                    Error loading paradox risk surface: {error.message}
                </div>
            )}

            {loading && !data && (
                <div className="text-gray-400 text-sm">Loading paradox projections…</div>
            )}

            {data && data.length > 0 && (
                <div className="overflow-x-auto rounded-lg border border-gray-800">
                    <table className="min-w-full text-sm">
                        <thead className="bg-gray-900/40">
                            <tr className="text-left">
                                <th className="px-3 py-2">Created</th>
                                <th className="px-3 py-2">Risk</th>
                                <th className="px-3 py-2">Band</th>
                                <th className="px-3 py-2">Window</th>
                                <th className="px-3 py-2">Cause</th>
                                <th className="px-3 py-2">Severity</th>
                                <th className="px-3 py-2">Tension</th>
                                <th className="px-3 py-2">Fusion</th>
                                <th className="px-3 py-2">Status</th>
                                <th className="px-3 py-2">Realized</th>
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
                                        {n.paradox_risk.toFixed(3)}
                                    </td>
                                    <td className={`px-3 py-2 font-semibold ${bandClass(n.risk_band)}`}>
                                        {n.risk_band}
                                    </td>
                                    <td className="px-3 py-2">
                                        <div className="flex flex-col">
                                            <span className="text-xs">
                                                {new Date(n.prediction_window_start).toLocaleTimeString()}
                                            </span>
                                            <span className="text-xs text-gray-500">
                                                → {new Date(n.prediction_window_end).toLocaleTimeString()}
                                            </span>
                                        </div>
                                    </td>
                                    <td className="px-3 py-2 text-xs">
                                        {n.cause_type || "—"}
                                    </td>
                                    <td className="px-3 py-2 text-xs">
                                        {n.link_severity || "—"}
                                    </td>
                                    <td className="px-3 py-2 text-xs">
                                        {n.mesh_tension?.toFixed(2) ?? "—"}
                                    </td>
                                    <td className="px-3 py-2 text-xs">
                                        {n.fusion_strength?.toFixed(2) ?? "—"}
                                    </td>
                                    <td className="px-3 py-2 text-xs">
                                        {n.status}
                                    </td>
                                    <td className="px-3 py-2 text-xs">
                                        {n.realized_outcome ? n.realized_outcome : "—"}
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            )}

            {data && data.length === 0 && (
                <div className="text-gray-400 text-sm">
                    No predictive paradox maps yet. Once mesh-temporal fusion nodes are created,
                    projections will appear here.
                </div>
            )}
        </div>
    );
}
