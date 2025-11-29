"use client";

import React from "react";
import { useCausalityMesh } from "../../hooks/useCausalityMesh";
import { useCausalityTension } from "../../hooks/useCausalityTension";

export default function CausalityPage() {
    const { links, loading, error } = useCausalityMesh();
    const { nodes, loading: tensionLoading, error: tensionError } = useCausalityTension();

    return (
        <div className="p-8 bg-black min-h-screen text-gray-200 font-mono">
            <header className="mb-8 border-b border-gray-800 pb-4">
                <h1 className="text-3xl font-bold text-purple-400 mb-2">
                    Ω.6-A — Causality Mesh
                </h1>
                <p className="text-sm text-gray-500">
                    Directed causal links between audit events.
                </p>
            </header>

            {loading && <div className="text-yellow-500 animate-pulse">Loading mesh topology...</div>}
            {error && <div className="text-red-500">Error: {error}</div>}

            {!loading && !error && (
                <div className="overflow-x-auto mb-12">
                    <table className="w-full text-left border-collapse">
                        <thead>
                            <tr className="text-xs text-gray-500 uppercase border-b border-gray-800">
                                <th className="p-2">Time</th>
                                <th className="p-2">Cause Type</th>
                                <th className="p-2">Source Event</th>
                                <th className="p-2">Target Event</th>
                                <th className="p-2">Weight</th>
                                <th className="p-2">Phase Lock</th>
                            </tr>
                        </thead>
                        <tbody>
                            {links.map((link) => (
                                <tr
                                    key={link.id}
                                    className="border-b border-gray-900 hover:bg-gray-900/50 transition-colors"
                                >
                                    <td className="p-2 text-xs text-gray-500 whitespace-nowrap">
                                        {new Date(link.created_at).toLocaleTimeString()}
                                    </td>
                                    <td className="p-2 text-purple-300 font-bold">
                                        {link.cause_type}
                                    </td>
                                    <td className="p-2">
                                        <div className="text-xs text-blue-400">
                                            {link.source_component}
                                        </div>
                                        <div className="text-xs text-gray-400">
                                            {link.source_event_type}
                                        </div>
                                    </td>
                                    <td className="p-2">
                                        <div className="text-xs text-green-400">
                                            {link.target_component}
                                        </div>
                                        <div className="text-xs text-gray-400">
                                            {link.target_event_type}
                                        </div>
                                    </td>
                                    <td className="p-2 text-xs">
                                        {link.weight.toFixed(2)}
                                    </td>
                                    <td className="p-2 text-xs font-mono text-gray-600">
                                        {link.phase_lock_hash ? link.phase_lock_hash.substring(0, 8) + "..." : "-"}
                                    </td>
                                </tr>
                            ))}
                            {links.length === 0 && (
                                <tr>
                                    <td colSpan={6} className="p-8 text-center text-gray-600">
                                        No causal links detected in the mesh.
                                    </td>
                                </tr>
                            )}
                        </tbody>
                    </table>
                </div>
            )}

            <section className="mt-10 border-t border-gray-800 pt-8">
                <h2 className="text-xl font-semibold text-purple-300 mb-3">
                    High-Tension Nodes
                </h2>
                {tensionLoading && (
                    <div className="text-yellow-500 animate-pulse">
                        Computing mesh tension…
                    </div>
                )}
                {tensionError && (
                    <div className="text-red-500">Error: {tensionError}</div>
                )}
                {!tensionLoading && !tensionError && (
                    <div className="overflow-x-auto">
                        <table className="w-full text-left border-collapse text-xs">
                            <thead>
                                <tr className="border-b border-gray-800 text-gray-500 uppercase">
                                    <th className="p-2">Event Type</th>
                                    <th className="p-2">Component</th>
                                    <th className="p-2">Severity</th>
                                    <th className="p-2">Total Weight</th>
                                    <th className="p-2">Mesh Tension</th>
                                    <th className="p-2">Last Seen</th>
                                </tr>
                            </thead>
                            <tbody>
                                {nodes.map((n) => (
                                    <tr key={n.event_id} className="border-b border-gray-900">
                                        <td className="p-2">{n.event_type}</td>
                                        <td className="p-2">{n.component}</td>
                                        <td className="p-2">
                                            <span className={
                                                n.severity_dominant === "RED"
                                                    ? "text-red-400"
                                                    : n.severity_dominant === "YELLOW"
                                                        ? "text-yellow-400"
                                                        : n.severity_dominant === "GREEN"
                                                            ? "text-green-400"
                                                            : "text-gray-400"
                                            }>
                                                {n.severity_dominant || "UNKNOWN"}
                                            </span>
                                        </td>
                                        <td className="p-2">{n.total_weight_norm.toFixed(3)}</td>
                                        <td className="p-2">{n.mesh_tension_max.toFixed(3)}</td>
                                        <td className="p-2">
                                            {new Date(n.latest_event_at).toLocaleString()}
                                        </td>
                                    </tr>
                                ))}
                                {nodes.length === 0 && (
                                    <tr>
                                        <td colSpan={6} className="p-8 text-center text-gray-600">
                                            No high-tension nodes detected.
                                        </td>
                                    </tr>
                                )}
                            </tbody>
                        </table>
                    </div>
                )}
            </section>
        </div>
    );
}
