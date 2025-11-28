"use client";

import { usePhaseLock } from "../hooks/usePhaseLock";

export function PhaseLockPanel() {
    const { loading, error, result, runCheck } = usePhaseLock();

    const statusColor = result
        ? result.passed
            ? "bg-emerald-500/20 text-emerald-300 border-emerald-500/40"
            : "bg-rose-500/20 text-rose-300 border-rose-500/40"
        : "bg-slate-700/40 text-slate-200 border-slate-600/60";

    const statusLabel = result
        ? result.passed
            ? "PHASE-LOCK: STABLE"
            : "PHASE-LOCK: DIVERGED"
        : "PHASE-LOCK: UNKNOWN";

    return (
        <section className="mt-8 rounded-2xl border border-slate-700/60 bg-slate-900/60 p-6 shadow-lg shadow-slate-950/60">
            <div className="flex items-center justify-between gap-4">
                <div>
                    <h2 className="text-lg font-semibold text-slate-100">
                        Phase-Lock Integrity
                    </h2>
                    <p className="mt-1 text-sm text-slate-400">
                        Run an explicit integrity check against the constitutional baseline.
                    </p>
                </div>
                <button
                    onClick={runCheck}
                    disabled={loading}
                    className="rounded-xl border border-emerald-500/60 bg-emerald-500/10 px-4 py-2 text-sm font-medium text-emerald-200 hover:bg-emerald-500/20 disabled:cursor-wait disabled:opacity-60"
                >
                    {loading ? "Verifying…" : "Run Phase-Lock Check"}
                </button>
            </div>

            <div className="mt-4 flex flex-wrap items-center gap-3">
                <span
                    className={`inline-flex items-center rounded-full border px-3 py-1 text-xs font-semibold uppercase tracking-wide ${statusColor}`}
                >
                    {statusLabel}
                </span>
                {result && (
                    <span className="text-xs text-slate-400">
                        log: <span className="font-mono text-slate-300">{result.log_id}</span>
                    </span>
                )}
            </div>

            {error && (
                <div className="mt-4 rounded-xl border border-rose-500/40 bg-rose-950/40 p-3 text-sm text-rose-200">
                    {error}
                </div>
            )}

            {result && (
                <div className="mt-4 grid gap-4 md:grid-cols-3">
                    <div className="rounded-xl border border-slate-700/60 bg-slate-950/60 p-3">
                        <div className="text-xs font-semibold text-slate-400">
                            Expected Root Hash
                        </div>
                        <div className="mt-1 font-mono text-xs text-slate-200 break-all">
                            {result.expected_root_hash ?? "— (baseline created)"}
                        </div>
                    </div>
                    <div className="rounded-xl border border-slate-700/60 bg-slate-950/60 p-3">
                        <div className="text-xs font-semibold text-slate-400">
                            Actual Root Hash
                        </div>
                        <div className="mt-1 font-mono text-xs text-slate-200 break-all">
                            {result.actual_root_hash}
                        </div>
                    </div>
                    <div className="rounded-xl border border-slate-700/60 bg-slate-950/60 p-3">
                        <div className="text-xs font-semibold text-slate-400">
                            Checkpoint
                        </div>
                        <div className="mt-1 text-xs text-slate-200">
                            {result.checkpoint_id ? (
                                <>
                                    id:{" "}
                                    <span className="font-mono text-slate-300">
                                        {result.checkpoint_id}
                                    </span>
                                </>
                            ) : (
                                "No checkpoint linked (baseline created)."
                            )}
                        </div>
                    </div>
                </div>
            )}
        </section>
    );
}
