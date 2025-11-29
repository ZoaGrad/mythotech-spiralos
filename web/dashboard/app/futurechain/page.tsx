'use client';

import { useEffect, useState } from 'react';

interface FutureChainNode {
    id: string;
    created_at: string;
    lattice_id: string;
    projected_timestep: number;
    projected_state: {
        original_probability: number;
        projected_probability: number;
        delta: number;
    };
    confidence: number;
    guardian_influence: string | null;
    integration_lattice: {
        lattice_state: string;
        collapse_probability: number;
    };
}

export default function FutureChainPage() {
    const [nodes, setNodes] = useState<FutureChainNode[]>([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchNodes = async () => {
            try {
                const res = await fetch('/api/futurechain');
                const data = await res.json();
                if (Array.isArray(data)) {
                    setNodes(data);
                }
            } catch (e) {
                console.error(e);
            } finally {
                setLoading(false);
            }
        };

        fetchNodes();
        const interval = setInterval(fetchNodes, 5000);
        return () => clearInterval(interval);
    }, []);

    if (loading) return <div className="p-8 text-white">Loading FutureChain...</div>;

    return (
        <div className="min-h-screen bg-black text-white p-8 font-mono">
            <h1 className="text-3xl font-bold mb-2 text-purple-400">Ω.8 FutureChain Horizon</h1>
            <p className="text-gray-400 mb-8">Recursive Forward Projection Timeline</p>

            <div className="space-y-4">
                {nodes.map((node) => (
                    <div key={node.id} className="border border-purple-900/50 bg-purple-900/10 p-4 rounded-lg flex items-center justify-between">
                        <div>
                            <div className="text-xs text-purple-300 mb-1">
                                {new Date(node.created_at).toLocaleTimeString()} | T+{node.projected_timestep}
                            </div>
                            <div className="flex items-center gap-4">
                                <span className={`px-2 py-0.5 rounded text-xs uppercase ${node.integration_lattice.lattice_state === 'stable' ? 'bg-green-900 text-green-300' :
                                        node.integration_lattice.lattice_state === 'critical' ? 'bg-red-900 text-red-300' :
                                            'bg-yellow-900 text-yellow-300'
                                    }`}>
                                    {node.integration_lattice.lattice_state}
                                </span>
                                <span className="text-gray-400">→</span>
                                <span className="text-sm">
                                    Prob: {node.projected_state.original_probability.toFixed(2)}
                                    <span className="text-gray-500 mx-2">→</span>
                                    <span className={node.projected_state.delta < 0 ? 'text-green-400' : 'text-red-400'}>
                                        {node.projected_state.projected_probability.toFixed(2)}
                                    </span>
                                </span>
                            </div>
                        </div>

                        <div className="text-right">
                            <div className="text-xs text-gray-500 uppercase tracking-wider mb-1">Guardian Influence</div>
                            <div className={`text-sm font-bold ${node.guardian_influence === 'stabilize' ? 'text-blue-400' :
                                    node.guardian_influence === 'escalate' ? 'text-red-500' :
                                        'text-gray-300'
                                }`}>
                                {node.guardian_influence || 'NONE'}
                            </div>
                            <div className="text-xs text-gray-600 mt-1">
                                Conf: {(node.confidence * 100).toFixed(0)}%
                            </div>
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
}
