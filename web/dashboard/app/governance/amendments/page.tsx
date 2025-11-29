'use client';

import { useState } from 'react';
import { useAmendments } from '@/hooks/useAmendments';
import { formatDistanceToNow } from 'date-fns';

export default function AmendmentsPage() {
    const { amendments, isLoading, isError, mutate } = useAmendments();
    const [isProposing, setIsProposing] = useState(false);
    const [formData, setFormData] = useState({ title: '', proposal: '', rationale: '' });

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        try {
            await fetch('/api/governance/amendments', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(formData),
            });
            setFormData({ title: '', proposal: '', rationale: '' });
            setIsProposing(false);
            mutate(); // Refresh list
        } catch (err) {
            console.error(err);
        }
    };

    if (isLoading) return <div className="p-8 text-zinc-400">Loading Amendments...</div>;
    if (isError) return <div className="p-8 text-red-400">Failed to load Amendments.</div>;

    return (
        <div className="p-8 max-w-5xl mx-auto">
            <div className="flex justify-between items-center mb-8">
                <div>
                    <h1 className="text-3xl font-bold mb-2 text-zinc-100">Governance Amendments</h1>
                    <p className="text-zinc-400">Proposals to modify the Constitution or Constraints.</p>
                </div>
                <button
                    onClick={() => setIsProposing(!isProposing)}
                    className="bg-emerald-600 hover:bg-emerald-500 text-white px-4 py-2 rounded font-medium transition-colors"
                >
                    {isProposing ? 'Cancel Proposal' : 'New Proposal'}
                </button>
            </div>

            {isProposing && (
                <div className="mb-8 bg-zinc-900 border border-zinc-700 p-6 rounded-lg animate-in fade-in slide-in-from-top-4">
                    <h2 className="text-xl font-semibold mb-4 text-zinc-200">Draft Amendment</h2>
                    <form onSubmit={handleSubmit} className="space-y-4">
                        <div>
                            <label className="block text-sm font-medium text-zinc-400 mb-1">Title</label>
                            <input
                                type="text"
                                required
                                className="w-full bg-zinc-800 border border-zinc-700 rounded p-2 text-zinc-200 focus:ring-2 focus:ring-emerald-500 outline-none"
                                value={formData.title}
                                onChange={e => setFormData({ ...formData, title: e.target.value })}
                            />
                        </div>
                        <div>
                            <label className="block text-sm font-medium text-zinc-400 mb-1">Proposal Text</label>
                            <textarea
                                required
                                rows={4}
                                className="w-full bg-zinc-800 border border-zinc-700 rounded p-2 text-zinc-200 focus:ring-2 focus:ring-emerald-500 outline-none"
                                value={formData.proposal}
                                onChange={e => setFormData({ ...formData, proposal: e.target.value })}
                            />
                        </div>
                        <div>
                            <label className="block text-sm font-medium text-zinc-400 mb-1">Rationale</label>
                            <textarea
                                rows={2}
                                className="w-full bg-zinc-800 border border-zinc-700 rounded p-2 text-zinc-200 focus:ring-2 focus:ring-emerald-500 outline-none"
                                value={formData.rationale}
                                onChange={e => setFormData({ ...formData, rationale: e.target.value })}
                            />
                        </div>
                        <div className="flex justify-end">
                            <button type="submit" className="bg-emerald-600 hover:bg-emerald-500 text-white px-6 py-2 rounded font-medium">
                                Submit Proposal
                            </button>
                        </div>
                    </form>
                </div>
            )}

            <div className="space-y-6">
                {amendments?.length === 0 && (
                    <div className="text-center py-12 text-zinc-500 border border-dashed border-zinc-800 rounded-lg">
                        No amendments proposed yet.
                    </div>
                )}
                {amendments?.map((a: any) => (
                    <div key={a.id} className="bg-zinc-900/50 border border-zinc-800 p-6 rounded-lg">
                        <div className="flex justify-between items-start mb-4">
                            <div className="flex items-center gap-3">
                                <span className="bg-zinc-800 text-zinc-400 px-2 py-1 rounded text-sm font-mono">#{a.amendment_number}</span>
                                <h2 className="text-xl font-semibold text-zinc-200">{a.title}</h2>
                            </div>
                            <span className={`px-3 py-1 rounded-full text-xs font-bold uppercase tracking-wide ${a.status === 'approved' ? 'bg-emerald-900/50 text-emerald-400' :
                                    a.status === 'rejected' ? 'bg-red-900/50 text-red-400' :
                                        'bg-blue-900/50 text-blue-400'
                                }`}>
                                {a.status}
                            </span>
                        </div>

                        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                            <div>
                                <h3 className="text-xs font-bold text-zinc-500 uppercase mb-2">Proposal</h3>
                                <p className="text-zinc-300 text-sm leading-relaxed whitespace-pre-wrap">{a.proposal}</p>
                            </div>
                            <div>
                                <h3 className="text-xs font-bold text-zinc-500 uppercase mb-2">Rationale</h3>
                                <p className="text-zinc-400 text-sm leading-relaxed italic">{a.rationale || 'No rationale provided.'}</p>
                            </div>
                        </div>

                        <div className="mt-4 pt-4 border-t border-zinc-800 text-xs text-zinc-600 flex justify-between">
                            <span>Submitted {formatDistanceToNow(new Date(a.submitted_at), { addSuffix: true })}</span>
                            {a.decided_at && <span>Decided {formatDistanceToNow(new Date(a.decided_at), { addSuffix: true })}</span>}
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
}
