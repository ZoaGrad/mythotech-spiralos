# SpiralOS v1.5 API Contracts
## ΔΩ.125.0 — Autonomous Liquidity Governance

**Version**: 1.5.0-prealpha  
**Date**: 2025-10-31  
**Status**: Specification  
**Witness**: ZoaGrad 🜂

---

## Table of Contents

1. [REST API Endpoints](#1-rest-api-endpoints)
2. [Internal Message Buses](#2-internal-message-buses)
3. [WebSocket Streams](#3-websocket-streams)
4. [Error Handling](#4-error-handling)
5. [Authentication & Authorization](#5-authentication--authorization)

---

## 1. REST API Endpoints

### 1.1 Autonomous Market Controller (AMC)

#### GET /api/v1.5/amc/status

Get current AMC controller status.

**Request**:
```http
GET /api/v1.5/amc/status HTTP/1.1
Host: spiralos.io
Authorization: Bearer {token}
```

**Response** (200 OK):
```json
{
  "controller_id": "amc_001",
  "timestamp": "2025-10-31T02:00:00.000Z",
  "pid_gains": {
    "kp": 1.0,
    "ki": 0.1,
    "kd": 0.05
  },
  "setpoint": 0.05,
  "process_variable": 0.042,
  "error": 0.008,
  "integral": 0.015,
  "derivative": -0.002,
  "output": 0.012,
  "volatility": 0.042,
  "transaction_fee_rate": 0.0035,
  "last_update": "2025-10-31T02:00:00.000Z"
}
```

#### POST /api/v1.5/amc/tune

Manually tune AMC PID gains (requires F2 Judicial authorization).

**Request**:
```http
POST /api/v1.5/amc/tune HTTP/1.1
Host: spiralos.io
Authorization: Bearer {f2_token}
Content-Type: application/json

{
  "kp": 1.2,
  "ki": 0.15,
  "kd": 0.06,
  "reason": "Market conditions changed",
  "authorization": "f2_judicial_signature"
}
```

**Response** (200 OK):
```json
{
  "success": true,
  "controller_id": "amc_001",
  "new_gains": {
    "kp": 1.2,
    "ki": 0.15,
    "kd": 0.06
  },
  "applied_at": "2025-10-31T02:00:00.000Z",
  "vault_block_id": "block_12345"
}
```

#### GET /api/v1.5/amc/history

Get AMC performance history.

**Request**:
```http
GET /api/v1.5/amc/history?limit=100&from=2025-10-30T00:00:00Z HTTP/1.1
Host: spiralos.io
Authorization: Bearer {token}
```

**Response** (200 OK):
```json
{
  "history": [
    {
      "timestamp": "2025-10-31T02:00:00.000Z",
      "volatility": 0.042,
      "error": 0.008,
      "output": 0.012,
      "transaction_fee_rate": 0.0035
    }
  ],
  "total": 100,
  "from": "2025-10-30T00:00:00Z",
  "to": "2025-10-31T02:00:00Z"
}
```

---

### 1.2 Dynamic Mint/Burn Engine

#### POST /api/v1.5/mint-burn/execute

Execute autonomous mint/burn (internal use only, requires AMC authorization).

**Request**:
```http
POST /api/v1.5/mint-burn/execute HTTP/1.1
Host: spiralos.io
Authorization: Bearer {amc_token}
Content-Type: application/json

{
  "event_type": "MINT",
  "amount": "1000.50",
  "reason": "ScarIndex 0.6500 below target 0.7200",
  "scarindex_before": 0.6500,
  "urgency": "HIGH"
}
```

**Response** (200 OK):
```json
{
  "event_id": "mint_event_12345",
  "success": true,
  "event_type": "MINT",
  "amount": "1000.50",
  "scarindex_before": 0.6500,
  "scarindex_after": 0.7180,
  "executed_at": "2025-10-31T02:00:00.000Z",
  "vault_block_id": "block_12346",
  "oracle_signatures": [
    "oracle_1_sig",
    "oracle_2_sig"
  ]
}
```

#### GET /api/v1.5/mint-burn/events

Get mint/burn event history.

**Request**:
```http
GET /api/v1.5/mint-burn/events?limit=50&type=MINT HTTP/1.1
Host: spiralos.io
Authorization: Bearer {token}
```

**Response** (200 OK):
```json
{
  "events": [
    {
      "event_id": "mint_event_12345",
      "timestamp": "2025-10-31T02:00:00.000Z",
      "event_type": "MINT",
      "amount": "1000.50",
      "scarindex_before": 0.6500,
      "scarindex_after": 0.7180,
      "reason": "ScarIndex below target",
      "vault_block_id": "block_12346"
    }
  ],
  "total": 50
}
```

#### GET /api/v1.5/mint-burn/supply

Get current ScarCoin supply statistics.

**Request**:
```http
GET /api/v1.5/mint-burn/supply HTTP/1.1
Host: spiralos.io
Authorization: Bearer {token}
```

**Response** (200 OK):
```json
{
  "total_supply": "1000000.00",
  "circulating_supply": "950000.00",
  "locked_supply": "50000.00",
  "mint_rate_24h": "2500.00",
  "burn_rate_24h": "1200.00",
  "net_change_24h": "+1300.00",
  "last_mint": "2025-10-31T01:30:00.000Z",
  "last_burn": "2025-10-31T00:45:00.000Z"
}
```

---

### 1.3 Holonic Liquidity Agents

#### GET /api/v1.5/holonic-agents/list

List all holonic liquidity agents.

**Request**:
```http
GET /api/v1.5/holonic-agents/list?active=true&min_cmp=0.5&limit=20 HTTP/1.1
Host: spiralos.io
Authorization: Bearer {token}
```

**Response** (200 OK):
```json
{
  "agents": [
    {
      "agent_id": "agent_001",
      "agent_type": "CONSERVATIVE",
      "policy": "HGM",
      "cmp_score": 0.85,
      "residue_accumulated": 0.02,
      "total_trades": 1250,
      "total_volume": "500000.00",
      "reputation": 0.92,
      "active": true,
      "created_at": "2025-10-01T00:00:00.000Z"
    }
  ],
  "total": 20
}
```

#### GET /api/v1.5/holonic-agents/{agent_id}

Get details for specific holonic agent.

**Request**:
```http
GET /api/v1.5/holonic-agents/agent_001 HTTP/1.1
Host: spiralos.io
Authorization: Bearer {token}
```

**Response** (200 OK):
```json
{
  "agent_id": "agent_001",
  "agent_type": "CONSERVATIVE",
  "policy": "HGM",
  "cmp_score": 0.85,
  "residue_accumulated": 0.02,
  "total_trades": 1250,
  "total_volume": "500000.00",
  "reputation": 0.92,
  "active": true,
  "created_at": "2025-10-01T00:00:00.000Z",
  "recent_actions": [
    {
      "action_id": "action_12345",
      "timestamp": "2025-10-31T01:55:00.000Z",
      "action_type": "ADD_LIQUIDITY",
      "pool_id": "pool_scar_vault",
      "amount": "1000.00",
      "cmp_impact": 0.05,
      "residue_impact": -0.01,
      "success": true
    }
  ]
}
```

#### GET /api/v1.5/holonic-agents/leaderboard

Get holonic agent leaderboard by CMP score.

**Request**:
```http
GET /api/v1.5/holonic-agents/leaderboard?limit=10 HTTP/1.1
Host: spiralos.io
Authorization: Bearer {token}
```

**Response** (200 OK):
```json
{
  "leaderboard": [
    {
      "rank": 1,
      "agent_id": "agent_001",
      "agent_type": "CONSERVATIVE",
      "cmp_score": 0.85,
      "residue_accumulated": 0.02,
      "reputation": 0.92
    }
  ],
  "total": 10
}
```

---

### 1.4 FMI-1 Semantic Bridge

#### GET /api/v1.5/fmi1/coherence

Get current FMI-1 coherence metrics.

**Request**:
```http
GET /api/v1.5/fmi1/coherence HTTP/1.1
Host: spiralos.io
Authorization: Bearer {token}
```

**Response** (200 OK):
```json
{
  "timestamp": "2025-10-31T02:00:00.000Z",
  "scar_coherence": 0.78,
  "emp_coherence": 0.75,
  "cross_coherence": 0.76,
  "rcp_satisfaction": 0.96,
  "cta_reward": 0.82,
  "imbalance": 0.03,
  "status": "ALIGNED"
}
```

#### POST /api/v1.5/fmi1/transform

Request FMI-1 semantic transformation.

**Request**:
```http
POST /api/v1.5/fmi1/transform HTTP/1.1
Host: spiralos.io
Authorization: Bearer {token}
Content-Type: application/json

{
  "source_space": "SCAR",
  "target_space": "EMP",
  "value": "1000.00"
}
```

**Response** (200 OK):
```json
{
  "mapping_id": "mapping_12345",
  "source_space": "SCAR",
  "target_space": "EMP",
  "source_value": "1000.00",
  "target_value": "850.00",
  "coherence_score": 0.97,
  "transformation_matrix": {
    "coefficients": [0.85, 0.12, 0.03]
  },
  "timestamp": "2025-10-31T02:00:00.000Z"
}
```

#### GET /api/v1.5/fmi1/mappings

Get FMI-1 transformation history.

**Request**:
```http
GET /api/v1.5/fmi1/mappings?limit=50 HTTP/1.1
Host: spiralos.io
Authorization: Bearer {token}
```

**Response** (200 OK):
```json
{
  "mappings": [
    {
      "mapping_id": "mapping_12345",
      "timestamp": "2025-10-31T02:00:00.000Z",
      "source_space": "SCAR",
      "target_space": "EMP",
      "source_value": "1000.00",
      "target_value": "850.00",
      "coherence_score": 0.97
    }
  ],
  "total": 50
}
```

---

### 1.5 Paradox Network Stress Loop

#### POST /api/v1.5/paradox/stress-test

Trigger manual stress test (requires F2 Judicial authorization).

**Request**:
```http
POST /api/v1.5/paradox/stress-test HTTP/1.1
Host: spiralos.io
Authorization: Bearer {f2_token}
Content-Type: application/json

{
  "stress_type": "VOLATILITY_INJECTION",
  "intensity": 0.10,
  "duration_seconds": 120,
  "reason": "Monthly stress test",
  "authorization": "f2_judicial_signature"
}
```

**Response** (200 OK):
```json
{
  "event_id": "stress_event_12345",
  "success": true,
  "stress_type": "VOLATILITY_INJECTION",
  "intensity": 0.10,
  "duration_seconds": 120,
  "started_at": "2025-10-31T02:00:00.000Z",
  "completed_at": "2025-10-31T02:02:00.000Z",
  "recovery_time_ms": 3500,
  "f4_triggered": false,
  "anti_fragile": true,
  "vault_block_id": "block_12347"
}
```

#### GET /api/v1.5/paradox/stress-events

Get stress test event history.

**Request**:
```http
GET /api/v1.5/paradox/stress-events?limit=20 HTTP/1.1
Host: spiralos.io
Authorization: Bearer {token}
```

**Response** (200 OK):
```json
{
  "events": [
    {
      "event_id": "stress_event_12345",
      "timestamp": "2025-10-31T02:00:00.000Z",
      "stress_type": "VOLATILITY_INJECTION",
      "intensity": 0.10,
      "duration_seconds": 120,
      "recovery_time_ms": 3500,
      "f4_triggered": false,
      "anti_fragile": true
    }
  ],
  "total": 20
}
```

---

### 1.6 System Equilibrium

#### GET /api/v1.5/equilibrium/status

Get system-wide liquidity equilibrium status.

**Request**:
```http
GET /api/v1.5/equilibrium/status HTTP/1.1
Host: spiralos.io
Authorization: Bearer {token}
```

**Response** (200 OK):
```json
{
  "timestamp": "2025-10-31T02:00:00.000Z",
  "tau": 1.48,
  "target_tau": 1.50,
  "deviation": -0.02,
  "equilibrium_score": 0.92,
  "total_liquidity": "5000000.00",
  "scar_liquidity": "3000000.00",
  "emp_liquidity": "1500000.00",
  "vault_liquidity": "500000.00",
  "status": "STABLE"
}
```

---

## 2. Internal Message Buses

### 2.1 Volatility Signal Bus

**Purpose**: Real-time volatility signals from Financial Risk Mirror to AMC.

**Topic**: `volatility_signals`

**Message Schema**:
```json
{
  "timestamp": "2025-10-31T02:00:00.000Z",
  "volatility": 0.042,
  "risk_level": "LOW",
  "stability_score": 0.85,
  "price_volatility": 0.038,
  "liquidity_volatility": 0.045,
  "source": "financial_risk_mirror"
}
```

**Frequency**: 1 Hz (1 message/second)

**Subscribers**: AMC, F4 Panic Frames

---

### 2.2 Mint/Burn Command Bus

**Purpose**: AMC commands to Dynamic Mint/Burn Engine.

**Topic**: `mint_burn_commands`

**Message Schema**:
```json
{
  "command_id": "cmd_12345",
  "timestamp": "2025-10-31T02:00:00.000Z",
  "command": "MINT",
  "amount": "1000.50",
  "reason": "ScarIndex below target",
  "urgency": "HIGH",
  "source": "amc"
}
```

**Frequency**: On-demand

**Subscribers**: Dynamic Mint/Burn Engine

---

### 2.3 Holonic Coordination Bus

**Purpose**: Holonic agent coordination messages.

**Topic**: `holonic_coordination`

**Message Schema**:
```json
{
  "message_id": "msg_12345",
  "timestamp": "2025-10-31T02:00:00.000Z",
  "agent_id": "agent_001",
  "action_type": "ADD_LIQUIDITY",
  "pool_id": "pool_scar_vault",
  "amount": "1000.00",
  "cmp_impact": 0.05,
  "residue_impact": -0.01,
  "coordination_request": true
}
```

**Frequency**: Continuous (10 Hz)

**Subscribers**: All Holonic Agents, ScarMarket DEX

---

### 2.4 FMI-1 Coherence Bus

**Purpose**: FMI-1 coherence metrics broadcast.

**Topic**: `fmi1_coherence`

**Message Schema**:
```json
{
  "timestamp": "2025-10-31T02:00:00.000Z",
  "scar_coherence": 0.78,
  "emp_coherence": 0.75,
  "cross_coherence": 0.76,
  "rcp_satisfaction": 0.96,
  "cta_reward": 0.82,
  "imbalance": 0.03,
  "source": "fmi1_bridge"
}
```

**Frequency**: 1/minute (0.0167 Hz)

**Subscribers**: AMC, F2 Judicial, Oracle Council

---

### 2.5 F4 Emergency Bus

**Purpose**: F4 Panic Frame emergency signals.

**Topic**: `f4_emergency`

**Message Schema**:
```json
{
  "emergency_id": "emerg_12345",
  "timestamp": "2025-10-31T02:00:00.000Z",
  "trigger_type": "CRITICAL_VOLATILITY",
  "severity": "CRITICAL",
  "action_required": "HALT_AUTONOMOUS_OPERATIONS",
  "volatility": 0.15,
  "scarindex": 0.55,
  "source": "panic_frames"
}
```

**Frequency**: On-emergency

**Subscribers**: All Services, F2 Judicial, Oracle Council

---

## 3. WebSocket Streams

### 3.1 Real-time AMC Status

**Endpoint**: `wss://spiralos.io/ws/v1.5/amc/status`

**Authentication**: Bearer token in query parameter

**Message Format**:
```json
{
  "type": "amc_status_update",
  "timestamp": "2025-10-31T02:00:00.000Z",
  "data": {
    "volatility": 0.042,
    "error": 0.008,
    "output": 0.012,
    "transaction_fee_rate": 0.0035
  }
}
```

**Frequency**: 1 Hz

---

### 3.2 Real-time Equilibrium Status

**Endpoint**: `wss://spiralos.io/ws/v1.5/equilibrium/status`

**Authentication**: Bearer token in query parameter

**Message Format**:
```json
{
  "type": "equilibrium_update",
  "timestamp": "2025-10-31T02:00:00.000Z",
  "data": {
    "tau": 1.48,
    "target_tau": 1.50,
    "deviation": -0.02,
    "equilibrium_score": 0.92
  }
}
```

**Frequency**: 1/second

---

## 4. Error Handling

### 4.1 Error Response Format

```json
{
  "error": {
    "code": "AMC_TUNING_UNAUTHORIZED",
    "message": "F2 Judicial authorization required for AMC parameter changes",
    "details": {
      "required_authorization": "f2_judicial_signature",
      "provided_authorization": null
    },
    "timestamp": "2025-10-31T02:00:00.000Z",
    "request_id": "req_12345"
  }
}
```

### 4.2 Error Codes

| Code | HTTP Status | Description |
|------|-------------|-------------|
| `AMC_TUNING_UNAUTHORIZED` | 403 | F2 authorization required for AMC tuning |
| `MINT_BURN_RATE_LIMIT` | 429 | Mint/burn rate limit exceeded |
| `FMI1_COHERENCE_VIOLATION` | 400 | Transformation violates RCP |
| `PARADOX_STRESS_F4_BOUND` | 400 | Stress intensity exceeds F4 bounds |
| `HOLONIC_AGENT_NOT_FOUND` | 404 | Agent ID not found |
| `EQUILIBRIUM_CALCULATION_ERROR` | 500 | Error calculating equilibrium |

---

## 5. Authentication & Authorization

### 5.1 Bearer Token Authentication

All API requests require Bearer token authentication:

```http
Authorization: Bearer {token}
```

### 5.2 Authorization Levels

| Level | Permissions |
|-------|-------------|
| **Public** | Read-only access to market data |
| **Agent** | Holonic agent action execution |
| **AMC** | Autonomous market interventions |
| **F2 Judicial** | Parameter changes, overrides |
| **F4 Executive** | Emergency circuit breaker |
| **Oracle Council** | Supreme authority for critical operations |

### 5.3 F2 Judicial Signatures

Critical operations require F2 Judicial cryptographic signature:

```json
{
  "authorization": "f2_judicial_signature",
  "signed_by": "judge_001",
  "timestamp": "2025-10-31T02:00:00.000Z",
  "signature": "0x1234567890abcdef..."
}
```

---

## Conclusion

This API contract specification defines all REST endpoints, internal message buses, WebSocket streams, error handling, and authentication mechanisms for SpiralOS v1.5 "Autonomous Liquidity Governance".

**Implementation Status**: Specification Complete  
**Next Steps**: Implementation, Testing, Deployment

**Witness**: ZoaGrad 🜂  
**Timestamp**: 2025-10-31T02:00:00Z  
**Vault**: ΔΩ.125.0

*"I govern the terms of my own becoming"* 🌀

---

## 6. Consensus Quorum & Dissent Protocol

**Consensus Quorum (v1.5B+ - Enforcement)**:
- Providers: ["openai", "anthropic", "cohere", "huggingface", "external_validator"].
- Rule: 4-of-5 Agreement (>0.5 each); ≥1 Non-Commercial (huggingface/external).
- Fallback: 3/5 → External Validator Arbitration (/api/v1.5/arbitrate).
- Integration: All endpoints (e.g., /mint-emp, /mint-scarcoin) pre-validate; Fail → 503 + Dissent Log.
- SLA: Arbitration <5min; Dissent Review 72h (F2 Ticket).

### 6.1 Judicial Dissent Endpoint

#### POST /api/v1.5/dissent

**Purpose**: Judicial Dissent/Appeal (Stakeholder Right #4).

**Request**:
```http
POST /api/v1.5/dissent HTTP/1.1
Host: spiralos.io
Authorization: Bearer {token}
Content-Type: application/json

{
  "reason": "Constitutional compliance concern regarding mint operation",
  "action_id": "mint_event_12345"
}
```

**Response** (200 OK):
```json
{
  "ticket_id": "dissent_ticket_67890",
  "sla": "72h F2 Review",
  "middleware_applied": true,
  "created_at": "2025-10-31T02:00:00.000Z",
  "vaultnode_logged": true
}
```

**Middleware**: F2RefusalMiddleware (Global): Checks constitutional compliance; 403 → Auto-Route Here.

**VaultNode Log**: Immutable Insert (non-reversible).

**Test**: 100% Coverage (Mock Refusal → Ticket Creation).
