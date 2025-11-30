'use client';
import { useConstitutionalState } from '../hooks/useConstitutionalState';

export function ConstitutionalArbiterPanel() {
    const { proposedAmendments, cccSnapshots } = useConstitutionalState();
    const latestCCC = cccSnapshots[0];

    return (
        <div className="bg-white rounded-lg shadow p-6 border-l-4 border-l-indigo-500">
            <h3 className="text-lg font-semibold mb-4">Constitutional Arbiter</h3>

            {/* Amendment Proposals */}
            <div className="mb-6">
                <h4 className="font-medium text-gray-700 mb-3">Proposed Amendments</h4>
                <div className="space-y-3">
                    {proposedAmendments.map(amendment => (
                        <div key={amendment.id} className="border rounded-lg p-4 bg-blue-50">
                            <div className="flex justify-between items-start mb-2">
                                <h5 className="font-medium text-blue-900">{amendment.title}</h5>
                                <span className="text-xs bg-blue-200 text-blue-800 px-2 py-1 rounded">
                                    #{amendment.amendment_number}
                                </span>
                            </div>
                            <p className="text-sm text-blue-700 mb-2">{amendment.rationale}</p>
                            <div className="flex gap-2">
                                <button className="text-xs bg-green-500 text-white px-3 py-1 rounded hover:bg-green-600">
                                    Approve
                                </button>
                                <button className="text-xs bg-red-500 text-white px-3 py-1 rounded hover:bg-red-600">
                                    Reject
                                </button>
                                <button className="text-xs bg-gray-500 text-white px-3 py-1 rounded hover:bg-gray-600">
                                    Defer
                                </button>
                            </div>
                        </div>
                    ))}
                    {proposedAmendments.length === 0 && (
                        <p className="text-sm text-gray-500 text-center py-4">No proposed amendments</p>
                    )}
                </div>
            </div>

            {/* Constitutional Cognitive Context */}
            <div className="p-4 bg-indigo-50 rounded-lg">
                <h4 className="font-medium text-indigo-900 mb-2">Constitutional Cognitive Context</h4>
                {latestCCC ? (
                    <div className="space-y-2 text-sm">
                        <div className="flex justify-between">
                            <span>AFR Imperative:</span>
                            <span className="font-mono">{latestCCC.afr_adjustment_imperative?.toFixed(3)}</span>
                        </div>
                        <div className="flex justify-between">
                            <span>Amendment Type:</span>
                            <span className="font-mono">{latestCCC.proposed_amendment_type || 'None'}</span>
                        </div>
                        {latestCCC.constitutional_rationale && (
                            <div className="text-xs text-indigo-700 mt-2 p-2 bg-indigo-100 rounded">
                                {latestCCC.constitutional_rationale}
                            </div>
                        )}
                    </div>
                ) : (
                    <p className="text-sm text-indigo-700">No CCC data available</p>
                )}
            </div>
        </div>
    );
}
