'use client';
import { AFRGovernorPanel } from '../../components/AFRGovernorPanel';
import { HolonicAgentPanel } from '../../components/HolonicAgentPanel';
import { MarketControllerPanel } from '../../components/MarketControllerPanel';
import { ConstitutionalArbiterPanel } from '../../components/ConstitutionalArbiterPanel';
import { EffectivenessCard } from '../../components/EffectivenessCard';
import { CoherencePanel } from '../../components/CoherencePanel';
import { ScarIndexPanel } from '../../components/ScarIndexPanel';

export default function GuardianDashboard() {
    return (
        <div className="p-6 space-y-6 max-w-7xl mx-auto">
            <h1 className="text-2xl font-bold text-blue-400">Guardian System v1.5</h1>

            {/* Phase 1.5 Core Systems */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <AFRGovernorPanel />
                <MarketControllerPanel />
            </div>

            {/* Phase 2.0 Constitutional Intelligence */}
            <ConstitutionalArbiterPanel />

            {/* Holonic Agent Ecosystem */}
            <HolonicAgentPanel />

            {/* Legacy Systems */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <EffectivenessCard />
                <CoherencePanel />
                <ScarIndexPanel />
            </div>
        </div>
    );
}
