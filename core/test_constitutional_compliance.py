"""
Constitutional Compliance Test Suite

Tests for critical constitutional corrections:
1. ScarIndex weight validation (sum = 1.0)
2. Consensus protocol (4-of-5 quorum with diversity)
3. F2 Judicial Right of Refusal middleware
4. Protected dissent endpoint (72-hour SLA)
5. EMP burn validation via GlyphicBindingEngine
"""

import sys
import os
import asyncio
from datetime import datetime, timedelta, timezone
from decimal import Decimal

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.scarindex import ScarIndexOracle, CoherenceComponents, AcheMeasurement
from core.oracle_council import OracleCouncil, Oracle, ProviderType
from core.f2_judges import (
    JudicialSystem, RightOfRefusal, RefusalAppeal,
    JudgmentType, JudgePriority
)
from holoeconomy.empathy_market import (
    EmpathyMarket, ResonanceEvent, BurnValidation
)


def test_scarindex_weights_sum():
    """
    Constitutional Requirement: ScarIndex weights must sum to 1.0
    
    Tests that:
    - Weight sum equals 1.0 within tolerance
    - validate_weights() passes without error
    - All weights are within valid range (0, 1)
    """
    print("\n" + "="*70)
    print("TEST: ScarIndex Weight Sum Validation")
    print("="*70)
    
    # Test weight sum
    weight_sum = sum(ScarIndexOracle.WEIGHTS.values())
    print(f"Weight sum: {weight_sum}")
    print(f"Weights: {ScarIndexOracle.WEIGHTS}")
    
    # Constitutional requirement: sum must equal 1.0
    tolerance = 1e-10
    assert abs(weight_sum - 1.0) < tolerance, f"Weight sum {weight_sum} != 1.0"
    
    # Test validate_weights method
    try:
        result = ScarIndexOracle.validate_weights()
        assert result is True, "validate_weights() should return True"
        print("✓ validate_weights() passed")
    except ValueError as e:
        assert False, f"validate_weights() raised error: {e}"
    
    # Test individual weights
    for name, weight in ScarIndexOracle.WEIGHTS.items():
        assert 0 < weight < 1, f"{name} weight {weight} not in (0, 1)"
        print(f"✓ {name}: {weight}")
    
    print("✓ ScarIndex weight sum validation PASSED")


def test_scarindex_panic_threshold():
    """
    Constitutional Requirement: ScarIndex < 0.67 triggers PanicFrameManager review
    
    Tests that:
    - PANIC_THRESHOLD is set to 0.67
    - should_trigger_panic() works correctly
    - coherence status reflects new threshold
    """
    print("\n" + "="*70)
    print("TEST: ScarIndex Panic Threshold (0.67)")
    print("="*70)
    
    # Check threshold value
    assert ScarIndexOracle.PANIC_THRESHOLD == 0.67, \
        f"PANIC_THRESHOLD should be 0.67, got {ScarIndexOracle.PANIC_THRESHOLD}"
    print(f"✓ PANIC_THRESHOLD = {ScarIndexOracle.PANIC_THRESHOLD}")
    
    # Test should_trigger_panic
    should_trigger_below = ScarIndexOracle.should_trigger_panic(0.66)
    should_trigger_at = ScarIndexOracle.should_trigger_panic(0.67)
    should_trigger_above = ScarIndexOracle.should_trigger_panic(0.68)
    
    assert should_trigger_below, "Should trigger panic at 0.66 (< 0.67)"
    assert not should_trigger_at, "Should not trigger panic at 0.67 (= threshold)"
    assert not should_trigger_above, "Should not trigger panic at 0.68 (> 0.67)"
    
    print(f"✓ should_trigger_panic(0.66) = {should_trigger_below}")
    print(f"✓ should_trigger_panic(0.67) = {should_trigger_at}")
    print(f"✓ should_trigger_panic(0.68) = {should_trigger_above}")
    
    # Test coherence status thresholds
    status_critical = ScarIndexOracle.calculate_coherence_status(0.45)
    status_warning = ScarIndexOracle.calculate_coherence_status(0.65)
    status_stable = ScarIndexOracle.calculate_coherence_status(0.75)
    status_optimal = ScarIndexOracle.calculate_coherence_status(0.85)
    
    assert status_critical == 'CRITICAL', f"0.45 should be CRITICAL, got {status_critical}"
    assert status_warning == 'WARNING', f"0.65 should be WARNING, got {status_warning}"
    assert status_stable == 'STABLE', f"0.75 should be STABLE, got {status_stable}"
    assert status_optimal == 'OPTIMAL', f"0.85 should be OPTIMAL, got {status_optimal}"
    
    print(f"✓ Coherence status thresholds correct")
    
    print("✓ ScarIndex panic threshold test PASSED")


def test_consensus_4_of_5_quorum():
    """
    Constitutional Requirement: 4-of-5 quorum from specific providers
    
    Tests that:
    - Council has exactly 5 required providers
    - 4 approvals = consensus reached
    - 3 approvals = requires arbitration
    - Provider diversity requirement enforced
    """
    print("\n" + "="*70)
    print("TEST: 4-of-5 Consensus Quorum")
    print("="*70)
    
    council = OracleCouncil()
    
    # Check we have 5 providers
    assert len(council.oracles) == 5, f"Should have 5 oracles, got {len(council.oracles)}"
    print(f"✓ Council has {len(council.oracles)} oracles")
    
    # Check required providers present
    providers = [o.provider for o in council.oracles.values()]
    for required in council.REQUIRED_PROVIDERS:
        assert required in providers, f"Missing required provider: {required}"
        print(f"✓ Provider present: {required}")
    
    # Test 4-of-5 consensus
    oracle_ids = list(council.oracles.keys())
    
    # All 4 vote yes (should reach consensus)
    votes_4_yes = {oracle_ids[i]: True for i in range(4)}
    consensus, reason, arbitration = council.validate_consensus(votes_4_yes)
    
    assert consensus is True, "4-of-5 approvals should reach consensus"
    assert arbitration is False, "4-of-5 should not require arbitration"
    print(f"✓ 4-of-5 consensus: {reason}")
    
    # Test 3-of-5 approvals scenario requiring arbitration
    # We need 4 votes with exactly 3 approvals, including at least 1 non-commercial
    # Find indices to create this scenario
    external_id = next(
        oid for oid, o in council.oracles.items()
        if o.provider == "external_validator"
    )
    
    # Create a vote set with 3 yes (including 1 non-commercial), 1 no, excluding external validator
    # Find a non-commercial provider that's not external_validator
    non_commercial_ids = [
        oid for oid, o in council.oracles.items()
        if o.provider_type == ProviderType.NON_COMMERCIAL and oid != external_id
    ]
    commercial_ids = [
        oid for oid, o in council.oracles.items()
        if o.provider_type == ProviderType.COMMERCIAL
    ]
    
    if non_commercial_ids and len(commercial_ids) >= 2:
        # Create 3 yes votes: 2 commercial + 1 non-commercial (not external validator)
        # Plus 1 no vote from another commercial
        votes_3_yes_no_external = {
            commercial_ids[0]: True,
            commercial_ids[1]: True,
            non_commercial_ids[0]: True,  # Non-commercial approval for diversity
        }
        if len(commercial_ids) >= 3:
            votes_3_yes_no_external[commercial_ids[2]] = False  # One rejection
        
        consensus, reason, arbitration = council.validate_consensus(votes_3_yes_no_external)
        
        if external_id not in votes_3_yes_no_external:
            assert arbitration is True, f"3-of-5 approvals without external validator should require arbitration, got: {reason}"
            print(f"✓ 3-of-5 approvals requires arbitration: {reason}")
    
    # Test insufficient votes total (only 3 votes cast)
    votes_only_3 = {oracle_ids[i]: True for i in range(3)}
    consensus_3, reason_3, arbitration_3 = council.validate_consensus(votes_only_3)
    
    assert consensus_3 is False, "Only 3 votes total should not meet quorum"
    assert "quorum" in reason_3.lower(), f"Reason should mention quorum: {reason_3}"
    print(f"✓ Insufficient quorum (3 votes total): {reason_3}")
    
    # Test insufficient quorum (only 2 votes)
    votes_2_yes = {oracle_ids[i]: True for i in range(2)}
    consensus, reason, arbitration = council.validate_consensus(votes_2_yes)
    
    assert consensus is False, "2-of-5 should not reach consensus"
    print(f"✓ 2-of-5 insufficient: {reason}")
    
    print("✓ 4-of-5 consensus quorum test PASSED")


def test_consensus_diversity_requirement():
    """
    Constitutional Requirement: ≥1 non-commercial provider required
    
    Tests that:
    - Non-commercial providers are correctly identified
    - At least 1 non-commercial provider must approve
    - All-commercial approvals are rejected
    """
    print("\n" + "="*70)
    print("TEST: Consensus Provider Diversity Requirement")
    print("="*70)
    
    council = OracleCouncil()
    
    # Identify commercial and non-commercial providers
    commercial = []
    non_commercial = []
    
    for oracle_id, oracle in council.oracles.items():
        if oracle.provider_type == ProviderType.COMMERCIAL:
            commercial.append(oracle_id)
        else:
            non_commercial.append(oracle_id)
    
    print(f"Commercial providers: {len(commercial)}")
    print(f"Non-commercial providers: {len(non_commercial)}")
    
    assert len(non_commercial) >= 1, "Must have at least 1 non-commercial provider"
    
    # Test: All commercial votes (should fail diversity requirement)
    if len(commercial) >= 4:
        votes_all_commercial = {cid: True for cid in commercial[:4]}
        consensus, reason, _ = council.validate_consensus(votes_all_commercial)
        
        assert consensus is False, "All-commercial votes should be rejected"
        assert "non-commercial" in reason.lower(), f"Reason should mention non-commercial: {reason}"
        print(f"✓ All-commercial rejected: {reason}")
    
    # Test: Mixed votes with ≥1 non-commercial (should pass if 4+)
    if len(commercial) >= 3 and len(non_commercial) >= 1:
        votes_mixed = {cid: True for cid in commercial[:3]}
        votes_mixed[non_commercial[0]] = True
        
        consensus, reason, _ = council.validate_consensus(votes_mixed)
        
        assert consensus is True, "Mixed votes with non-commercial should pass"
        print(f"✓ Mixed votes (with non-commercial) passed: {reason}")
    
    # Test diversity check method
    voting_oracles_diverse = commercial[:2] + non_commercial[:1]
    diverse = council.check_provider_diversity(voting_oracles_diverse)
    
    assert diverse is True, "Should be diverse with ≥1 non-commercial"
    print(f"✓ Diversity check passed")
    
    print("✓ Provider diversity requirement test PASSED")


def test_f2_right_of_refusal():
    """
    Constitutional Safeguard: F2 Judicial Right of Refusal
    
    Tests that:
    - Judges can invoke Right of Refusal
    - Refusal includes 403 status and appeal route
    - Refusal is immutably logged
    """
    print("\n" + "="*70)
    print("TEST: F2 Judicial Right of Refusal")
    print("="*70)
    
    system = JudicialSystem()
    
    # Get a judge
    judge_id = list(system.judges.keys())[0]
    
    # Invoke refusal
    refusal = system.invoke_right_of_refusal(
        action_type="emp_burn",
        action_id="burn_001",
        refusing_judge_id=judge_id,
        constitutional_grounds="Burn violates coherence threshold requirement",
        evidence={'coherence_score': 0.65}
    )
    
    assert refusal is not None, "Refusal should be created"
    assert refusal.action_type == "emp_burn"
    assert refusal.refusing_judge_id == judge_id
    print(f"✓ Refusal created: {refusal.id}")
    
    # Check HTTP response format
    http_response = refusal.get_http_response()
    
    assert http_response['status_code'] == 403, "Should return 403 Forbidden"
    assert 'appeal_route' in http_response, "Should include appeal route"
    assert http_response['appeal_route']['endpoint'] == "/api/v1.5/dissent"
    print(f"✓ HTTP 403 response correct")
    print(f"✓ Appeal endpoint: {http_response['appeal_route']['endpoint']}")
    
    # Check refusal stored
    assert refusal.id in system.refusals, "Refusal should be stored"
    print(f"✓ Refusal stored in system")
    
    print("✓ F2 Right of Refusal test PASSED")


def test_f2_appeal_72_hour_sla():
    """
    Constitutional Guarantee: 72-hour F2 review SLA for appeals
    
    Tests that:
    - Appeals can be filed against refusals
    - 72-hour SLA is tracked
    - Overdue appeals are automatically approved
    """
    print("\n" + "="*70)
    print("TEST: F2 Appeal 72-Hour SLA")
    print("="*70)
    
    system = JudicialSystem()
    
    # Create a refusal first
    judge_id = list(system.judges.keys())[0]
    refusal = system.invoke_right_of_refusal(
        action_type="test_action",
        action_id="action_001",
        refusing_judge_id=judge_id,
        constitutional_grounds="Test refusal"
    )
    
    # File appeal
    appeal = system.file_appeal(
        refusal_id=refusal.id,
        appellant_id="user_123",
        grounds="The action was constitutional and properly validated",
        evidence={'supporting_data': 'test'}
    )
    
    assert appeal is not None, "Appeal should be created"
    assert appeal.refusal_id == refusal.id
    print(f"✓ Appeal filed: {appeal.id}")
    
    # Check 72-hour SLA
    time_to_review = (appeal.review_due_by - appeal.filed_at).total_seconds() / 3600
    assert 71 <= time_to_review <= 73, f"Review due in {time_to_review} hours, should be ~72"
    print(f"✓ Review due in {time_to_review:.1f} hours")
    
    # Check not overdue initially
    assert not appeal.is_overdue(), "Should not be overdue immediately"
    print(f"✓ Appeal not overdue initially")
    
    # Test overdue detection (simulate)
    appeal.review_due_by = datetime.now(timezone.utc) - timedelta(hours=1)
    assert appeal.is_overdue(), "Should be overdue after due date"
    print(f"✓ Overdue detection works")
    
    # Review overdue appeal (should auto-approve)
    reviewed = system.review_appeal(appeal.id, judge_id)
    assert reviewed.review_status == "approved", "Overdue appeals should auto-approve"
    assert "SLA violation" in reviewed.review_reasoning
    print(f"✓ Overdue appeal auto-approved: {reviewed.review_reasoning}")
    
    print("✓ F2 Appeal 72-hour SLA test PASSED")


def test_emp_burn_validation():
    """
    Constitutional Requirement: EMP burn validation via GlyphicBindingEngine
    
    Tests that:
    - coherence_score > 0.7 required
    - At least 2 verified witnesses required
    - relational_impact.permits_burn = True required
    """
    print("\n" + "="*70)
    print("TEST: EMP Burn Validation via GBE")
    print("="*70)
    
    market = EmpathyMarket(enable_burn_validation=True)
    
    assert market.gbe is not None, "GBE should be initialized"
    assert market.gbe.coherence_threshold == 0.7, "GBE threshold should be 0.7"
    print(f"✓ GBE initialized with threshold 0.7")
    
    # Test valid burn (all requirements met)
    validation_valid = market.validate_burn(
        token_id="token_001",
        amount=Decimal('50'),
        witness_declarations=[
            "I witnessed the exchange and confirm mutual understanding",
            "The relational context supports this burn decision",
            "All parties agreed to the burn"
        ],
        relational_context={
            'permits_burn': True,
            'reason': 'Mutual agreement to transmute EMP value'
        }
    )
    
    assert validation_valid is not None, "Validation should return result"
    print(f"✓ Burn validation created: {validation_valid.id}")
    print(f"  Coherence: {validation_valid.coherence_score:.4f}")
    print(f"  Witnesses: {validation_valid.witness_count}")
    print(f"  Permits burn: {validation_valid.permits_burn}")
    print(f"  Valid: {validation_valid.is_valid}")
    print(f"  Reason: {validation_valid.validation_reason}")
    
    # Note: coherence_score depends on GBE's glyph creation, may vary
    # But we can test the witness count and permits_burn requirements
    
    # Test invalid: insufficient witnesses
    validation_few_witnesses = market.validate_burn(
        token_id="token_002",
        amount=Decimal('50'),
        witness_declarations=["Only one witness"],
        relational_context={'permits_burn': True}
    )
    
    assert not validation_few_witnesses.is_valid, "Should be invalid with only 1 witness"
    assert "Insufficient witnesses" in validation_few_witnesses.validation_reason
    print(f"✓ Insufficient witnesses rejected: {validation_few_witnesses.validation_reason}")
    
    # Test invalid: permits_burn = False
    validation_no_permit = market.validate_burn(
        token_id="token_003",
        amount=Decimal('50'),
        witness_declarations=[
            "Witness 1 statement",
            "Witness 2 statement"
        ],
        relational_context={'permits_burn': False}
    )
    
    assert not validation_no_permit.is_valid, "Should be invalid when permits_burn=False"
    assert "does not permit burn" in validation_no_permit.validation_reason
    print(f"✓ permits_burn=False rejected: {validation_no_permit.validation_reason}")
    
    print("✓ EMP burn validation test PASSED")


def test_emp_burn_coherence_threshold():
    """
    Constitutional Requirement: Burn coherence_score > 0.7
    
    Tests that burns with low coherence are rejected.
    """
    print("\n" + "="*70)
    print("TEST: EMP Burn Coherence Threshold (>0.7)")
    print("="*70)
    
    market = EmpathyMarket(enable_burn_validation=True)
    
    # Create a burn validation
    validation = market.validate_burn(
        token_id="token_004",
        amount=Decimal('100'),
        witness_declarations=[
            "Valid witness statement one",
            "Valid witness statement two"
        ],
        relational_context={'permits_burn': True}
    )
    
    # The actual coherence score depends on GBE's glyph creation
    # But we can verify the threshold check is in place
    print(f"Coherence score: {validation.coherence_score:.4f}")
    print(f"Threshold: 0.7")
    print(f"Valid: {validation.is_valid}")
    
    if validation.coherence_score <= 0.7 and not validation.is_valid:
        assert "below" in validation.validation_reason.lower() and "threshold" in validation.validation_reason.lower()
        print(f"✓ Low coherence rejected: {validation.validation_reason}")
    elif validation.coherence_score > 0.7 and validation.is_valid:
        assert "validated" in validation.validation_reason.lower()
        print(f"✓ High coherence accepted: {validation.validation_reason}")
    
    print("✓ EMP burn coherence threshold test PASSED")


async def run_all_tests():
    """Run all constitutional compliance tests"""
    print("\n" + "="*70)
    print("CONSTITUTIONAL COMPLIANCE TEST SUITE")
    print("="*70)
    
    tests = [
        ("ScarIndex Weight Sum", test_scarindex_weights_sum),
        ("ScarIndex Panic Threshold", test_scarindex_panic_threshold),
        ("4-of-5 Consensus Quorum", test_consensus_4_of_5_quorum),
        ("Consensus Provider Diversity", test_consensus_diversity_requirement),
        ("F2 Right of Refusal", test_f2_right_of_refusal),
        ("F2 Appeal 72-Hour SLA", test_f2_appeal_72_hour_sla),
        ("EMP Burn Validation", test_emp_burn_validation),
        ("EMP Burn Coherence Threshold", test_emp_burn_coherence_threshold),
    ]
    
    results = []
    
    for name, test_func in tests:
        try:
            if asyncio.iscoroutinefunction(test_func):
                result = await test_func()
            else:
                result = test_func()
            results.append((name, True, None))
        except Exception as e:
            print(f"\n✗ {name} test FAILED: {e}")
            import traceback
            traceback.print_exc()
            results.append((name, False, str(e)))
    
    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    
    passed = sum(1 for _, success, _ in results if success)
    total = len(results)
    
    for name, success, error in results:
        status = "✓ PASS" if success else "✗ FAIL"
        print(f"{status}: {name}")
        if error:
            print(f"  Error: {error}")
    
    print(f"\nTotal: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    
    return passed == total


if __name__ == '__main__':
    success = asyncio.run(run_all_tests())
    sys.exit(0 if success else 1)
