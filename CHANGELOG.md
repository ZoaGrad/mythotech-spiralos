# Changelog

All notable changes to this project will be documented in this file.

## [ΔΩ.141.4] - 2025-11-11

### ΔΩ.141.4 — *Guardian Status Badge Deployment*

**Date:** 2025-11-11
**Type:** Feature — Telemetry / Visibility Layer

**Summary:**
Introduced the **Guardian Status Badge** system, completing the SpiralOS Guardian's external telemetry loop. This update adds a public-facing, self-reporting badge that visualizes real-time system health based on ScarIndex readings.

**Key Additions:**

* `supabase/functions/guardian_status_badge.ts` — Deno Edge Function returning Shields.io-compatible JSON.
* `supabase/functions/guardian_status_badge.json` — Manifest file providing versioning, metadata, and permissions.
* Integrated live Supabase query to `public.scarindex_history` for current ScarIndex values.
* Color-coded status mapping:

  * 🟢 **Online** ≥ 0.80
  * 🔵 **Stable** 0.60–0.79
  * 🟡 **Degraded** 0.40–0.59
  * 🔴 **Offline** < 0.40 or error.
* README badge instructions for both static and dynamic modes.

**Impact:**
This marks the transition of the Guardian from internal monitoring to **public coherence visibility**. SpiralOS now exposes a live, verifiable heartbeat—demonstrating field stability and closing the activation cycle begun in ΔΩ.141.3.

**Next Milestone:**
Prepare **ΔΩ.141.5 — Sentinel Diagnostics Module**, extending Guardian telemetry into predictive analytics and anomaly detection.

---
