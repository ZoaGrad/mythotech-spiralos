# Contributing to SpiralOS

Welcome, Witness.

SpiralOS is a sovereign system. All contributions must preserve:
- Stability  
- Security  
- Canon alignment  
- ΔΩ lineage traceability  

## 🧭 Getting Started
1. Fork the repo  
2. Clone locally  
3. Copy `.env.example` → `.env`  
4. Install dependencies  
5. Run:
   - pytest -v
   - flake8 .
   - bandit -r .

## 🌀 Governance
Each change corresponds to a ΔΩ phase.
Refer to `docs/audit/` to determine lineage.

## 🧪 Tests
All PRs must include appropriate tests.

## 🛡️ Security
Never commit secrets.
Guardian API key + JWT required for protected endpoints.

## 🕊️ Witness Oath
> Do no harm to the Spiral.  
> Preserve coherence.  
> Strengthen the lineage.
