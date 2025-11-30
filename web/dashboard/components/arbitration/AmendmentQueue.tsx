'use client';

interface Amendment {
    id: string;
    amendment_number: number;
    title: string;
    proposal_text: string;
    rationale: string;
    status: string;
    proposed_at: string;
    trigger_conditions: any;
    ccc_id: string;
}

interface AmendmentQueueProps {
    amendments: Amendment[];
    onArbitrationDecision: (amendmentId: string, decision: 'ratify' | 'veto') => void;
}

export function AmendmentQueue({ amendments, onArbitrationDecision }: AmendmentQueueProps) {
    const proposedAmendments = amendments.filter(a => a.status === 'proposed');

    if (proposedAmendments.length === 0) {
        return (
            <div className="bg-white rounded-lg shadow p-6">
                <h3 className="text-lg font-semibold mb-4">Amendment Queue</h3>
                <div className="text-center py-8 text-gray-500">
                    <p>No amendments pending review</p>
                    <p className="text-sm mt-2">Amendments will appear here when constitutional triggers are met</p>
                </div>
            </div>
        );
    }

    return (
        <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-semibold mb-4">Amendment Queue</h3>

            <div className="space-y-4">
                {proposedAmendments.map((amendment) => (
                    <div key={amendment.id} className="border border-gray-200 rounded-lg p-4">
                        <div className="flex justify-between items-start mb-3">
                            <div>
                                <h4 className="font-medium text-gray-900">{amendment.title}</h4>
                                <div className="flex items-center space-x-2 mt-1">
                                    <span className="text-xs bg-blue-100 text-blue-800 px-2 py-1 rounded">
                                        #{amendment.amendment_number}
                                    </span>
                                    <span className="text-xs text-gray-500">
                                        {new Date(amendment.proposed_at).toLocaleDateString()}
                                    </span>
                                </div>
                            </div>
                        </div>

                        <div className="mb-3">
                            <p className="text-sm text-gray-700">{amendment.rationale}</p>
                        </div>

                        <div className="mb-3">
                            <div className="text-xs text-gray-500 mb-1">Trigger Conditions:</div>
                            <div className="text-xs font-mono bg-gray-50 p-2 rounded">
                                AFR: {amendment.trigger_conditions?.afr_imperative?.toFixed(3) || 'N/A'}
                            </div>
                        </div>

                        <div className="flex space-x-2">
                            <button
                                onClick={() => onArbitrationDecision(amendment.id, 'ratify')}
                                className="flex-1 bg-green-500 text-white py-2 px-4 rounded text-sm font-medium hover:bg-green-600 transition-colors"
                            >
                                Ratify
                            </button>
                            <button
                                onClick={() => onArbitrationDecision(amendment.id, 'veto')}
                                className="flex-1 bg-red-500 text-white py-2 px-4 rounded text-sm font-medium hover:bg-red-600 transition-colors"
                            >
                                Veto
                            </button>
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
}
