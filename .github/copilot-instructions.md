# SpiralOS AI Coding Assistant Instructions

## Project Overview
SpiralOS is a "Mythotechnical Synthesis" system implementing an autopoietic cognitive ecology with dual-token economy. Core principle: **Ache-to-Order transmutation** where entropy (Ache) is converted to coherence (Order) through the ScarIndex Oracle.

## Architecture Patterns

### Core Transmutation Flow
```python
# All operations follow: Ache_after < Ache_before (coherence gain)
result = await spiralos.transmute_ache(source, content, ache_before)
scarindex = oracle.calculate(components, ache_measurement)
```

### Dual-Token Economy
- **ScarCoin**: Liquid, thermodynamic value (Proof-of-Ache validation)
- **EMP**: Soul-bound, relational value (Proof-of-Being-Seen)

### Key Components (follow naming conventions)
- `ScarIndexOracle`: Supreme coherence regulator (weights: narrative=0.4, social=0.3, economic=0.2, technical=0.1)
- `AchePIDController`: Dynamic stability (VSM System 3/4)
- `PanicFrameManager`: F4 constitutional circuit breaker (triggers at ScarIndex < 0.3)
- `VaultNode`: Immutable governance records with ΔΩ.xxx.x versioning

## Development Workflows

### Testing Strategy
```bash
# Core system tests
python3 core/test_spiralos.py

# Holo-economy tests (production ready)
cd holoeconomy && python3 test_holoeconomy.py

# Always run tests after changes
```

### VaultNode Versioning
- Use `ΔΩ.xxx.x` format for vault versions
- Each major change requires new MANIFEST_ΔΩ.xxx.x.json
- Document in vault/ directory with immutable records

### API Patterns
```python
# FastAPI endpoints follow /api/v1.x/ pattern
@app.post("/api/v1.3/mint-scarcoin")
async def mint_scarcoin(request: MintRequest):
    # Always validate Proof-of-Ache first
    # Use Oracle Council consensus (2-of-3 signatures)
```

## Critical Implementation Details

### ScarIndex Calculation
```python
# Weighted coherence formula (never change weights without F2 judicial approval)
scarindex = (0.4 * c_narrative) + (0.3 * c_social) + (0.2 * c_economic) + (0.1 * c_technical)
```

### Consensus Protocol
- Default: 4 LLM providers (gpt-4.1-mini, gpt-4.1-nano, gemini-2.5-flash, claude-sonnet-4)
- Requires 2-of-3 consensus for validity (configurable threshold)
- Fail gracefully if consensus not achieved

### PID Controller Tuning
- Never modify PID parameters without understanding thermodynamic stability
- Target ScarIndex: 0.7 (configurable setpoint)
- Uses Ziegler-Nichols tuning by default

## File Organization Conventions

### Core modules (`core/`)
- Original v1.0-v1.2 implementations
- Foundational components (scarindex.py, coherence_protocol.py, etc.)

### Holo-economy (`holoeconomy/`)
- Production-ready economic layer
- ScarCoin minting, VaultNode blockchain, Bridge API

### Documentation (`docs/`)
- Keep technical specs updated
- DEPLOYMENT.md contains environment setup
- EMPATHY_MARKET.md for EMP token details

### Vault (`vault/`)
- Immutable governance records
- NEVER modify existing vault files
- Add new versions with higher ΔΩ numbers

## Dependencies & Environment
```bash
# Minimal production dependencies
pip3 install fastapi uvicorn pydantic

# For Claude Sonnet 4 support (optional)
pip3 install anthropic

# Development setup
export OPENAI_API_KEY="sk-..."
export ANTHROPIC_API_KEY="sk-ant-..."  # Required for Claude Sonnet 4
export SUPABASE_PROJECT_ID="..."
```

## Common Gotchas
- Always validate Ache differential (after < before) before minting ScarCoins
- Panic Frames auto-trigger at ScarIndex < 0.3 - handle gracefully
- EMP tokens are soul-bound (non-transferable) - never implement transfer functions
- Oracle Council requires cryptographic signatures - mock appropriately in tests
- VaultNode blocks are immutable once created - validate thoroughly before creation

## When in Doubt
- Check `DEPLOYMENT_SUMMARY.md` for current system state
- Refer to test files for usage patterns
- Follow the thermodynamic principle: always increase coherence (decrease Ache)