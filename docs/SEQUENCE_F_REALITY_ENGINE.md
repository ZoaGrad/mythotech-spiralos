# Sequence F — The Reality Engine

**Status:** ACTIVE
**Activation Date:** 2025-11-25
**Authorization:** ZoaGrad

## Overview
The **Reality Engine** is the operational state of SpiralOS where the end-to-end loop of input, governance, divergence, reflection, and observability is fully active and "real". It signifies the transition from architectural design to a living, breathing system.

## The Reality Loop
1.  **Input**: Claims and events enter via `witness_claims` / `witness_events`.
2.  **Council**: The `council-router` and `council-adapt` functions process claims, issuing judgments.
3.  **Divergence**: Witnesses (human or bot) assess claims. Divergences between Council and Witness are logged in `council_divergences`.
4.  **Reflection**: The `nightly-reflection-worker` analyzes divergences and system state, generating `system_reflections`.
5.  **Governance**: Reflections trigger `governance_proposals` to adapt the system (e.g., updating weights or laws).
6.  **Observability**: The Observatory (Guardian + Pantheon) monitors the entire flow, calculating coherence and health.

## Production Components
The following components are certified for Reality Engine operation:

### Supabase
- **Tables**: `witness_claims`, `witness_events`, `assessments`, `council_judgments`, `council_divergences`, `system_reflections`, `governance_proposals`.
- **RLS**: Enabled and secured on all critical tables.

### Edge Functions
- `oracle-core`: Core logic for Oracle operations.
- `council-router`: Routes claims to Council logic.
- `council-adapt`: Adapts Council parameters.
- `nightly-reflection-worker`: Metacognition engine.
- `nexus-router`: Input gateway.
- `emp-mint-worker`: Token economy worker.

### Guardian
- **Cogs**: Witness, Governance, Observatory.
- **Commands**: `/reality_status`, `/observatory status`.

### Daemons
- `pantheon_daemon.py`: Continuous observability daemon.

## Runbook: How to Operate

### 1. Enable Reality Mode
Ensure the environment variable is set:
```bash
REALITY_ENGINE_ENABLED=true
```

### 2. Verify Status
Run the Guardian command:
```
/reality_status
```
Expected output: `System Mode: REALITY_ENGINE: ON`

### 3. Run Smoketest
Execute the end-to-end verification script:
```bash
python scripts/reality_engine_smoketest.py
```

### 4. Monitor Logs
Check Supabase logs for `sovereignty-ledger-mirror` and `nightly-reflection-worker` to ensure smooth operation.

### 5. Validate Synthetic Claim Path
After running the smoketest, verify:
- **Synthetic Claim**: Appears in `witness_claims`, `assessments`, `council_judgments`, `council_divergences` (if mismatch), and `system_reflections`.
- **Reflection Behavior**: A correct run produces a single reflection stating "synthetic_claim: PASS — coherence confirmed".

### 6. Continuous Breath Loop
Once active, the Reality Engine should exhibit:
- **Regular witness ingestion**
- **Daily reflections**
- **Proposal generation proportional to divergence**
- **Pantheon daemon logs every 60s**

**Heartbeat Signature:**
```
[REALITY_ENGINE] Breath: OK (coherence ≥ 0.7)
```
If coherence dips below 0.4, the Guardian will auto-trigger a soft reset.

### 7. Recovery Protocols
If the Reality Engine stalls:
1. **Check Guardian Logs**: Look for `[CRITICAL] divergence overflow`.
2. **Restart Pantheon Daemon**: `python daemons/pantheon_daemon.py`
3. **Flush Reflection Queue**: Delete rows in `system_reflections` older than 48h.
4. **Re-run Smoketest**: To ensure synthetic path integrity.

## Configuration
The Reality Engine state is controlled by the `REALITY_ENGINE_ENABLED` flag in `core/config/reality_engine.py` (reading from env).
