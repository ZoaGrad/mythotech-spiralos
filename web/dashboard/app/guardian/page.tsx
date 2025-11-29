// web/dashboard/app/guardian/page.tsx
"use client";

import { useGuardianActions } from "../../hooks/useGuardianActions";

const severityClass = (sev: number) => {
    if (sev >= 9) return "text-red-500 font-black";
    if (sev >= 7) return "text-orange-500 font-bold";
    if (sev >= 3) return "text-yellow-400 font-semibold";
    return "text-gray-400";
};

const actionClass = (action: string) => {
    switch (action) {
        case "escalate": return "bg-red-900/30 text-red-300 border-red-800";
        case "stabilize": return "bg-orange-900/30 text-orange-300 border-orange-800";
        case "alert": return "bg-yellow-900/30 text-yellow-300 border-yellow-800";
        default: return "bg-gray-800/50 text-gray-400 border-gray-700";
    }
};

export default function GuardianPage() {
    const { data, error, loading } = useGuardianActions();

    return (
        <div className="p-8 max-w-7xl mx-auto">
            <h1 className="text-3xl font-bold mb-4 text-blue-400">
                Guardian Console (Ω.7.1)
            </h1>
            <p className="text-sm text-gray-400 mb-6">
                Action layer binding Integration Lattice to operational decisions.
            </p>

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
