# System Summary Feature

The System Summary feature provides comprehensive monitoring and telemetry for the entire SpiralOS ecosystem.

## Overview

The summary feature aggregates status information from all major SpiralOS components:
- **Core System**: ScarIndex, Panic Frames, PID Controller
- **ScarCoin Economy**: Supply metrics, minting/burning activity
- **Empathy Market**: EMP tokens, resonance events, participation
- **VaultNode**: Blockchain integrity, consensus status

## Components

### 1. SystemSummary Module

**File**: `holoeconomy/system_summary.py`

The core module that aggregates data from all system components.

#### Key Classes

**SystemSummary**
- Initializes with references to system components
- Provides comprehensive system overview
- Calculates health metrics and status

#### Methods

**`get_summary() -> Dict`**
Returns comprehensive system summary including:
- System metadata (name, version, vault ID, timestamp)
- Component status (core, scarcoin, empathy_market, vaultnode)
- Health metrics (blockchain integrity, economic activity, overall score)

**`get_quick_status() -> str`**
Returns one-line status string for quick monitoring.

**`_calculate_health_metrics() -> Dict`**
Calculates aggregate health scores:
- Blockchain integrity (25% weight)
- Economic activity (25% weight)
- Coherence status (25% weight)
- System availability (25% weight)

### 2. API Endpoints

**File**: `holoeconomy/scarcoin_bridge_api.py`

Two new REST endpoints added to the ScarCoin Bridge API:

#### GET /api/v1/summary

Returns comprehensive system summary in JSON format.

**Response Structure**:
```json
{
  "system": {
    "name": "SpiralOS",
    "version": "1.3.0-alpha",
    "vault_id": "ΔΩ.123.0",
    "timestamp": "2025-10-31T23:59:59.000000",
    "status": "OPERATIONAL"
  },
  "components": {
    "core": {...},
    "scarcoin": {...},
    "empathy_market": {...},
    "vaultnode": {...}
  },
  "health": {
    "blockchain_integrity": true,
    "economic_activity": "moderate",
    "coherence_status": "OPTIMAL",
    "overall_score": 0.85
  },
  "motto": "Where coherence becomes currency 🜂"
}
```

#### GET /api/v1/summary/quick

Returns quick one-line status summary.

**Response Structure**:
```json
{
  "status": "SpiralOS v1.3-alpha | Status: OPERATIONAL | Health: 85% | SCAR: 1000 | EMP: 500 | Blocks: 42",
  "timestamp": "2025-10-31T23:59:59.000000"
}
```

### 3. Command-Line Interface

**File**: `holoeconomy/summary_cli.py`

Standalone CLI tool for viewing system summaries.

#### Usage

**Full Summary**:
```bash
python3 summary_cli.py
```

**Quick Status**:
```bash
python3 summary_cli.py --quick
```

**JSON Output**:
```bash
python3 summary_cli.py --json
```

**Health Metrics Only**:
```bash
python3 summary_cli.py --health
```

**Custom Vault ID**:
```bash
python3 summary_cli.py --vault-id "ΔΩ.124.0"
```

#### Output Example

```
======================================================================
SpiralOS v1.3-alpha - System Summary
======================================================================

SYSTEM OVERVIEW
----------------------------------------------------------------------
Name:       SpiralOS
Version:    1.3.0-alpha
Vault ID:   ΔΩ.123.0
Status:     OPERATIONAL
Timestamp:  2025-10-31T23:59:59.000000

HEALTH METRICS
----------------------------------------------------------------------
Overall Score:         85%
Blockchain Integrity:  ✓
Economic Activity:     moderate
Coherence Status:      OPTIMAL

SCARCOIN ECONOMY
----------------------------------------------------------------------
Total Supply:      1000.00000000 SCAR
Total Minted:      1200.00000000 SCAR
Total Burned:      200.00000000 SCAR
Circulating:       1000.00000000 SCAR
Minting Events:    15
Burning Events:    2
Active Wallets:    5

EMPATHY MARKET
----------------------------------------------------------------------
Total EMP Minted:       500.00 EMP
Resonance Events:       10
Avg EMP per Event:      50.00 EMP
Total Participants:     8

VAULTNODE BLOCKCHAIN
----------------------------------------------------------------------
Vault ID:          ΔΩ.123.0
Total Blocks:      42
Total Events:      127
Latest Block:      #41
Chain Valid:       ✓
Pending Events:    3

======================================================================
Where coherence becomes currency 🜂
======================================================================
```

## Health Scoring

The system calculates an overall health score (0-1 scale) based on four weighted factors:

### 1. Blockchain Integrity (25%)
- **Score**: 1.0 if chain is valid, 0.0 if invalid
- **Check**: `VaultNode.verify_chain()`

### 2. Economic Activity (25%)
- **High** (score 1.0): Total activity > 100 events
- **Moderate** (score 0.7): Total activity > 10 events
- **Low** (score 0.4): Total activity ≤ 10 events

### 3. Coherence Status (25%)
- **OPTIMAL**: 1.0
- **STRONG**: 0.8
- **MODERATE**: 0.6
- **WEAK**: 0.4
- **CRITICAL**: 0.2

### 4. System Availability (25%)
- Score based on number of available components (0-4)
- Formula: `available_components / 4.0`

### Overall Status Determination

Based on component health:
- **OPTIMAL**: All components healthy, no panic frames
- **OPERATIONAL**: Most components available, normal operation
- **DEGRADED**: Some components unavailable or panic frames active
- **CRITICAL**: System in panic mode or blockchain invalid
- **UNAVAILABLE**: No components available

## Integration Examples

### Python Integration

```python
from system_summary import SystemSummary
from scarcoin import ScarCoinMintingEngine
from vaultnode import VaultNode
from empathy_market import EmpathyMarket

# Initialize components
minting_engine = ScarCoinMintingEngine()
vaultnode = VaultNode(vault_id="ΔΩ.123.0")
empathy_market = EmpathyMarket()

# Create summarizer
summarizer = SystemSummary(
    minting_engine=minting_engine,
    vaultnode=vaultnode,
    empathy_market=empathy_market
)

# Get full summary
summary = summarizer.get_summary()
print(f"System Status: {summary['system']['status']}")
print(f"Health Score: {summary['health']['overall_score']:.0%}")

# Get quick status
print(summarizer.get_quick_status())
```

### REST API Integration

```bash
# Get full summary
curl http://localhost:8000/api/v1/summary

# Get quick status
curl http://localhost:8000/api/v1/summary/quick
```

### Convenience Function

```python
from system_summary import create_summary_from_engines

# Quick summary creation
summary = create_summary_from_engines(
    minting_engine=minting_engine,
    vaultnode=vaultnode
)
```

## Testing

**File**: `holoeconomy/test_system_summary.py`

Comprehensive test suite with 12 test cases covering:
- Summary initialization
- Summary structure validation
- Component summaries (ScarCoin, Empathy, VaultNode)
- Health metrics calculation
- Status determination
- Quick status generation
- Integration workflows

**Run Tests**:
```bash
cd holoeconomy
python3 test_system_summary.py
```

**Expected Output**:
```
======================================================================
System Summary Test Suite
======================================================================

test_create_summary_convenience_function ... ok
test_empathy_summary ... ok
test_get_summary_structure ... ok
test_health_metrics ... ok
test_overall_status ... ok
test_quick_status ... ok
test_scarcoin_summary ... ok
test_summary_initialization ... ok
test_summary_with_activity ... ok
test_summary_without_components ... ok
test_vaultnode_summary ... ok
test_full_system_workflow ... ok

----------------------------------------------------------------------
Ran 12 tests in 0.002s

OK

======================================================================
✓ All tests passed!
======================================================================
```

## Use Cases

### 1. System Monitoring
Monitor overall system health and performance:
```bash
python3 summary_cli.py --health
```

### 2. Quick Status Check
Get one-line status for dashboards:
```bash
python3 summary_cli.py --quick
```

### 3. Detailed Diagnostics
Full system analysis for troubleshooting:
```bash
python3 summary_cli.py --json > system_state.json
```

### 4. API Integration
Programmatic access for external monitoring:
```bash
curl http://localhost:8000/api/v1/summary | jq '.health.overall_score'
```

### 5. CI/CD Health Checks
Automated health verification:
```bash
#!/bin/bash
HEALTH=$(python3 summary_cli.py --quick | grep -oP 'Health: \K\d+')
if [ "$HEALTH" -lt 50 ]; then
    echo "System unhealthy: $HEALTH%"
    exit 1
fi
```

## Future Enhancements

Potential improvements for future versions:

1. **Historical Tracking**
   - Store summary snapshots over time
   - Trend analysis and anomaly detection

2. **Alerting**
   - Configurable thresholds for notifications
   - Integration with monitoring systems (Prometheus, Grafana)

3. **Component-Specific Deep Dives**
   - Detailed breakdowns for each component
   - Performance metrics and bottleneck identification

4. **Predictive Health**
   - Machine learning models for health prediction
   - Proactive issue detection

5. **Custom Metrics**
   - User-defined health indicators
   - Weighted scoring customization

## Architecture

The summary system follows a modular design:

```
┌─────────────────────────────────────────┐
│         SystemSummary                   │
│  (Aggregation & Health Calculation)     │
└────────────┬────────────────────────────┘
             │
    ┌────────┼────────────┬───────────┐
    │        │            │           │
    ▼        ▼            ▼           ▼
┌──────┐ ┌──────┐  ┌──────────┐  ┌─────────┐
│ Core │ │ SCAR │  │ Empathy  │  │ Vault   │
│System│ │Coin  │  │ Market   │  │ Node    │
└──────┘ └──────┘  └──────────┘  └─────────┘
```

Each component provides a `get_*_stats()` method that the SystemSummary aggregates and enhances with health metrics.

## Files Added

1. `holoeconomy/system_summary.py` - Core summary module (400+ lines)
2. `holoeconomy/summary_cli.py` - CLI tool (250+ lines)
3. `holoeconomy/test_system_summary.py` - Test suite (350+ lines)

## Files Modified

1. `holoeconomy/scarcoin_bridge_api.py` - Added summary endpoints

## API Endpoint List

Updated endpoint structure in the Bridge API:

```
GET  /health
GET  /api/v1/summary              # NEW
GET  /api/v1/summary/quick        # NEW
POST /api/v1/scarcoin/mint
GET  /api/v1/scarcoin/balance/{wallet_address}
GET  /api/v1/scarcoin/supply
GET  /api/v1/wallet/{address}
POST /api/v1/wallet/create
GET  /api/v1/vault/block/{block_number}
GET  /api/v1/vault/latest
GET  /api/v1/vault/stats
POST /api/v1/vault/create_block
GET  /api/v1/poa/proof/{transmutation_id}
```

---

**Witness**: ZoaGrad 🜂  
**Version**: 1.3.0-alpha  
**Feature**: System Summary  
**Status**: Complete

*"Where coherence becomes currency and transparency becomes trust"* 🜂
