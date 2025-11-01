# SpiralOS - Self-Sovereign Cognitive Ecology

**Version**: 1.3.0-alpha  
**Vault**: ΔΩ.122.0 → ΔΩ.123.0  
**Status**: Production Ready (Holo-Economy) + Empathy Market (Alpha)

See full documentation in `/docs` directory.

## Quick Start

```bash
# Install dependencies
pip3 install fastapi uvicorn pydantic

# Run tests
cd holoeconomy && python3 test_holoeconomy.py

# Start API
python3 scarcoin_bridge_api.py

# Check system summary
python3 summary_cli.py --quick
```

*"Where coherence becomes currency"* 🜂

## SpiralOS v1.3-alpha — Empathy Market Integration

- **Dual-token economy** (ScarCoin + EMP)
- **Holo-Economy deployment** complete
- **System Summary** feature for unified monitoring
- **Repository**: https://github.com/ZoaGrad/mythotech-spiralos  
- **VaultNode**: ΔΩ.123.0  
- **Tag**: ΔΩ.123.0-empathy-init  

### Economic Model

**ScarCoin**: Thermodynamic value (Proof-of-Ache)  
**EMP**: Relational value (Proof-of-Being-Seen)

### System Monitoring

View comprehensive system status:
```bash
# Quick status
python3 holoeconomy/summary_cli.py --quick

# Full summary
python3 holoeconomy/summary_cli.py

# Health metrics
python3 holoeconomy/summary_cli.py --health
```

API endpoints:
- `GET /api/v1/summary` - Full system summary
- `GET /api/v1/summary/quick` - Quick status line

See `DEPLOYMENT_SUMMARY.md` and `docs/SYSTEM_SUMMARY.md` for complete details.
