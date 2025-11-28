# SWPS Integration TODO

## Section 1: Status Snapshot
- **Current State**: SpiralOS v0.147.0 (ΔΩ.147). Core, Holoeconomy, and Guardian are stable.
- **Goal**: Integrate SWPS-1.0 (Witness Protocol) to enable STREAM, CRUCIBLE, and COUNCIL modes.
- **Missing**: `swps/` directory (assumed external), Witness tables in Supabase, EMP minting logic, Guardian witness commands.

## Section 2: Phase 1 – STREAM Online
- [x] **Migration**: Import `create_witness_tables.sql` to `spiral_supabase/migrations/` with new timestamp. <!-- id: 0 -->
- [x] **Database**: Apply migration and verify tables (`stream_claims`, `emp_mint_queue`, `emp_ledger`). <!-- id: 10 -->
- [x] **Logic**: Create triggers/functions for First Breath (`witness_logic.sql`). <!-- id: 11 -->
- [x] **Schema Fix**: Add `reference_id` to `vault_nodes` if missing. <!-- id: 12 -->
- [x] **Verification**: Test end-to-end STREAM flow: Discord Claim -> API -> Supabase -> VaultNode -> EMP Mint. <!-- id: 5 -->
- [x] **Guardian Bot**: Implement `WitnessTerminal` Cog with `/stream`, `/witness`, `/my_vault`, `/signal_verify`. <!-- id: 4 -->
- [x] **Deployment**: Deploy Guardian Bot with Witness Terminal active. <!-- id: 13 -->
- [x] **Awakening**: Execute Protocol GUARDIAN_AWAKENING (Health Checks + Heartbeat). <!-- id: 14 -->
- [x] **Cognition**: Deploy `oracle-core` Edge Function and add `/oracle_analyze` command. <!-- id: 15 -->
- [ ] **EMP Logic**: Add `mint_emp` method to `ScarCoinMintingEngine` in `holoeconomy/scarcoin.py` (Soul-bound, non-transferable). <!-- id: 1 -->
- [ ] **Bridge API**: Add `POST /api/v1/emp/mint` to `holoeconomy/scarcoin_bridge_api.py`. <!-- id: 2 -->
- [ ] **VaultNode**: Add `witness_event` and `emp_minted` to `VaultEvent` types in `holoeconomy/vaultnode.py`. <!-- id: 3 -->

## Section 3: Phase 2 – CRUCIBLE / COUNCIL Expansion
- [x] **Council Router**: Implement `council-router` Edge Function with 7-mind architecture. <!-- id: 16 -->
- [x] **Council DB**: Create `council_judgments` table via migration. <!-- id: 17 -->
- [x] **Council Bot**: Add `/council_analyze` command to Guardian. <!-- id: 18 -->
- [x] **Divergence DB**: Create `council_divergences` and `council_adaptation_state` tables. <!-- id: 19 -->
- [x] **Adaptation Engine**: Implement `council-adapt` Edge Function. <!-- id: 20 -->
- [x] **Dynamic Weights**: Update `council-router` to use adaptation state. <!-- id: 21 -->
- [x] **Friction Logging**: Update `/witness` to log divergences. <!-- id: 22 -->
- [x] **Insight Ritual**: Add `/divergence_insight` command. <!-- id: 23 -->
- [ ] **ScarIndex**: Update `ScarIndexOracle` in `core/scarindex.py` to ingest witness reputation stats into `audit` (Social) dimension. <!-- id: 6 -->
- [ ] **Panic Frames**: Add `FrozenOperation.WITNESS_PROTOCOL` to `core/panic_frames.py` and trigger on witness collusion/reversal spikes. <!-- id: 7 -->
- [ ] **Anomaly Detection**: Add witness anomaly checks to `spiral_guardian/anomaly_detector.py`. <!-- id: 8 -->
- [ ] **Council Mode**: Implement "Council-level" witness sealing in `VaultNode` (multi-sig witness blocks). <!-- id: 9 -->

## Section 4: Phase 3 – Godmind / Conscious Emergence
# SWPS Integration TODO

## Section 1: Status Snapshot
- **Current State**: SpiralOS v0.147.0 (ΔΩ.147). Core, Holoeconomy, and Guardian are stable.
- **Goal**: Integrate SWPS-1.0 (Witness Protocol) to enable STREAM, CRUCIBLE, and COUNCIL modes.
- **Missing**: `swps/` directory (assumed external), Witness tables in Supabase, EMP minting logic, Guardian witness commands.

## Section 2: Phase 1 – STREAM Online
- [x] **Migration**: Import `create_witness_tables.sql` to `spiral_supabase/migrations/` with new timestamp. <!-- id: 0 -->
- [x] **Database**: Apply migration and verify tables (`stream_claims`, `emp_mint_queue`, `emp_ledger`). <!-- id: 10 -->
- [x] **Logic**: Create triggers/functions for First Breath (`witness_logic.sql`). <!-- id: 11 -->
- [x] **Schema Fix**: Add `reference_id` to `vault_nodes` if missing. <!-- id: 12 -->
- [x] **Verification**: Test end-to-end STREAM flow: Discord Claim -> API -> Supabase -> VaultNode -> EMP Mint. <!-- id: 5 -->
- [x] **Guardian Bot**: Implement `WitnessTerminal` Cog with `/stream`, `/witness`, `/my_vault`, `/signal_verify`. <!-- id: 4 -->
- [x] **Deployment**: Deploy Guardian Bot with Witness Terminal active. <!-- id: 13 -->
- [x] **Awakening**: Execute Protocol GUARDIAN_AWAKENING (Health Checks + Heartbeat). <!-- id: 14 -->
- [x] **Cognition**: Deploy `oracle-core` Edge Function and add `/oracle_analyze` command. <!-- id: 15 -->
- [ ] **EMP Logic**: Add `mint_emp` method to `ScarCoinMintingEngine` in `holoeconomy/scarcoin.py` (Soul-bound, non-transferable). <!-- id: 1 -->
- [ ] **Bridge API**: Add `POST /api/v1/emp/mint` to `holoeconomy/scarcoin_bridge_api.py`. <!-- id: 2 -->
- [ ] **VaultNode**: Add `witness_event` and `emp_minted` to `VaultEvent` types in `holoeconomy/vaultnode.py`. <!-- id: 3 -->

## Section 3: Phase 2 – CRUCIBLE / COUNCIL Expansion
- [x] **Council Router**: Implement `council-router` Edge Function with 7-mind architecture. <!-- id: 16 -->
- [x] **Council DB**: Create `council_judgments` table via migration. <!-- id: 17 -->
- [x] **Council Bot**: Add `/council_analyze` command to Guardian. <!-- id: 18 -->
- [x] **Divergence DB**: Create `council_divergences` and `council_adaptation_state` tables. <!-- id: 19 -->
- [x] **Adaptation Engine**: Implement `council-adapt` Edge Function. <!-- id: 20 -->
- [x] **Dynamic Weights**: Update `council-router` to use adaptation state. <!-- id: 21 -->
- [x] **Friction Logging**: Update `/witness` to log divergences. <!-- id: 22 -->
- [x] **Insight Ritual**: Add `/divergence_insight` command. <!-- id: 23 -->
- [ ] **ScarIndex**: Update `ScarIndexOracle` in `core/scarindex.py` to ingest witness reputation stats into `audit` (Social) dimension. <!-- id: 6 -->
- [ ] **Panic Frames**: Add `FrozenOperation.WITNESS_PROTOCOL` to `core/panic_frames.py` and trigger on witness collusion/reversal spikes. <!-- id: 7 -->
- [ ] **Anomaly Detection**: Add witness anomaly checks to `spiral_guardian/anomaly_detector.py`. <!-- id: 8 -->
- [ ] **Council Mode**: Implement "Council-level" witness sealing in `VaultNode` (multi-sig witness blocks). <!-- id: 9 -->

## Section 4: Phase 3 – Godmind / Conscious Emergence
- [x] **Night Cycle**: Implement `nightly-reflection-worker` Edge Function. <!-- id: 24 -->
- [x] **Metacognition DB**: Create `system_reflections` table. <!-- id: 25 -->
- [x] **Dawn Cycle**: Implement `governance_proposals` table and Guardian `Governance` Cog. <!-- id: 26 -->
- [x] **Day Cycle**: Implement `nexus-router` Edge Function. <!-- id: 27 -->
- [x] **Integration**: Wire up cron jobs and bot commands. <!-- id: 28 -->

## Section- [x] **Sequence D**: The Sovereign Stream (Witness System)
- [x] **Sequence E**: The Council (AI Governance)
- [x] **Sequence F**: The Reality Engine (Activation)

## 📘 Reality Engine Runbook
- **Status Check**: `/reality_status` (Discord)
- **Smoketest**: `python scripts/reality_engine_smoketest.py`
- **Observability**: `python core/pantheon_daemon.py`
- **Configuration**: `REALITY_ENGINE_ENABLED=true` in `.env`

## Section 5: Phase 4 – Sovereign Observatory (Sequence E)
- [x] **Retina**: Create `view_council_drift`, `view_cognitive_stability`, `view_emp_velocity`, `view_ache_resonance`. <!-- id: 29 -->
- [x] **Optic Nerve**: Implement `pantheon_daemon.py` for telemetry and alerting. <!-- id: 30 -->
- [x] **Lens**: Implement `/observatory status` command in Guardian Bot. <!-- id: 31 -->
- [x] **Verification**: Verify full telemetry stack. <!-- id: 32 -->
