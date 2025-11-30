'use client';
import { useGuardianEffectiveness, EffectivenessRecord } from '../hooks/useGuardianEffectiveness';

export function EffectivenessCard() {
    const { records } = useGuardianEffectiveness();
    const effectiveness = records && records.length > 0
        ? records.reduce((acc: number, r: EffectivenessRecord) => acc + r.effectiveness_score, 0) / records.length
        : 0.85;

    return (
        <div className="bg-white rounded-lg shadow p-4">
            <h3 className="text-sm font-semibold text-gray-500 mb-1">Effectiveness</h3>
            <div className="text-2xl font-mono text-green-600">
                {(effectiveness * 100).toFixed(1)}%
            </div>
        </div>
    );
}
