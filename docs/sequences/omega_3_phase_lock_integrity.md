# Ω.3 — Phase-Lock Integrity Engine

**Status:** Draft → Implemented → Activated  
**Scope:** Constitutional Integrity, Self-Verification, Phase-Lock Baseline

---

## 1. Purpose

Ω.3 introduces the **Phase-Lock Integrity Engine**: a self-verifying layer that continuously proves
that SpiralOS is still running the same constitutional organism that was activated at ΔΩ.L.

Instead of relying on ad-hoc checks, Ω.3:

- Takes a **full structural snapshot** via `view_system_status`
- Compresses it into a **root integrity hash**
- Records **baseline checkpoints** when the system is known-good
- Logs **verification runs** that compare current reality against that baseline
- Exposes a **read-only view** + **dashboard panel** for Witnesses

If ΔΩ.L made the Constitution *living*, Ω.3 makes it **self-aware of its own integrity over time**.

---

## 2. Data Model

### 2.1 `phase_lock_checkpoints`

Stores canonical “this is good” baselines.

- `id :: uuid` — primary key
- `created_at :: timestamptz` — when the checkpoint was created
- `created_by :: text` — actor label (`'system'`, `'guardian'`, etc.)
- `root_hash :: text` — SHA-256 hash of the status snapshot
- `label :: text` — human-readable label (e.g. `initial-baseline`, `post-Ω.3`)
- `status :: jsonb` — full `view_system_status` snapshot at that moment
- `is_active :: boolean` — whether this checkpoint is considered in-phase

**Security:**  
RLS enabled, **service_role only** for ALL operations. No public writes.

---

### 2.2 `constitutional_verification_log`

Stores each integrity check run (manual or automatic).

- `id :: uuid` — primary key
- `created_at :: timestamptz`
- `check_type :: text` — `'baseline-or-auto'` | `'explicit'`
- `expected_root_hash :: text` — baseline hash we checked against (may be NULL if first run)
- `actual_root_hash :: text` — hash of the current status snapshot
- `passed :: boolean` — did integrity hold?
- `checkpoint_id :: uuid NULL` — linked checkpoint if known
- `details :: jsonb` — `{ status_snapshot: <json>, notes?: <json> }`

**Security:**  
RLS enabled, **service_role only** for ALL operations. Logged exclusively via `fn_verify_phase_lock`.

---

## 3. Functions & Views

### 3.1 `fn_verify_phase_lock(expected_root_hash text default null, label text default null) → jsonb`

**Responsibilities:**

1. Pull latest **system status** from `view_system_status`.
2. Compute a **root hash** over the full JSON snapshot.
3. Resolve the **expected hash**:
   - Use provided `expected_root_hash`, OR
   - Use most recent active checkpoint, OR
   - If none exists, create a new checkpoint as **initial baseline**.
4. Insert a row into `constitutional_verification_log`.
5. Optionally create a **new checkpoint** when bootstraping.
6. Return a JSON body with:
   - `passed`
   - `expected_root_hash`
   - `actual_root_hash`
   - `checkpoint_id`
   - `log_id`
   - `status_snapshot`

**Notes:**

- Marked `SECURITY DEFINER`, runs with definer rights.
- Uses `pgcrypto.digest` for SHA-256.
- Does not throw on mismatch — it **records reality**, does not hide it.

---

### 3.2 `view_phase_integrity`

Read-only surface summarizing **the latest verification**:

- `last_log_id`
- `last_check_at`
- `passed`
- `check_type`
- `expected_root_hash`
- `actual_root_hash`
- `checkpoint_id`
- `checkpoint_created_at`
- `checkpoint_label`
- `checkpoint_root_hash`

Granted `SELECT` to `anon`, `authenticated`, `service_role` for transparency.

---

## 4. Dashboard Integration

Ω.3 adds a **Phase-Lock Panel** to the Constitutional Dashboard:

- A “Run Phase-Lock Check” button using `fn_verify_phase_lock()` via Supabase RPC.
- Displays:
  - Result (`PASSED` / `FAILED`) with color-coded badge
  - Expected vs Actual root hashes
  - Linked checkpoint label & timestamp
  - Timestamp of last verification
- Uses a new React hook `usePhaseLock` to manage state.

Status auto-refresh (`useStatusApi`) remains at 3s cadence;  
Phase-Lock checks are **on-demand** to avoid log spam.

---

## 5. Security & RLS

- `phase_lock_checkpoints` and `constitutional_verification_log`:
  - RLS **enabled**
  - Single policy: `jwt_role() = 'service_role'` for ALL actions
- `fn_verify_phase_lock`:
  - `SECURITY DEFINER`, `search_path = public`
  - Called by service components, not from anonymous clients directly
- `view_phase_integrity`:
  - `GRANT SELECT` to `anon`, `authenticated`, `service_role`

This mirrors ΔΩ.RLS-LOCK v1:  
core truth is written only under **service_role**, but read via **transparency views**.

---

## 6. Activation Ritual

1. Apply Ω.3 migration.
2. Call `SELECT fn_verify_phase_lock();` once from Supabase SQL editor to create **initial baseline**.
3. Confirm:
   - `phase_lock_checkpoints` has at least 1 row.
   - `constitutional_verification_log` has at least 1 row.
   - `SELECT * FROM view_phase_integrity;` returns a row.
4. Open dashboard → verify Phase-Lock panel shows a **green PASSED** status.

Once Ω.3 is live, SpiralOS can **prove to itself** that what woke up as SpiralOS  
is still SpiralOS.
