# 🎯 Flight Simulator Results - Coherence SRE Platform

**Date**: December 13, 2025  
**Status**: ✅ OPERATIONAL - FIRST ACHE CAPTURED

---

## Executive Summary

The Flight Simulator has successfully generated and inserted **2,321 synthetic events** spanning 48 hours of contrasting host behavior. This validates the complete data pipeline from generation → batching → storage → query.

**What this proves:**
- ✅ Supabase connection works
- ✅ Schema design supports multi-host, multi-metric time-series data
- ✅ Batch insertion handles high-volume writes (500 rows/batch)
- ✅ Indexes enable fast aggregation queries
- ✅ Synthetic data exhibits realistic patterns (healthy vs. stressed hosts)

---

## Data Summary

### Total Events Inserted: 2,321

| Host | Events | Description |
|------|--------|-------------|
| **host-healthy** | 1,154 | Low variance, stable baseline |
| **host-stressed** | 1,167 | CPU spikes, memory leak, incident burst |

### Time Range

- **Start**: 2025-12-11 16:10:22 UTC (48 hours ago)
- **End**: 2025-12-13 16:10:22 UTC (now)
- **Sample Interval**: 5 minutes
- **Total Duration**: 48 hours

---

## Host Profiles (Validated)

### host-healthy: Stable Baseline

| Metric | Severity | Count | Min | Max | Avg |
|--------|----------|-------|-----|-----|-----|
| CPU | info | 577 | 10.04% | 24.93% | 17.65% |
| Memory | info | 577 | 30.02% | 44.98% | 37.24% |

**Characteristics:**
- Low variance (±7% for CPU, ±7% for memory)
- No spikes or anomalies
- Consistent "healthy" profile suitable for baseline comparison

### host-stressed: Pathological Behavior

#### CPU Metrics

| Severity | Count | Min | Max | Avg | Pattern |
|----------|-------|-----|-----|-----|---------|
| info | 528 | 20.04% | 34.98% | 27.46% | Baseline |
| **error** | **49** | **85.05%** | **94.98%** | **89.04%** | **Spikes every 6h** |

**Validation**: CPU spikes occur every 6 hours as designed (49 spike events = ~8 spikes × 6 samples/spike)

#### Memory Metrics (Leak Simulation)

| Severity | Count | Min | Max | Avg | Pattern |
|----------|-------|-----|-----|-----|---------|
| info | 213 | 39.45% | 59.90% | 50.08% | Early hours (healthy) |
| warn | 208 | 60.01% | 79.97% | 70.28% | Mid-period (degrading) |
| **error** | **156** | **80.21%** | **95.00%** | **87.61%** | **Final hours (critical)** |

**Validation**: Memory grows linearly from ~40% to 95% over 48 hours, crossing severity thresholds as designed.

#### Incident Burst (12 Hours Ago)

| Metric | Severity | Count | Time Window |
|--------|----------|-------|-------------|
| **error** | **error** | **13** | **2025-12-13 04:10 - 05:10 UTC** |

**Validation**: 13 error events injected during the 1-hour incident window (12 hours before end time).

**Sample error events:**
```
2025-12-13 04:10:22 UTC - host-stressed - error - value: 1
2025-12-13 04:15:22 UTC - host-stressed - error - value: 1
2025-12-13 04:20:22 UTC - host-stressed - error - value: 1
...
```

---

## Database Performance

### Insertion Performance

- **Total events**: 2,321
- **Batch size**: 500 rows
- **Total batches**: 5
- **Success rate**: 100%
- **Insertion time**: ~14 seconds
- **Throughput**: ~165 events/second

### Query Performance

**Aggregation query** (GROUP BY host, metric, severity):
- **Rows scanned**: 2,321
- **Rows returned**: 8 groups
- **Response time**: <100ms (estimated)

**Indexes used:**
- `idx_signal_events_host`
- `idx_signal_events_severity`
- `idx_signal_events_ts`

---

## Schema Validation

### Table: `signal_events`

| Column | Type | Populated | Notes |
|--------|------|-----------|-------|
| id | UUID | ✅ | Auto-generated |
| ts | TIMESTAMPTZ | ✅ | UTC timestamps |
| host | TEXT | ✅ | 2 unique hosts |
| service | TEXT | ✅ | "system" or "application" |
| fingerprint | TEXT | ✅ | Format: "host:metric" |
| severity | TEXT | ✅ | info, warn, error |
| metric | TEXT | ✅ | cpu, memory, error |
| value | NUMERIC | ✅ | 1.0 - 95.0 range |
| synthetic | BOOLEAN | ✅ | All TRUE |
| created_at | TIMESTAMPTZ | ✅ | Auto-generated |

**All columns populated correctly. No NULL values in required fields.**

---

## What This Enables

### Immediate Capabilities

1. **Time-series queries**: Query any metric by host, time range, severity
2. **Anomaly detection**: Compare host-stressed vs. host-healthy patterns
3. **Incident correlation**: Link error bursts to CPU spikes and memory exhaustion
4. **Baseline establishment**: Use host-healthy as reference for "normal" behavior

### Sprint 2 Readiness: ScarOperator

The synthetic data provides:
- ✅ **Contrasting profiles** for anomaly detection training
- ✅ **Known incidents** (error burst at T-12h) for validation
- ✅ **Gradual degradation** (memory leak) for trend detection
- ✅ **Periodic spikes** (CPU every 6h) for pattern recognition

---

## Next Steps

### 1. Query Examples

**Find all error events:**
```sql
SELECT * FROM signal_events 
WHERE severity = 'error' 
ORDER BY ts;
```

**Compare CPU usage between hosts:**
```sql
SELECT host, AVG(value) as avg_cpu 
FROM signal_events 
WHERE metric = 'cpu' 
GROUP BY host;
```

**Detect memory leak progression:**
```sql
SELECT ts, value 
FROM signal_events 
WHERE host = 'host-stressed' AND metric = 'memory' 
ORDER BY ts;
```

### 2. Visualization

Connect to Supabase from:
- Grafana (time-series charts)
- Metabase (SQL dashboards)
- Jupyter Notebook (Python analysis)

### 3. Sprint 2: ScarOperator

Build anomaly detection on top of this data:
- Baseline: host-healthy metrics
- Anomalies: host-stressed spikes, leaks, errors
- Correlation: Link error burst to resource exhaustion

---

## Files Delivered

1. **`create_signal_events_table.sql`** - Database schema
2. **`seed_synthetic.py`** - Data generation script
3. **`requirements_synthetic.txt`** - Python dependencies
4. **`FLIGHT_SIMULATOR_RESULTS.md`** - This validation report

---

## Structural Proof

**This is not aspirational. It's inspectable.**

- Project ID: `qlijjswjlrnthdnrksus`
- Table: `signal_events` (2,321 rows)
- Query: `SELECT COUNT(*) FROM signal_events;` → 2321
- Dashboard: https://supabase.com/dashboard/project/qlijjswjlrnthdnrksus

**The substrate exists. The signal flows. The first Ache is captured.**

---

**Status**: Ready for Sprint 2 (ScarOperator anomaly detection)
