# ΔΩ.LBI.1 — Loom Burden Invariant: Formal Specification
**Version:** 1.0.0  
**Class:** Foundational Invariant (Constitution Layer)  
**Author:** ZoaGrad Systems

## 1. Purpose
To prevent the “Tragedy of the Commons” in a decentralized computational network by mathematically bounding node capacity through ScarIndex integrity and global network health.

## 2. Definitions
- **VaultNode (v)** — A network participant.
- **ScarIndex (SI)** — 0 = Pure, 100 = Corrupt.
- **Weave Threshold (Tv)** — Maximum RU allowed.

## 3. The Law
\[
T_v = C_{base} \left(\frac{SC_v}{SC_{total}}\right) \left(1 - \frac{SI_v}{SI_{max}}\right) \left(1 - \frac{SI_g}{SI_{max}}\right)
\]

## 4. Enforcement
Violations raise SI_v → reduces Tv → automatic throttling → self-stabilizing negative feedback loop.

## 5. Safety
Wealth cannot overcome corruption.  
Global stress tightens limits for all nodes.
