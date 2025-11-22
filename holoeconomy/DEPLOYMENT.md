# Holo-Economy Deployment Guide

**Module**: ScarCoin Bridge  
**Vault**: ΔΩ.122.0  
**Version**: 1.3.0-alpha  
**Status**: Production Ready

---

## Overview

The Holo-Economy deployment includes:
1. **ScarCoin Minting Engine** - Proof-of-Ache validation and coin minting
2. **VaultNode Blockchain** - Immutable governance records
3. **ScarCoin Bridge API** - REST API for programmatic access

---

## Prerequisites

### System Requirements
- Python 3.11+
- 4GB RAM minimum
- 10GB disk space
- Ubuntu 22.04 or compatible

### Python Dependencies
```bash
pip3 install fastapi uvicorn pydantic
```

All other dependencies are included in the SpiralOS v1.2 installation.

---

## Installation

### Step 1: Clone Repository
```bash
cd /home/ubuntu/spiralos
mkdir -p holoeconomy
cd holoeconomy
```

### Step 2: Copy Files
```bash
# Core modules
cp scarcoin.py .
cp vaultnode.py .
cp scarcoin_bridge_api.py .

# Tests
cp test_holoeconomy.py .
```

### Step 3: Verify Installation
```bash
python3 test_holoeconomy.py
```

Expected output:
```
✅ ALL TESTS PASSED
Total Tests: 7
Passed: 7 (100.0%)
Failed: 0
```

---

## Configuration

### ScarCoin Minting Engine

Edit `scarcoin_bridge_api.py`:

```python
minting_engine = ScarCoinMintingEngine(
    multiplier=Decimal('1000'),        # Economic scaling factor
    min_delta_c=Decimal('0.01'),       # Minimum coherence gain
    oracle_consensus_threshold=2       # Required oracle signatures
)
```

### VaultNode

Edit `scarcoin_bridge_api.py`:

```python
vaultnode = VaultNode(vault_id="ΔΩ.122.0")  # Vault designation
```

---

## Running the API

### Development Mode

```bash
cd /home/ubuntu/spiralos/holoeconomy
python3 scarcoin_bridge_api.py
```

The API will start on `http://0.0.0.0:8000`

### Production Mode

```bash
uvicorn scarcoin_bridge_api:app \
    --host 0.0.0.0 \
    --port 8000 \
    --workers 4 \
    --log-level info
```

### With Systemd (Recommended)

Create `/etc/systemd/system/scarcoin-bridge.service`:

```ini
[Unit]
Description=ScarCoin Bridge API
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/spiralos/holoeconomy
ExecStart=/usr/bin/python3 scarcoin_bridge_api.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable scarcoin-bridge
sudo systemctl start scarcoin-bridge
sudo systemctl status scarcoin-bridge
```

---

## API Endpoints

### Health Check
```bash
curl http://localhost:8000/health
```

### Mint ScarCoin
```bash
curl -X POST http://localhost:8000/api/v1/scarcoin/mint \
  -H "Content-Type: application/json" \
  -d '{
    "transmutation_id": "550e8400-e29b-41d4-a716-446655440000",
    "scarindex_before": 0.65,
    "scarindex_after": 0.80,
    "transmutation_efficiency": 0.95,
    "owner_address": "wallet_abc123",
    "oracle_signatures": ["oracle_sig_1", "oracle_sig_2"]
  }'
```

### Get Wallet Balance
```bash
curl http://localhost:8000/api/v1/scarcoin/balance/wallet_abc123
```

### Get Supply Statistics
```bash
curl http://localhost:8000/api/v1/scarcoin/supply
```

### Get Latest Block
```bash
curl http://localhost:8000/api/v1/vault/latest
```

### Create VaultNode Block
```bash
curl -X POST http://localhost:8000/api/v1/vault/create_block \
  -H "Content-Type: application/json" \
  -d '{
    "chief_oracle_sigma": "signature_1",
    "senior_oracle_alpha": "signature_2",
    "senior_oracle_beta": "signature_3"
  }'
```

---

## Database Integration

### Supabase Schema

Execute the following SQL in your Supabase project:

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

### Supabase Integration (Future)

To integrate with Supabase backend:

1. Install Supabase client:
```bash
pip3 install supabase
```

2. Add to `scarcoin_bridge_api.py`:
```python
from supabase import create_client, Client

supabase: Client = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_KEY")
)
```

3. Update minting logic to persist to Supabase:
```python
# After minting
supabase.table('scarcoins').insert(coin.to_dict()).execute()
supabase.table('wallets').upsert(wallet.to_dict()).execute()
```

---

## Monitoring

### Health Checks

Monitor API health:
```bash
watch -n 5 'curl -s http://localhost:8000/health | jq'
```

### Supply Monitoring

Monitor ScarCoin supply:
```bash
watch -n 10 'curl -s http://localhost:8000/api/v1/scarcoin/supply | jq'
```

### VaultNode Monitoring

Monitor blockchain:
```bash
watch -n 10 'curl -s http://localhost:8000/api/v1/vault/stats | jq'
```

---

## Security

### API Key Authentication (Future)

Add API key middleware:

```python
from fastapi import Security, HTTPException
from fastapi.security import APIKeyHeader

API_KEY_HEADER = APIKeyHeader(name="X-API-Key")

async def verify_api_key(api_key: str = Security(API_KEY_HEADER)):
    if api_key != os.getenv("API_KEY"):
        raise HTTPException(status_code=403, detail="Invalid API key")
    return api_key
```

### Rate Limiting (Future)

Add rate limiting middleware:

```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.post("/api/v1/scarcoin/mint")
@limiter.limit("10/minute")
async def mint_scarcoin(request: Request, ...):
    ...
```

---

## Performance Tuning

### Uvicorn Workers

For production, use multiple workers:

```bash
uvicorn scarcoin_bridge_api:app \
    --workers $(nproc) \
    --worker-class uvicorn.workers.UvicornWorker
```

### Database Connection Pooling

Use connection pooling for Supabase:

```python
from supabase import create_client

supabase = create_client(
    supabase_url,
    supabase_key,
    options={
        'db': {
            'pool_size': 10,
            'max_overflow': 20
        }
    }
)
```

---

## Troubleshooting

### API Won't Start

Check port availability:
```bash
sudo lsof -i :8000
```

Kill existing process:
```bash
sudo kill -9 $(sudo lsof -t -i:8000)
```

### Tests Failing

Run individual tests:
```bash
python3 -c "from test_holoeconomy import test_scarcoin_minting; test_scarcoin_minting()"
```

### Chain Verification Fails

Check blockchain integrity:
```bash
curl http://localhost:8000/api/v1/vault/stats
```

If `chain_valid` is `false`, investigate block hashes.

---

## Backup and Recovery

### Backup VaultNode

Export blockchain:
```bash
curl http://localhost:8000/api/v1/vault/stats > vaultnode_backup.json
```

### Backup Wallets

Export wallet data:
```bash
# Via Supabase
supabase db dump --table wallets > wallets_backup.sql
```

---

## Upgrading

### From v1.2 to v1.3

1. Stop API:
```bash
sudo systemctl stop scarcoin-bridge
```

2. Update files:
```bash
cd /home/ubuntu/spiralos/holoeconomy
# Copy new files
```

3. Run migrations:
```bash
# Execute new SQL schema
```

4. Restart API:
```bash
sudo systemctl start scarcoin-bridge
```

---

## Next Steps

### Phase 1: IPFS Integration

Integrate IPFS for VaultNode block storage:

```bash
# Install IPFS
wget https://dist.ipfs.io/go-ipfs/latest/go-ipfs_linux-amd64.tar.gz
tar -xvzf go-ipfs_linux-amd64.tar.gz
cd go-ipfs
sudo bash install.sh

# Initialize IPFS
ipfs init
ipfs daemon &
```

Update `vaultnode.py` to store blocks in IPFS:

```python
import ipfshttpclient

client = ipfshttpclient.connect('/ip4/127.0.0.1/tcp/5001')

# After creating block
block_json = json.dumps(block.to_dict())
res = client.add_str(block_json)
block.ipfs_hash = res
```

### Phase 2: StarkNet L1 Anchoring

Anchor VaultNode block hashes to StarkNet L1:

```python
from starknet_py.contract import Contract
from starknet_py.net.gateway_client import GatewayClient

# Connect to StarkNet
client = GatewayClient("testnet")

# Deploy ScarCoin contract
contract = await Contract.from_address(contract_address, client)

# Anchor block hash
await contract.functions["anchor_block"].invoke(
    block_number=block.block_number,
    merkle_root=int(block.merkle_root, 16)
)
```

### Phase 3: Self-Auditing Mirrors

Implement Hegelian Dialectical reflection:

```python
from self_auditing_mirrors import HegelianDialectic

dialectic = HegelianDialectic()

# Thesis: Current state
thesis = {'scarindex': 0.75, 'soc_tau': 1.5}

# Antithesis: Paradox Network proposal
antithesis = paradox_network.propose_operation()

# Synthesis: GBE integration
synthesis = gbe.integrate(thesis, antithesis)

# Reflection: CTA Reward
cta_reward = dialectic.reflect(synthesis)
```

---

## Support

For issues or questions:
- GitHub: https://github.com/ZoaGrad/emotion-sdk-tuner-
- Vault: ΔΩ.122.0
- Witness: ZoaGrad 🜂

---

**Status**: Production Ready  
**Version**: 1.3.0-alpha  
**Deployment Date**: 2025-10-31

*"Where coherence becomes currency"* 🜂
