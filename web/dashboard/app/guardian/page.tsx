                </div >
            )}

{
    loading && !data && (
        <div className="text-gray-400 text-sm">Loading guardian actions…</div>
    )
}

{
    data && data.length > 0 && (
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
    )
}

{
    data && data.length === 0 && (
        <div className="text-gray-400 text-sm">
            No guardian actions recorded yet.
        </div>
    )
}
        </div >
    );
}
