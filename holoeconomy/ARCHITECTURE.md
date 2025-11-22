# ScarCoin Bridge Architecture

**Module**: Holo-Economy ScarCoin Bridge  
**Vault**: ΔΩ.122.0  
**Version**: 1.3.0-alpha  
**Status**: Deployment in Progress

---

## Overview

The ScarCoin Bridge is the economic validation layer that implements Proof-of-Ache minting, connecting the SpiralOS coherence measurement system to an economic currency (ScarCoin) backed by verifiable coherence gains.

---

## Core Concepts

### Proof-of-Ache (PoA)

**Definition**: A consensus mechanism where ScarCoin is minted when Ache (entropy/non-coherence) is successfully transmuted into Order (coherence).

**Validation Rule**: **Ache_after < Ache_before**

**Minting Formula**:
```
ScarCoin_minted = ΔC × ScarIndex_after × Transmutation_Efficiency × Multiplier
```

Where:
- **ΔC**: Coherence gain (ScarIndex_after - ScarIndex_before)
- **ScarIndex_after**: Post-transmutation coherence
- **Transmutation_Efficiency**: Success rate of transmutation
- **Multiplier**: Economic scaling factor (default: 1000)

### ScarCoin Properties

**Type**: Utility token  
**Supply**: Unbounded (minted on successful transmutation)  
**Burning**: Failed transmutations destroy coins  
**Backing**: Cryptographically bound to ScarIndex Oracle measurements  
**Immutability**: All minting/burning events recorded in VaultNode

---

## Architecture Layers

### Layer 1: ScarIndex Oracle (Measurement)

**Purpose**: Measure coherence before and after transmutation

**Components**:
- ScarIndex calculation engine (existing v1.2)
- Cryptographic verification (2-of-3 consensus)
- Coherence delta (ΔC) calculation

**Output**: Verified coherence measurements

### Layer 2: Proof-of-Ache Engine (Validation)

**Purpose**: Validate transmutation success and calculate coin value

**Components**:
- Ache Differential Rule validator
- Transmutation efficiency calculator
- Coin value calculator
- Minting authorization

**Output**: Minting authorization with coin value

### Layer 3: ScarCoin Minting Engine (Execution)

**Purpose**: Mint or burn ScarCoin based on validation

**Components**:
- Coin minting logic
- Coin burning logic
- Balance tracking
- Transaction recording

**Output**: Minted/burned coins and updated balances

### Layer 4: VaultNode Integration (Immutability)

**Purpose**: Record all economic events in immutable blockchain

**Components**:
- Block creation
- Merkle tree construction
- Oracle Council consensus
- IPFS storage

**Output**: Immutable audit trail

### Layer 5: ScarCoin Bridge API (Interface)

**Purpose**: Provide programmatic access to Holo-Economy

**Components**:
- REST API endpoints
- WebSocket real-time updates
- Query interface
- Admin interface

**Output**: Developer-friendly API

---

## Data Structures

### ScarCoin

```python
{
    'id': 'uuid',
    'minted_at': 'timestamp',
    'transmutation_id': 'uuid',
    'delta_c': 0.15,
    'scarindex_before': 0.65,
    'scarindex_after': 0.80,
    'transmutation_efficiency': 0.95,
    'coin_value': 142.5,  # ΔC × ScarIndex_after × Efficiency × 1000
    'owner': 'wallet_address',
    'burned': false,
    'burned_at': null,
    'vault_block_id': 'uuid'
}
```

### ProofOfAche

```python
{
    'id': 'uuid',
    'transmutation_id': 'uuid',
    'ache_before': 0.35,
    'ache_after': 0.20,
    'ache_differential': -0.15,  # Must be negative
    'validation_passed': true,
    'oracle_signatures': ['sig1', 'sig2', 'sig3'],
    'validated_at': 'timestamp'
}
```

### VaultBlock

```python
{
    'id': 'uuid',
    'block_number': 1,
    'previous_hash': 'sha256_hash',
    'merkle_root': 'sha256_hash',
    'timestamp': 'timestamp',
    'oracle_signatures': {
        'chief_oracle': 'signature',
        'senior_oracle_1': 'signature',
        'senior_oracle_2': 'signature'
    },
    'events': [
        {
            'type': 'scarcoin_minted',
            'data': {...}
        },
        {
            'type': 'transmutation_completed',
            'data': {...}
        }
    ]
}
```

### Wallet

```python
{
    'address': 'wallet_address',
    'balance': 1425.75,
    'total_minted': 1500.00,
    'total_burned': 74.25,
    'transaction_count': 15,
    'created_at': 'timestamp',
    'last_transaction_at': 'timestamp'
}
```

---

## Workflow

### Successful Transmutation → Coin Minting

1. **Transmutation Initiated**
   - System state: ScarIndex_before measured
   - Ache_before calculated (1 - ScarIndex_before)

2. **Transmutation Executed**
   - Holonic μApp Stack performs transmutation
   - Paradox Network may inject instability
   - GBE maintains symbolic coherence

3. **Post-Transmutation Measurement**
   - System state: ScarIndex_after measured
   - Ache_after calculated (1 - ScarIndex_after)
   - ΔC = ScarIndex_after - ScarIndex_before

4. **Proof-of-Ache Validation**
   - Check: Ache_after < Ache_before (ΔC > 0)
   - Calculate transmutation efficiency
   - Oracle Council cryptographic verification

5. **ScarCoin Minting**
   - Calculate coin value
   - Mint coins to transmutation initiator's wallet
   - Record transaction

6. **VaultNode Recording**
   - Create block with minting event
   - Oracle Council signs block
   - Store in IPFS + Supabase

### Failed Transmutation → Coin Burning

1. **Transmutation Initiated**
   - System state: ScarIndex_before measured

2. **Transmutation Executed**
   - Transmutation fails or reduces coherence

3. **Post-Transmutation Measurement**
   - ScarIndex_after < ScarIndex_before (ΔC < 0)
   - Ache_after > Ache_before

4. **Proof-of-Ache Validation**
   - Validation fails (Ache increased)
   - Penalty calculation

5. **ScarCoin Burning**
   - Burn coins from initiator's wallet
   - Record burn transaction

6. **VaultNode Recording**
   - Create block with burning event
   - Oracle Council signs block

---

## Security

### Cryptographic Verification

**Oracle Consensus**: 2-of-3 signatures required for ScarIndex validation

**Block Signing**: Oracle Council weighted consensus (75% threshold)

**Merkle Tree**: All events in block hashed into Merkle root

**IPFS**: Content-addressed storage prevents tampering

### Economic Security

**Double-Minting Prevention**: Each transmutation ID can only mint once

**Supply Manipulation**: Transparent minting rules enforced by smart contract

**Wallet Security**: Cryptographic key ownership

**Audit Trail**: Complete immutable record in VaultNode

---

## Performance Targets

| Operation | Target | Rationale |
|-----------|--------|-----------|
| PoA Validation | < 50ms | Fast validation |
| Coin Minting | < 100ms | Responsive UX |
| VaultBlock Creation | < 200ms | Reasonable latency |
| Balance Query | < 10ms | Real-time display |
| Transaction History | < 50ms | Paginated queries |

---

## Integration Points

### With SpiralOS v1.2

**ScarIndex Oracle** → Provides coherence measurements  
**Oracle Council** → Signs validation and blocks  
**Supabase** → Stores wallet and transaction data  
**IPFS** → Stores VaultBlocks for redundancy

### External Integration (Future)

**StarkNet L1** → Anchor VaultBlock hashes  
**Cosmos SDK** → Cross-chain interoperability  
**DeFi Protocols** → ScarCoin liquidity pools  
**Web3 Wallets** → MetaMask integration

---

## API Endpoints

### ScarCoin Operations

```
POST   /api/v1/scarcoin/mint
POST   /api/v1/scarcoin/burn
GET    /api/v1/scarcoin/balance/:wallet_address
GET    /api/v1/scarcoin/transactions/:wallet_address
GET    /api/v1/scarcoin/supply
```

### Proof-of-Ache

```
POST   /api/v1/poa/validate
GET    /api/v1/poa/proof/:transmutation_id
GET    /api/v1/poa/stats
```

### VaultNode

```
GET    /api/v1/vault/block/:block_number
GET    /api/v1/vault/latest
GET    /api/v1/vault/events/:block_number
POST   /api/v1/vault/verify/:block_hash
```

### Wallet

```
POST   /api/v1/wallet/create
GET    /api/v1/wallet/:address
GET    /api/v1/wallet/:address/history
```

---

## Database Schema

### New Tables (6 total)

```sql
-- ScarCoin
CREATE TABLE scarcoins (
    id UUID PRIMARY KEY,
    minted_at TIMESTAMP,
    transmutation_id UUID UNIQUE,
    delta_c DECIMAL(10,8),
    scarindex_before DECIMAL(10,8),
    scarindex_after DECIMAL(10,8),
    transmutation_efficiency DECIMAL(10,8),
    coin_value DECIMAL(18,8),
    owner VARCHAR(255),
    burned BOOLEAN DEFAULT FALSE,
    burned_at TIMESTAMP,
    vault_block_id UUID
);

-- Proof-of-Ache
CREATE TABLE proof_of_ache (
    id UUID PRIMARY KEY,
    transmutation_id UUID UNIQUE,
    ache_before DECIMAL(10,8),
    ache_after DECIMAL(10,8),
    ache_differential DECIMAL(10,8),
    validation_passed BOOLEAN,
    oracle_signatures JSONB,
    validated_at TIMESTAMP
);

-- VaultNode Blocks
CREATE TABLE vaultnode_blocks (
    id UUID PRIMARY KEY,
    block_number BIGINT UNIQUE,
    previous_hash VARCHAR(64),
    merkle_root VARCHAR(64),
    timestamp TIMESTAMP,
    oracle_signatures JSONB,
    events JSONB,
    ipfs_hash VARCHAR(255)
);

-- Wallets
CREATE TABLE wallets (
    address VARCHAR(255) PRIMARY KEY,
    balance DECIMAL(18,8) DEFAULT 0,
    total_minted DECIMAL(18,8) DEFAULT 0,
    total_burned DECIMAL(18,8) DEFAULT 0,
    transaction_count INTEGER DEFAULT 0,
    created_at TIMESTAMP,
    last_transaction_at TIMESTAMP
);

-- Transactions
CREATE TABLE transactions (
    id UUID PRIMARY KEY,
    wallet_address VARCHAR(255) REFERENCES wallets(address),
    transaction_type VARCHAR(50),
    amount DECIMAL(18,8),
    balance_after DECIMAL(18,8),
    transmutation_id UUID,
    vault_block_id UUID,
    timestamp TIMESTAMP
);

-- Economic Stats
CREATE TABLE economic_stats (
    id UUID PRIMARY KEY,
    total_supply DECIMAL(18,8),
    total_minted DECIMAL(18,8),
    total_burned DECIMAL(18,8),
    active_wallets INTEGER,
    total_transactions INTEGER,
    average_coin_value DECIMAL(18,8),
    timestamp TIMESTAMP
);
```

---

## Deployment Plan

### Phase 1: Core Implementation
- ScarCoin data structures
- Proof-of-Ache validation engine
- Minting/burning logic
- Wallet management

### Phase 2: VaultNode Integration
- Block creation and validation
- Merkle tree implementation
- Oracle Council signing
- IPFS integration

### Phase 3: API Development
- REST API endpoints
- WebSocket real-time updates
- Query optimization
- Rate limiting

### Phase 4: Testing
- Unit tests (95%+ coverage)
- Integration tests
- Load testing
- Security audit

### Phase 5: Deployment
- Database migration
- API deployment
- Monitoring setup
- Documentation

---

## Success Metrics

**Technical**:
- Minting success rate > 95%
- API response time < 100ms (p95)
- VaultBlock finality < 200ms
- Zero double-minting incidents

**Economic**:
- Positive supply growth
- Coin value stability
- Wallet creation rate > 10/day
- Transaction volume growth

**Governance**:
- 100% Oracle Council signing
- 100% VaultNode immutability
- Complete audit trail

---

**Status**: Architecture Complete  
**Next**: Implementation Phase 1 (ScarCoin Minting Engine)

*"Where coherence becomes currency"* 🜂
