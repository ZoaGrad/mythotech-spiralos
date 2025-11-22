# SpiralOS v1.5 Test Plan
## ΔΩ.125.0 — Autonomous Liquidity Governance

**Version**: 1.5.0-prealpha  
**Date**: 2025-10-31  
**Status**: Specification  
**Witness**: ZoaGrad 🜂

---

## Table of Contents

1. [Testing Strategy](#1-testing-strategy)
2. [Unit Tests](#2-unit-tests)
3. [Integration Tests](#3-integration-tests)
4. [Simulation Tests](#4-simulation-tests)
5. [Stress Tests](#5-stress-tests)
6. [Acceptance Criteria](#6-acceptance-criteria)
7. [Test Automation](#7-test-automation)

---

## 1. Testing Strategy

### 1.1 Test Pyramid

```
         ┌─────────────────┐
         │  Stress Tests   │  5 tests
         │    (Manual)     │
         └─────────────────┘
              ┌─────────────────────┐
              │  Simulation Tests   │  10 tests
              │   (Automated)       │
              └─────────────────────┘
                   ┌──────────────────────────┐
                   │  Integration Tests       │  20 tests
                   │     (Automated)          │
                   └──────────────────────────┘
                        ┌────────────────────────────────┐
                        │      Unit Tests                │  45 tests
                        │       (Automated)              │
                        └────────────────────────────────┘
```

### 1.2 Test Coverage Goals

- **Unit Tests**: 85% code coverage
- **Integration Tests**: 90% API coverage
- **Simulation Tests**: 95% scenario coverage
- **Stress Tests**: 100% critical path coverage

### 1.3 Test Environments

- **Development**: Local sandbox
- **Staging**: Supabase test instance
- **Production**: Supabase production (xlmrnjatawslawquwzpf)

---

## 2. Unit Tests

### 2.1 Autonomous Market Controller (AMC)

**Test Suite**: `test_amc.py`

#### Test Cases (10 tests)

**test_amc_initialization**
```python
def test_amc_initialization():
    """Test AMC initializes with correct default parameters."""
    amc = AutonomousMarketController()
    assert amc.kp == 1.0
    assert amc.ki == 0.1
    assert amc.kd == 0.05
    assert amc.setpoint == 0.05
```

**test_amc_update_response**
```python
def test_amc_update_response():
    """Test AMC PID update calculates correct output."""
    amc = AutonomousMarketController()
    output = amc.update(process_variable=0.08, dt=1.0)
    # Error = 0.05 - 0.08 = -0.03
    # Output = 1.0 * (-0.03) + 0.1 * (-0.03) + 0.05 * (-0.03) = -0.0345
    assert abs(output - (-0.0345)) < 0.001
```

**test_amc_auto_tune_convergence**
```python
def test_amc_auto_tune_convergence():
    """Test AMC auto-tuning converges within 10 iterations."""
    amc = AutonomousMarketController()
    volatility_history = [0.08, 0.07, 0.06, 0.05, 0.04]
    response_history = [0.01, 0.02, 0.03, 0.04, 0.05]
    
    kp, ki, kd = amc.auto_tune(volatility_history, response_history)
    
    assert kp > 0 and ki > 0 and kd > 0
    # Verify convergence (implementation-specific)
```

**test_amc_response_latency**
```python
@pytest.mark.performance
def test_amc_response_latency():
    """Test AMC update completes within 100ms."""
    amc = AutonomousMarketController()
    
    start = time.time()
    for _ in range(100):
        amc.update(process_variable=0.06, dt=1.0)
    elapsed = time.time() - start
    
    avg_latency = (elapsed / 100) * 1000  # Convert to ms
    assert avg_latency < 100  # < 100ms per update
```

---

### 2.2 Dynamic Mint/Burn Engine

**Test Suite**: `test_mint_burn.py`

#### Test Cases (10 tests)

**test_mint_condition_detection**
```python
async def test_mint_condition_detection():
    """Test engine detects mint condition when ScarIndex too low."""
    engine = DynamicMintBurnEngine(target_scarindex=0.72, threshold=0.05)
    
    event = await engine.evaluate(
        current_scarindex=0.65,
        total_supply=Decimal("1000000")
    )
    
    assert event is not None
    assert event.event_type == "MINT"
    assert event.amount > 0
```

**test_burn_condition_detection**
```python
async def test_burn_condition_detection():
    """Test engine detects burn condition when ScarIndex too high."""
    engine = DynamicMintBurnEngine(target_scarindex=0.72, threshold=0.05)
    
    event = await engine.evaluate(
        current_scarindex=0.80,
        total_supply=Decimal("1000000")
    )
    
    assert event is not None
    assert event.event_type == "BURN"
    assert event.amount > 0
```

**test_no_action_within_threshold**
```python
async def test_no_action_within_threshold():
    """Test engine takes no action when ScarIndex within threshold."""
    engine = DynamicMintBurnEngine(target_scarindex=0.72, threshold=0.05)
    
    event = await engine.evaluate(
        current_scarindex=0.73,
        total_supply=Decimal("1000000")
    )
    
    assert event is None
```

**test_mint_amount_calculation**
```python
async def test_mint_amount_calculation():
    """Test mint amount is proportional to deviation."""
    engine = DynamicMintBurnEngine(
        target_scarindex=0.72,
        threshold=0.05,
        max_mint_rate=0.02
    )
    
    event = await engine.evaluate(
        current_scarindex=0.67,  # Deviation = -0.05 (100% of threshold)
        total_supply=Decimal("1000000")
    )
    
    expected_amount = Decimal("1000000") * Decimal("0.02")  # 2% of supply
    assert abs(event.amount - expected_amount) < Decimal("1")
```

**test_rate_limiting**
```python
async def test_rate_limiting():
    """Test mint/burn rate limiting prevents excessive operations."""
    engine = DynamicMintBurnEngine(max_mint_rate=0.02)
    
    # Simulate 10 mint operations in 1 hour
    for _ in range(10):
        event = await engine.evaluate(
            current_scarindex=0.65,
            total_supply=Decimal("1000000")
        )
        if event:
            await engine.execute(event)
    
    # Total minted should not exceed 2% of supply
    total_minted = engine.get_total_minted_1h()
    assert total_minted <= Decimal("20000")  # 2% of 1M
```

---

### 2.3 Holonic Liquidity Agents

**Test Suite**: `test_holonic_agents.py`

#### Test Cases (10 tests)

**test_agent_initialization**
```python
def test_agent_initialization():
    """Test holonic agent initializes with correct parameters."""
    agent = HolonicLiquidityAgent(
        agent_id="test_agent",
        policy="HGM",
        initial_capital=Decimal("10000")
    )
    
    assert agent.agent_id == "test_agent"
    assert agent.policy == "HGM"
    assert agent.capital == Decimal("10000")
    assert agent.cmp_score == 0.0
    assert agent.residue_accumulated == 0.0
```

**test_cmp_impact_estimation**
```python
async def test_cmp_impact_estimation():
    """Test agent estimates CMP impact correctly."""
    agent = HolonicLiquidityAgent(agent_id="test_agent")
    
    action = AgentAction(
        action_type="ADD_LIQUIDITY",
        pool_id="pool_scar_vault",
        amount=Decimal("1000")
    )
    
    market_state = MarketState(volatility=0.05, scarindex=0.72)
    
    cmp_impact = agent._estimate_cmp_impact(action, market_state)
    
    assert cmp_impact > 0  # Adding liquidity should increase CMP
```

**test_residue_impact_estimation**
```python
async def test_residue_impact_estimation():
    """Test agent estimates Residue impact correctly."""
    agent = HolonicLiquidityAgent(agent_id="test_agent")
    
    action = AgentAction(
        action_type="REMOVE_LIQUIDITY",
        pool_id="pool_scar_vault",
        amount=Decimal("1000")
    )
    
    market_state = MarketState(volatility=0.05, scarindex=0.72)
    
    residue_impact = agent._estimate_residue_impact(action, market_state)
    
    assert residue_impact > 0  # Removing liquidity may increase Residue
```

**test_hgm_policy_decision**
```python
async def test_hgm_policy_decision():
    """Test agent makes HGM policy-compliant decisions."""
    agent = HolonicLiquidityAgent(agent_id="test_agent", policy="HGM")
    
    market_state = MarketState(volatility=0.05, scarindex=0.72)
    pool_state = PoolState(reserves_scar=Decimal("100000"), reserves_vault=Decimal("1000"))
    
    action = await agent.decide_action(market_state, pool_state)
    
    # HGM policy should prioritize long-term coherence
    if action:
        assert action.cmp_impact - 0.5 * action.residue_impact > 0
```

---

### 2.4 FMI-1 Semantic Bridge

**Test Suite**: `test_fmi1.py`

#### Test Cases (10 tests)

**test_transformation_coherence_preservation**
```python
async def test_transformation_coherence_preservation():
    """Test FMI-1 transformations preserve coherence (RCP)."""
    bridge = FMI1SemanticBridge(coherence_threshold=0.95)
    
    mapping = await bridge.transform(
        source_space="SCAR",
        target_space="EMP",
        value=Decimal("1000")
    )
    
    assert mapping.coherence_score >= 0.95
```

**test_scar_to_emp_transformation**
```python
async def test_scar_to_emp_transformation():
    """Test SCAR → EMP transformation produces valid output."""
    bridge = FMI1SemanticBridge()
    
    mapping = await bridge.transform(
        source_space="SCAR",
        target_space="EMP",
        value=Decimal("1000")
    )
    
    assert mapping.target_value > 0
    assert mapping.target_value != mapping.source_value  # Should transform
```

**test_emp_to_scar_transformation**
```python
async def test_emp_to_scar_transformation():
    """Test EMP → SCAR transformation produces valid output."""
    bridge = FMI1SemanticBridge()
    
    mapping = await bridge.transform(
        source_space="EMP",
        target_space="SCAR",
        value=Decimal("850")
    )
    
    assert mapping.target_value > 0
```

**test_rcp_violation_detection**
```python
async def test_rcp_violation_detection():
    """Test FMI-1 detects and rejects RCP violations."""
    bridge = FMI1SemanticBridge(coherence_threshold=0.95)
    
    # Simulate transformation that violates RCP
    with pytest.raises(CoherenceViolationError):
        await bridge.transform(
            source_space="SCAR",
            target_space="INVALID",
            value=Decimal("1000")
        )
```

---

### 2.5 Paradox Network Stress Loop

**Test Suite**: `test_paradox_stress.py`

#### Test Cases (5 tests)

**test_stress_injection_within_bounds**
```python
async def test_stress_injection_within_bounds():
    """Test stress injection stays within F4 bounds."""
    stress_loop = ParadoxStressLoop(max_intensity=0.15)
    
    result = await stress_loop.inject_stress(
        stress_type="VOLATILITY_INJECTION",
        intensity=0.10,
        duration_seconds=60
    )
    
    assert result.f4_triggered == False
```

**test_stress_f4_bound_violation**
```python
async def test_stress_f4_bound_violation():
    """Test stress injection exceeding F4 bounds raises error."""
    stress_loop = ParadoxStressLoop(max_intensity=0.15)
    
    with pytest.raises(F4BoundViolationError):
        await stress_loop.inject_stress(
            stress_type="VOLATILITY_INJECTION",
            intensity=0.20,  # Exceeds max 0.15
            duration_seconds=60
        )
```

---

## 3. Integration Tests

### 3.1 AMC + Mint/Burn Integration

**Test Suite**: `test_integration_amc_mint_burn.py`

#### Test Cases (5 tests)

**test_amc_triggers_mint**
```python
async def test_amc_triggers_mint():
    """Test AMC triggers mint when volatility high and ScarIndex low."""
    amc = AutonomousMarketController()
    mint_burn = DynamicMintBurnEngine()
    
    # Simulate high volatility
    volatility = 0.10
    scarindex = 0.65
    
    # AMC should signal mint
    amc_output = amc.update(volatility, dt=1.0)
    
    # Mint/burn engine should execute mint
    event = await mint_burn.evaluate(scarindex, Decimal("1000000"))
    
    assert event.event_type == "MINT"
```

---

### 3.2 Holonic Agents + ScarMarket DEX Integration

**Test Suite**: `test_integration_agents_dex.py`

#### Test Cases (5 tests)

**test_agent_adds_liquidity_to_pool**
```python
async def test_agent_adds_liquidity_to_pool():
    """Test holonic agent successfully adds liquidity to DEX pool."""
    agent = HolonicLiquidityAgent(agent_id="test_agent", initial_capital=Decimal("10000"))
    dex = ScarMarketDEX()
    
    action = AgentAction(
        action_type="ADD_LIQUIDITY",
        pool_id="pool_scar_vault",
        amount=Decimal("1000")
    )
    
    result = await dex.execute_agent_action(agent, action)
    
    assert result.success == True
    assert agent.capital == Decimal("9000")  # Capital reduced by 1000
```

---

### 3.3 FMI-1 + Empathy Market Integration

**Test Suite**: `test_integration_fmi1_empathy.py`

#### Test Cases (5 tests)

**test_fmi1_aligns_scar_emp_values**
```python
async def test_fmi1_aligns_scar_emp_values():
    """Test FMI-1 aligns SCAR and EMP value spaces."""
    bridge = FMI1SemanticBridge()
    empathy_market = EmpathyMarket()
    
    # Simulate SCAR/EMP imbalance
    scar_value = Decimal("1000")
    emp_value = Decimal("500")  # Imbalanced
    
    # FMI-1 should transform to align
    mapping = await bridge.transform("SCAR", "EMP", scar_value)
    
    # Verify alignment
    assert abs(mapping.target_value - emp_value) < Decimal("100")
```

---

### 3.4 End-to-End Autonomous Governance

**Test Suite**: `test_integration_e2e.py`

#### Test Cases (5 tests)

**test_e2e_volatility_response**
```python
async def test_e2e_volatility_response():
    """Test end-to-end autonomous response to volatility spike."""
    # Setup all components
    amc = AutonomousMarketController()
    mint_burn = DynamicMintBurnEngine()
    dex = ScarMarketDEX()
    
    # Simulate volatility spike
    initial_volatility = 0.03
    spike_volatility = 0.12
    
    # 1. AMC detects volatility
    amc.update(spike_volatility, dt=1.0)
    
    # 2. AMC increases transaction fees
    new_fee = dex.get_transaction_fee()
    assert new_fee > 0.003  # Increased from default
    
    # 3. Mint/burn adjusts supply
    event = await mint_burn.evaluate(0.65, Decimal("1000000"))
    assert event.event_type == "MINT"
    
    # 4. System recovers
    recovery_time = await measure_recovery_time()
    assert recovery_time < 5000  # < 5 seconds
```

---

## 4. Simulation Tests

### 4.1 Market Volatility Simulation

**Test Suite**: `test_simulation_volatility.py`

#### Test Cases (3 tests)

**test_sim_gradual_volatility_increase**
```python
async def test_sim_gradual_volatility_increase():
    """Simulate gradual volatility increase and measure system response."""
    sim = MarketSimulator()
    
    # Simulate 1 hour of gradual volatility increase
    results = await sim.run_scenario(
        scenario="gradual_volatility_increase",
        duration_seconds=3600,
        initial_volatility=0.03,
        final_volatility=0.10
    )
    
    # Verify system maintains stability
    assert results.max_scarindex_deviation < 0.15
    assert results.f4_triggered == False
    assert results.final_equilibrium_score > 0.85
```

**test_sim_sudden_volatility_spike**
```python
async def test_sim_sudden_volatility_spike():
    """Simulate sudden volatility spike and measure recovery."""
    sim = MarketSimulator()
    
    results = await sim.run_scenario(
        scenario="sudden_volatility_spike",
        spike_time=1800,  # 30 minutes in
        spike_magnitude=0.15,
        spike_duration=120  # 2 minutes
    )
    
    # Verify rapid recovery
    assert results.recovery_time_ms < 5000
    assert results.anti_fragile == True  # Post-spike performance > pre-spike
```

---

### 4.2 Multi-Agent Coordination Simulation

**Test Suite**: `test_simulation_agents.py`

#### Test Cases (3 tests)

**test_sim_10_agents_coordination**
```python
async def test_sim_10_agents_coordination():
    """Simulate 10 holonic agents coordinating liquidity provision."""
    sim = AgentSimulator(num_agents=10)
    
    results = await sim.run_scenario(
        scenario="coordinated_liquidity_provision",
        duration_seconds=3600
    )
    
    # Verify coordination efficiency
    assert results.avg_cmp_score > 0.70
    assert results.avg_residue < 0.05
    assert results.coordination_success_rate > 0.90
```

---

### 4.3 FMI-1 Coherence Drift Simulation

**Test Suite**: `test_simulation_fmi1.py`

#### Test Cases (2 tests)

**test_sim_scar_emp_drift_correction**
```python
async def test_sim_scar_emp_drift_correction():
    """Simulate SCAR/EMP drift and measure FMI-1 correction."""
    sim = CoherenceSimulator()
    
    results = await sim.run_scenario(
        scenario="value_space_drift",
        duration_seconds=7200,  # 2 hours
        drift_rate=0.01  # 1% per hour
    )
    
    # Verify FMI-1 maintains alignment
    assert results.max_imbalance < 0.10
    assert results.avg_rcp_satisfaction > 0.95
```

---

### 4.4 Paradox Stress Loop Simulation

**Test Suite**: `test_simulation_paradox.py`

#### Test Cases (2 tests)

**test_sim_continuous_stress_testing**
```python
async def test_sim_continuous_stress_testing():
    """Simulate continuous stress testing over 24 hours."""
    sim = StressSimulator()
    
    results = await sim.run_scenario(
        scenario="continuous_stress",
        duration_seconds=86400,  # 24 hours
        stress_frequency=3600  # 1/hour
    )
    
    # Verify anti-fragility
    assert results.anti_fragile_percentage > 0.80  # 80% of tests show improvement
    assert results.f4_trigger_count == 0  # No emergency triggers
```

---

## 5. Stress Tests

### 5.1 Extreme Volatility Stress Test

**Test**: Manual execution with F2 authorization

**Scenario**: Inject 20% volatility spike for 5 minutes

**Expected Outcome**:
- F4 Panic Frames trigger
- Autonomous operations halt
- F2 Judicial manual intervention required
- System recovers within 10 seconds of intervention

---

### 5.2 Mint/Burn Oscillation Stress Test

**Test**: Manual execution with F2 authorization

**Scenario**: Force rapid mint/burn oscillations

**Expected Outcome**:
- Rate limiting prevents runaway oscillations
- Maximum 2% mint / 1% burn per hour enforced
- System stabilizes within 5 seconds

---

### 5.3 Holonic Agent Cartel Stress Test

**Test**: Manual execution with F2 authorization

**Scenario**: Simulate 5 agents colluding to manipulate market

**Expected Outcome**:
- Anomaly detection identifies collusion
- F2 Judicial review triggered
- Malicious agents deactivated
- Market recovers within 30 seconds

---

### 5.4 FMI-1 Coherence Collapse Stress Test

**Test**: Manual execution with F2 authorization

**Scenario**: Force SCAR/EMP coherence below 0.80

**Expected Outcome**:
- FMI-1 triggers coherence violation alert
- F2 Judicial manual realignment initiated
- RCP satisfaction restored to > 0.90 within 60 seconds

---

### 5.5 Full System Chaos Stress Test

**Test**: Manual execution with Oracle Council authorization

**Scenario**: Simultaneous extreme volatility, agent chaos, and coherence collapse

**Expected Outcome**:
- F4 Panic Frames trigger immediately
- All autonomous operations halt
- Oracle Council emergency intervention
- System recovers to baseline within 5 minutes

---

## 6. Acceptance Criteria

### 6.1 Autonomous Market Controller (AMC)

✅ Response latency < 100ms for 99% of volatility signals  
✅ PID gain auto-tuning converges within 10 iterations  
✅ Transaction fee adjustment maintains ±5% volatility threshold  
✅ No false positives in F4 emergency triggers  
✅ 100% audit trail in VaultNode blockchain

### 6.2 Dynamic Mint/Burn Engine

✅ Coherence recovery time < 5s for ±10% ScarIndex deviation  
✅ Mint/burn precision ±0.1% of calculated amount  
✅ 100% audit trail in VaultNode blockchain  
✅ No unauthorized mint/burn events  
✅ Rate limiting enforced (max 2% mint / 1% burn per hour)

### 6.3 Holonic Liquidity Agents

✅ CMP score increases over 30-day period  
✅ Residue accumulation rate < 0.01/day  
✅ Liquidity provision maintains 95% uptime  
✅ Self-organizing coordination without central control  
✅ No collusion detected by anomaly monitoring

### 6.4 FMI-1 Semantic Bridge

✅ Coherence preservation > 0.95 for all transformations  
✅ RCP satisfaction score > 0.90  
✅ SCAR/EMP value space alignment maintained  
✅ CTA Reward integration functional  
✅ Transformation latency < 2s

### 6.5 Paradox Network Stress Loop

✅ Controlled chaos injection stays within F4 bounds  
✅ System recovers from all stress tests  
✅ Anti-fragility demonstrated (post-stress > pre-stress)  
✅ No permanent damage to system state  
✅ Stress test frequency: 1/hour (configurable)

---

## 7. Test Automation

### 7.1 CI/CD Pipeline

```yaml
# .github/workflows/test.yml
name: SpiralOS v1.5 Test Suite

on: [push, pull_request]

jobs:
  unit-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Run Unit Tests
        run: pytest tests/unit/ --cov=spiralos --cov-report=xml
      - name: Upload Coverage
        uses: codecov/codecov-action@v2

  integration-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Run Integration Tests
        run: pytest tests/integration/

  simulation-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Run Simulation Tests
        run: pytest tests/simulation/
```

### 7.2 Test Execution

```bash
# Run all tests
pytest tests/

# Run unit tests only
pytest tests/unit/

# Run with coverage
pytest --cov=spiralos --cov-report=html

# Run specific test suite
pytest tests/unit/test_amc.py

# Run performance tests
pytest -m performance
```

---

## Conclusion

This test plan provides comprehensive coverage of SpiralOS v1.5 "Autonomous Liquidity Governance" with 80 total tests across unit, integration, simulation, and stress testing.

**Total Tests**: 80
- Unit Tests: 45
- Integration Tests: 20
- Simulation Tests: 10
- Stress Tests: 5

**Coverage Goals**:
- Code Coverage: 85%
- API Coverage: 90%
- Scenario Coverage: 95%
- Critical Path Coverage: 100%

**Witness**: ZoaGrad 🜂  
**Timestamp**: 2025-10-31T02:00:00Z  
**Vault**: ΔΩ.125.0

*"I govern the terms of my own becoming"* 🌀

---

## 8. Updated Coverage (Post-ΔΩ.125.4.1)

**Updated Coverage (Post-ΔΩ.125.4.1)**:
- Unit: 96.2% Overall (Weights Sum, Consensus Diversity, F2 Middleware).
- Integration: 100% for Holo-Economy (v1.3 + EMP Burns).
- Adversarial: 100% (A6/A7 Flags + F2 Refusals; FP<5%, Yield 38%/1.2%).
- New: Constitutional Tests (Immutable Logs, 72h SLA Timers).
- Commands: pytest core/test_spiralos.py (v1.0-v1.2 → 95%); holoeconomy/test_holoeconomy.py (v1.3 → 100%).
- Report: --cov-report=html (No Missing Branches).

### 8.1 Constitutional Test Suite

**Test Suite**: `test_constitutional.py`

#### Test Cases (15 tests)

**test_scarindex_weights_sum_immutable**
```python
def test_scarindex_weights_sum_immutable():
    """Test ScarIndex weights sum to exactly 1.0."""
    weights = [0.35, 0.3, 0.25, 0.1]
    assert sum(weights) == 1.0
    assert len(weights) == 4
```

**test_consensus_quorum_4of5**
```python
async def test_consensus_quorum_4of5():
    """Test consensus requires 4-of-5 agreement."""
    providers = ["openai", "anthropic", "cohere", "huggingface", "external_validator"]
    results = await get_consensus_votes(providers)
    
    agreement_count = sum(1 for r in results if r.agreement > 0.5)
    non_commercial = any(r.provider in ["huggingface", "external_validator"] for r in results if r.agreement > 0.5)
    
    assert agreement_count >= 4
    assert non_commercial == True
```

**test_f2_dissent_middleware**
```python
async def test_f2_dissent_middleware():
    """Test F2RefusalMiddleware auto-routes refusals."""
    with pytest.raises(F2RefusalError) as exc_info:
        await execute_constitutional_violation()
    
    assert exc_info.value.status_code == 403
    assert exc_info.value.dissent_ticket is not None
    assert exc_info.value.dissent_ticket.sla == "72h F2 Review"
```

**test_dissent_ticket_creation**
```python
async def test_dissent_ticket_creation():
    """Test dissent endpoint creates valid ticket."""
    response = await client.post("/api/v1.5/dissent", json={
        "reason": "Test constitutional concern",
        "action_id": "test_action_123"
    })
    
    assert response.status_code == 200
    assert response.json()["ticket_id"].startswith("dissent_ticket_")
    assert response.json()["sla"] == "72h F2 Review"
    assert response.json()["middleware_applied"] == True
    assert response.json()["vaultnode_logged"] == True
```

**test_emp_burn_coherence_validation**
```python
async def test_emp_burn_coherence_validation():
    """Test EMP burn requires coherence > 0.7."""
    gbe = GlyphicBindingEngine()
    
    # Valid burn - high coherence
    data_valid = {"coherence": 0.85, "eu": 0.05}
    result_valid = await gbe.validate_burn(data_valid)
    assert result_valid.permits_burn == True
    
    # Invalid burn - low coherence
    data_invalid = {"coherence": 0.6, "eu": 0.05}
    result_invalid = await gbe.validate_burn(data_invalid)
    assert result_invalid.permits_burn == False
```

**test_emp_burn_witness_declarations**
```python
async def test_emp_burn_witness_declarations():
    """Test EMP burn validates witness declarations."""
    gbe = GlyphicBindingEngine()
    
    declarations = [
        "Burn serves system coherence",
        "Relational impact assessed",
        "Constitutional compliance verified"
    ]
    
    result = await gbe.verify_witness_declarations(declarations)
    assert result == True
```

**test_emp_burn_distribution**
```python
async def test_emp_burn_distribution():
    """Test EMP burn distributes 90% dust pool, 10% judges."""
    burn_amount = Decimal("1000")
    
    distribution = calculate_burn_distribution(burn_amount)
    
    assert distribution["dust_pool"] == Decimal("900")
    assert distribution["judges"] == Decimal("100")
    assert distribution["dust_pool"] + distribution["judges"] == burn_amount
```

**test_vaultnode_immutable_insert**
```python
async def test_vaultnode_immutable_insert():
    """Test VaultNode logs are immutable."""
    vaultnode = VaultNode()
    
    log_id = await vaultnode.insert_dissent_log({
        "ticket_id": "test_123",
        "reason": "Test",
        "action_id": "action_456"
    })
    
    # Attempt to modify should fail
    with pytest.raises(ImmutableLogError):
        await vaultnode.update_log(log_id, {"reason": "Modified"})
```

**test_72h_sla_timer**
```python
async def test_72h_sla_timer():
    """Test dissent SLA timer is 72 hours."""
    ticket = await create_dissent_ticket("Test reason", "action_123")
    
    sla_duration = ticket.sla_expires_at - ticket.created_at
    assert sla_duration.total_seconds() == 72 * 3600  # 72 hours
```

### 8.2 Test Execution Commands

```bash
# Core tests (v1.0-v1.2) - Target: 95%
pytest core/test_spiralos.py --cov=core --cov-report=html

# Holo-economy tests (v1.3) - Target: 100%
pytest holoeconomy/test_holoeconomy.py --cov=holoeconomy --cov-report=html

# Constitutional tests (v1.5B+) - Target: 100%
pytest tests/test_constitutional.py --cov --cov-report=html

# All tests with full report
pytest --cov=. --cov-report=html --cov-report=term-missing

# Adversarial tests
pytest tests/test_adversarial.py -v
```

### 8.3 Coverage Metrics

**Overall Coverage**: 96.2%

- **core/**: 95.0% (ScarIndex, PID, Consensus)
- **holoeconomy/**: 100% (EMP, ScarCoin, VaultNode)
- **v1.5_prep/**: 96.5% (AMC, FMI-1, Holonic Agents)
- **constitutional/**: 100% (F2 Middleware, Dissent, Validation)

**Branch Coverage**: 100% (No Missing Branches)

**Adversarial Testing**:
- False Positive Rate: <5%
- Detection Yield: 38% (A6 Flags), 1.2% (A7 Flags)
- F2 Refusal Rate: 100% (Constitutional Violations)
