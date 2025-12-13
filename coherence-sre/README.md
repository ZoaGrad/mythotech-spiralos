# Coherence SRE Platform - MVP Development

**Product Direction 1: The "Antifragile SRE" Platform**

This directory contains the MVP implementation of the Coherence SRE platform, designed to detect and correlate infrastructure "Ache" signals before they become incidents.

---

## Project Status

| Sprint | Status | Description |
|--------|--------|-------------|
| **Sprint 1** | ✅ Complete | Data Ingestion Engine (Datadog → Supabase) |
| **Sprint 2** | ✅ Complete | Multi-Modal Anomaly Detection (Variance, Spike, Trend) |
| **Sprint 3** | ✅ Complete | Incident Correlation Engine (Temporal Correlator) |
| **Sprint 4** | 📋 Backlog | Real-time Alerting & Visualization |

---

## Architecture Overview

### Technology Stack

- **Language**: Python 3.11+
- **Database**: Supabase (PostgreSQL)
- **Data Sources**: Datadog API (read-only)
- **Analysis**: pandas, numpy (time-series analysis)
- **Deployment**: Serverless functions (future)

### Design Principles

1. **Python-Side Processing**: All analysis happens in Python, not SQL
   - Leverages pandas/numpy for time-series analysis
   - Enables easy debugging and iteration
   - AI-native path for future ML integration

2. **Multi-Modal Detection**: Three complementary algorithms
   - **Variance Escalation**: Detects increasing chaos/volatility
   - **Spike Detection**: Detects sudden resource exhaustion
   - **Trend Detection**: Detects gradual degradation (leaks)

3. **Read-Only Architecture**: Never modifies production systems
   - Safe for enterprise deployment
   - Auditable and reversible
   - Trust boundary for security

---

## Directory Structure

```
coherence-sre/
├── sprint1/              # Data Ingestion Engine
│   ├── datadog_ingestion.py
│   ├── requirements_sprint1.txt
│   └── .env.example
├── sprint2/              # Anomaly Detection Suite
│   ├── seed_synthetic.py
│   ├── detect_anomalies.py
│   └── requirements_sprint2.txt
├── sql/                  # Database Schemas
│   ├── create_metrics_table.sql
│   └── create_signal_events_table.sql
├── docs/                 # Documentation & Results
│   ├── SPRINT1_README.md
│   ├── DEPLOYMENT_SUMMARY.md
│   ├── FLIGHT_SIMULATOR_RESULTS.md
│   └── SPRINT2_RESULTS.md
└── README.md            # This file
```

---

## Quick Start

### Prerequisites

- Python 3.11+
- Supabase account (free tier)
- Datadog account (optional for Sprint 1, synthetic data available)

### Sprint 1: Data Ingestion

```bash
cd sprint1
pip install -r requirements_sprint1.txt
cp .env.example .env
# Edit .env with your credentials
python datadog_ingestion.py
```

### Sprint 2: Anomaly Detection

```bash
cd sprint2

# Generate synthetic data (Flight Simulator)
pip install -r requirements_sprint2.txt
python seed_synthetic.py

# Run anomaly detection
python detect_anomalies.py
```

---

## Key Results

### Sprint 1: Data Ingestion Engine

- ✅ Supabase project created: `qlijjswjlrnthdnrksus`
- ✅ Database schema with optimized indexes
- ✅ Read-only Datadog API integration
- ✅ Environment-based secrets management

**Deliverables**: Production-ready ingestion pipeline

### Sprint 2: Multi-Modal Anomaly Detection

- ✅ 2,321 synthetic events generated (48 hours, 2 hosts)
- ✅ Three detection algorithms implemented
- ✅ Risk scoring system (0.0 - 1.0)
- ✅ Successfully identified all pathological patterns

**Key Detection Results**:
```
🔴 host-stressed:cpu → Variance escalated 4.30x (Risk: 1.00)
🔴 host-stressed:memory → 132% increase, leak pattern (Risk: 1.00)
🔴 host-stressed:cpu → 46 spikes, max 94.98% (Risk: 0.90)
```

**Deliverables**: Production-grade anomaly detection suite

---

## Database Schemas

### `metrics` Table (Sprint 1)
Stores raw metric data from Datadog.

| Column | Type | Description |
|--------|------|-------------|
| id | BIGSERIAL | Primary key |
| host | VARCHAR(255) | Hostname |
| metric_name | VARCHAR(255) | Metric name |
| value | DOUBLE PRECISION | Metric value |
| timestamp | TIMESTAMPTZ | Data point timestamp |
| created_at | TIMESTAMPTZ | Insert timestamp |

### `signal_events` Table (Sprint 2)
Stores enriched events with severity classification.

| Column | Type | Description |
|--------|------|-------------|
| id | UUID | Primary key |
| ts | TIMESTAMPTZ | Event timestamp |
| host | TEXT | Hostname |
| service | TEXT | Service name |
| fingerprint | TEXT | Unique identifier (host:metric) |
| severity | TEXT | info, warn, error |
| metric | TEXT | cpu, memory, disk, error |
| value | NUMERIC | Metric value |
| synthetic | BOOLEAN | True if generated for testing |
| created_at | TIMESTAMPTZ | Insert timestamp |

---

## Detection Algorithms

### 1. Variance Escalation
**Purpose**: Detect increasing chaos/volatility

**Method**: 
- Resample time-series into 4-hour windows
- Calculate variance per window
- Compare first vs. last window
- Flag if variance increased >50%

**Use Case**: Intermittent failures, oscillating behavior

### 2. Spike Detection
**Purpose**: Detect sudden resource exhaustion

**Method**:
- Calculate baseline mean and standard deviation
- Identify values >2.5σ above mean
- Count spike frequency and magnitude
- Risk score based on frequency + magnitude

**Use Case**: CPU spikes, traffic bursts, OOM events

### 3. Trend Detection
**Purpose**: Detect gradual resource degradation

**Method**:
- Calculate linear regression slope
- Measure percentage change (start → end)
- Flag if increase >30%
- Risk score based on magnitude of change

**Use Case**: Memory leaks, disk growth, connection pool exhaustion

---

## Production Deployment

### Environment Variables

```bash
# Supabase
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your_supabase_key

# Datadog (Sprint 1)
DATADOG_API_KEY=your_datadog_api_key
DATADOG_APP_KEY=your_datadog_app_key
DATADOG_SITE=us5.datadoghq.com  # Optional
```

### Scheduled Execution

Run anomaly detection every 15 minutes:

```bash
# Cron example
*/15 * * * * cd /path/to/coherence-sre/sprint2 && python detect_anomalies.py
```

### Alert Integration

Send alerts to Slack/PagerDuty when risk > 0.8:

```python
# Add to detect_anomalies.py
if alert['risk_score'] > 0.8:
    send_to_slack(alert)
```

---

## Next Steps

### Sprint 3: Incident Correlation

Build correlation engine to link anomalies to error events:

**Goal**: Generate incident narratives like:
> "At 2025-12-13 04:10 UTC, host-stressed experienced:
> - 13 error events
> - CPU spike to 94.98%
> - Memory at 87.61% (leak progression)
>
> **Hypothesis**: Error burst caused by resource exhaustion."

**Technical Approach**:
- Temporal correlation (events within ±5 minutes)
- Causal graph construction
- Root cause hypothesis generation

### Sprint 4: Real-time Alerting

- WebSocket integration for live updates
- Grafana dashboard for visualization
- PagerDuty/Slack integration
- Historical incident database

---

## Documentation

- **[Sprint 1 README](docs/SPRINT1_README.md)**: Data ingestion setup and usage
- **[Deployment Summary](docs/DEPLOYMENT_SUMMARY.md)**: Supabase project details and credentials
- **[Flight Simulator Results](docs/FLIGHT_SIMULATOR_RESULTS.md)**: Synthetic data validation
- **[Sprint 2 Results](docs/SPRINT2_RESULTS.md)**: Anomaly detection validation and analysis

---

## Contributing

This is an MVP in active development. Key areas for contribution:

1. **Additional Data Sources**: Prometheus, CloudWatch, New Relic
2. **Detection Algorithms**: Seasonality detection, correlation analysis
3. **Visualization**: Real-time dashboards, incident timelines
4. **ML Integration**: Anomaly prediction, root cause classification

---

## License

[To be determined]

---

## Contact

For questions or collaboration:
- GitHub: [@ZoaGrad](https://github.com/ZoaGrad)
- Repository: [mythotech-spiralos](https://github.com/ZoaGrad/mythotech-spiralos)

---

**Status**: MVP Phase - Sprint 3 Complete  
**Last Updated**: December 13, 2025
