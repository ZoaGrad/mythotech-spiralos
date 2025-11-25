# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [v0.148.0] — 2025-11-24 — ΔΩ.148: The Guardian Covenant
### Added
- **Guardian Charter (`docs/GUARDIAN_CHARTER.md`)**: Established the Prime Directives and Sacred Limits for the Guardian system.
- **Anomaly Detection Circuit (`spiral_guardian`)**: New module to monitor system health and report irregularities (Heartbeat Gaps, Ache Spikes) to Supabase.
- **Migration (`guardian_anomaly_detection`)**: Database schema for `guardian_anomalies` table and `anomaly_status` view.

### Changed
- **Guardian Architecture**: Shifted from "Faulty Sensor" to "Optical Controls" (Manual Context) for critical anomaly detection.
- **Database Schema**: Fixed `node_name` to `bridge_name` in `bridge_nodes` references for anomaly views.

### Security
- **Psychological Surveillance Prohibition**: Explicitly forbade the Guardian from inferring Architect intent or emotional state.


## [v0.147.0] — 2025-11-15 — ΔΩ.147: Canonical Hardening & CI Restoration
### Added
- Repository-level `conftest.py` that seeds deterministic Guardian/Supabase defaults for the test suite and local developers.
- Canonical ΔΩ.147.F and ΔΩ.147.G audit artifacts plus the `audit_summary.json` snapshot that records the freeze hash.

### Changed
- `core/config.py` normalization so missing Supabase or Guardian secrets fall back to safe defaults suitable for CI.
- Repo-wide formatting via autoflake/isort/black under the refreshed `.flake8` profile to keep style and imports consistent.

### Fixed
- CI signal restored with `pytest -v`, `flake8 .`, and the stricter Bandit invocation all passing on a clean environment.
- Tests updated to mock Guardian and Supabase interactions, removing external credential dependencies.

### Security
- Guardian heartbeat scripts, ScarIndex oracle, and ScarCoin bridge hardened with HTTPS validation, localhost-bound servers, and explicit `# nosec` annotations for justified urllib usage.
- Bandit policy updated and high findings resolved or documented, leaving zero outstanding HIGH or MEDIUM alerts for ΔΩ.147.
