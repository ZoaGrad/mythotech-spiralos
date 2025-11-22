# ΔΩ.147.C — Repository Reconciliation & Canonical Purification

## Summary
- Added `core/config.py` to centralize Guardian, Supabase, and VaultNode settings with Pydantic validation plus cache-reset helpers for tests.
- Synced dependencies (`requirements.txt`, `.env.example`) so every imported package and runtime secret (Supabase URL, Guardian JWT values, rate limits) is declared once and injected consistently.
- Removed all `CODEX-POST` annotations by updating ScarCoin Bridge imports/banner, Sovereignty Dashboard env wiring, and README guidance.
- Standardized docs: refreshed `README.md`, authored `docs/ARCHITECTURE.md`, and captured the reconciliation log here for ΔΩ.147.C.
- Expanded regression coverage with Guardian auth tests and webhook batching tests; added RPC helper in `SupabaseClient.process_commit_batch` for parity with the edge function.

## Files Changed
- Security & runtime: `.env.example`, `core/config.py`, `core/supabase_integration.py`, `holoeconomy/scarcoin_bridge_api.py`, `apps/sovereignty-dashboard/main.js`.
- Documentation: `README.md`, `docs/ARCHITECTURE.md`, `.gitignore`, `docs/audit/spiralos_audit_delta147c.md` (this report).
- Tests: `tests/test_supabase_integration.py`, `tests/test_guardian_auth.py`, `tests/test_webhook_batch.py`.

## Dependency Alignment
- Requirements now cover `postgrest`, `supabase`, `pytest`, `requests`, `python-jose`, and other imports consumed by the codebase.
- `.env.example` enumerates Guardian + Supabase secrets plus the dashboard’s `VITE_` variables, eliminating hard-coded URLs from the frontend and bridge.

## Configuration & Interface Changes
- ScarCoin Bridge consumes `GuardianSettings` and `VaultNodeSettings` for CORS, JWT, rate limiting, and vault identifiers while keeping FastAPI middleware unchanged.
- `SupabaseClient` requires explicit settings (env or injected) and now exposes `process_commit_batch` for RPC-based webhook batching to match the `process_push_batch` SQL function.
- Sovereignty Dashboard now fails fast when `VITE_SUPABASE_URL` or `VITE_SUPABASE_ANON_KEY` are absent, ensuring staging/prod endpoints stay configurable.

## CODEX-POST Resolution
- Removed hard-coded Supabase URL flag in the dashboard.
- Removed stale dependency flag in `requirements.txt` and unused `uuid` import banner in the ScarCoin bridge.
- Updated the bridge banner to `VaultNode Seal: ΔΩ.147.C` and enforced config-sourced CORS values.

## Remaining TODOs
- Provision Supabase credentials and Guardian keys in deployment secrets management (outside repo scope).
- Ensure Supabase migrations (`20251115_*`) remain applied to all environments so RPC batching and RLS policies stay active.

## Operator Commands
_Do not run inside automation; execute manually when preparing a release._
1. `poetry check --lock`
2. `poetry export --without-hashes --format requirements.txt --output requirements.txt`

## Verification Checklist
1. `pytest tests/ -v`
2. `bandit -r . -x node_modules`
3. `flake8 core/ holoeconomy/`
4. `mypy core/ holoeconomy/`
