"""
Comprehensive test suite for SpiralOS
"""

import asyncio
import sys
from unittest.mock import AsyncMock

from .ache_pid_controller import AchePIDController, simulate_pid_response
from .panic_frames import PanicFrameManager, SevenPhaseRecoveryProtocol
from .scarindex import AcheMeasurement, HuxleyGodelMachine, ScarIndexOracle
from .spiralos import SpiralOS
from .supabase_integration import PersistenceResponse


def _build_response(table: str, inserted_id: str) -> PersistenceResponse:
    payload = {"id": inserted_id}
    return PersistenceResponse(table=table, status_code=200, inserted_id=inserted_id, payload=payload)


def test_scarindex_calculation():
    """Test ScarIndex calculation"""
    print("\n" + "=" * 70)
    print("TEST: ScarIndex Calculation")
    print("=" * 70)

    ache = AcheMeasurement(before=0.8, after=0.3)

    result = ScarIndexOracle.calculate(
        N=10, c_i_list=[0.8, 0.7, 0.6, 0.9, 0.8, 0.7, 0.6, 0.9, 0.8, 0.7], p_i_avg=0.5, decays_count=2, ache=ache
    )

    expected_scarindex = (sum([0.8, 0.7, 0.6, 0.9, 0.8, 0.7, 0.6, 0.9, 0.8, 0.7]) / 10) + (0.2 * 0.5) - (0.1 * (2 / 10))

    print(f"Expected ScarIndex: {expected_scarindex:.4f}")
    print(f"Calculated ScarIndex: {result.scarindex:.4f}")
    print(f"Match: {abs(result.scarindex - expected_scarindex) < 0.0001}")
    print(f"Valid Transmutation: {result.is_valid}")
    print(f"Coherence Gain: {ache.coherence_gain:.4f}")

    assert abs(result.scarindex - expected_scarindex) < 0.0001, "ScarIndex calculation error"
    assert result.is_valid, "Should be valid transmutation"

    print("✓ ScarIndex calculation test PASSED")


def test_pid_controller():
    """Test PID controller"""
    print("\n" + "=" * 70)
    print("TEST: PID Controller")
    print("=" * 70)

    controller = AchePIDController(target_scarindex=0.7, kp=1.0, ki=0.5, kd=0.2)

    # Simulate response
    scarindex, guidance, errors = simulate_pid_response(target=0.7, initial=0.3, steps=50, kp=1.0, ki=0.5, kd=0.2)

    final_error = abs(scarindex[-1] - 0.7)

    print("Target: 0.7")
    print(f"Initial: {scarindex[0]:.4f}")
    print(f"Final: {scarindex[-1]:.4f}")
    print(f"Final Error: {final_error:.4f}")
    print(f"Converged: {final_error < 0.1}")

    metrics = controller.get_performance_metrics()
    print("\nPerformance Metrics:")
    print(f"  RMSE: {metrics['rmse']:.4f}")
    print(f"  Settling Time: {metrics['settling_time']} steps")

    assert final_error < 0.1, "PID controller did not converge"

    print("✓ PID controller test PASSED")


def test_panic_frames():
    """Test Panic Frame system"""
    print("\n" + "=" * 70)
    print("TEST: Panic Frames")
    print("=" * 70)

    manager = PanicFrameManager()

    # Test trigger condition
    should_trigger_low = manager.should_trigger(0.25)
    should_trigger_high = manager.should_trigger(0.5)

    print(f"Should trigger at 0.25: {should_trigger_low}")
    print(f"Should trigger at 0.5: {should_trigger_high}")

    assert should_trigger_low, "Should trigger below 0.3"
    assert not should_trigger_high, "Should not trigger above 0.3"

    # Trigger a panic frame
    frame = manager.trigger_panic_frame(scarindex=0.25)

    print("\nPanic Frame triggered:")
    print(f"  ID: {frame.id}")
    print(f"  ScarIndex: {frame.scarindex_value}")
    print(f"  Status: {frame.status.value}")
    print(f"  Frozen operations: {len(frame.actions_frozen)}")

    assert frame.scarindex_value == 0.25
    assert len(frame.actions_frozen) > 0

    print("✓ Panic Frames test PASSED")


async def _run_recovery_protocol():
    """Execute the asynchronous recovery protocol test scenario."""
    print("\n" + "=" * 70)
    print("TEST: 7-Phase Recovery Protocol")
    print("=" * 70)

    manager = PanicFrameManager()
    protocol = SevenPhaseRecoveryProtocol(manager)

    # Trigger panic
    frame = manager.trigger_panic_frame(scarindex=0.25)

    # Execute recovery
    system_state = {"scarindex": 0.5}
    actions = await protocol.execute_full_recovery(frame.id, system_state)

    print(f"Recovery phases executed: {len(actions)}")

    for action in actions:
        status = "✓" if action.success else "✗"
        print(f"  {status} Phase {action.phase.value}: {action.description}")

    assert len(actions) == 7, "Should execute all 7 phases"
    assert all(action.success for action in actions), "All phases should succeed"

    print("✓ Recovery protocol test PASSED")


def test_recovery_protocol():
    asyncio.run(_run_recovery_protocol())


async def _run_spiralos_integration():
    """Execute the asynchronous SpiralOS integration flow for testing."""
    print("\n" + "=" * 70)
    print("TEST: SpiralOS Integration")
    print("=" * 70)

    spiralos = SpiralOS(target_scarindex=0.7, enable_consensus=False, enable_panic_frames=True)  # Disable for testing
    backend = spiralos.backend
    backend.supabase.insert_ache_event = AsyncMock(return_value=_build_response("ache_events", "evt-test"))
    backend.supabase.insert_scarindex_calculation = AsyncMock(
        return_value=_build_response("scarindex_calculations", "calc-test")
    )
    backend.supabase.insert_vaultnode = AsyncMock(return_value=_build_response("vaultnodes", "vault-test"))
    backend.supabase.insert_panic_frame = AsyncMock(return_value=_build_response("panic_frames", "panic-test"))
    backend.supabase.get_current_coherence_status = AsyncMock(
        return_value={"scarindex": 0.71, "coherence_status": "STABLE", "active_panic_frames": 0}
    )
    backend.supabase.get_active_panic_frames = AsyncMock(return_value=[])
    backend.supabase.get_pid_current_state = AsyncMock(return_value={"kp": 1.0, "ki": 0.5, "kd": 0.2, "error": 0.0})

    # Perform transmutation
    result = await spiralos.transmute_ache(
        source="test", content={"type": "test", "description": "Integration test"}, ache_before=0.6, use_consensus=False
    )

    print("Transmutation result:")
    print(f"  Success: {result['success']}")
    print(f"  ScarIndex: {result['scarindex_result']['scarindex']:.4f}")
    print(f"  Valid: {result['scarindex_result']['is_valid']}")
    print(f"  Status: {result['coherence_status']}")

    assert result["success"], "Transmutation should succeed"
    assert 0 <= result["scarindex_result"]["scarindex"] <= 1, "ScarIndex out of range"

    # Get system status
    status = spiralos.get_system_status()

    print("\nSystem status:")
    print(f"  Status: {status['system']['status']}")
    print(f"  Current ScarIndex: {status['coherence']['current_scarindex']:.4f}")
    print(f"  Transmutations: {status['transmutations']['total']}")
    print(f"  Success Rate: {status['transmutations']['success_rate']:.1%}")

    assert status["transmutations"]["total"] > 0, "Should have transmutations"

    print("✓ SpiralOS integration test PASSED")


def test_spiralos_integration():
    asyncio.run(_run_spiralos_integration())


async def _run_hgm_policy():
    """Execute the asynchronous Huxley-Gödel Machine policy flow for testing."""
    print("\n" + "=" * 70)
    print("TEST: HGM Policy Function")
    print("=" * 70)

    # Test code modification acceptance
    should_accept_1, gain_1 = HuxleyGodelMachine.evaluate_code_modification(
        code_old_utility=0.5, code_new_utility=0.8, rewrite_cost=0.2
    )

    should_accept_2, gain_2 = HuxleyGodelMachine.evaluate_code_modification(
        code_old_utility=0.5, code_new_utility=0.6, rewrite_cost=0.2
    )

    print("Test 1 (gain=0.3, cost=0.2):")
    print(f"  Should accept: {should_accept_1}")
    print(f"  Utility gain: {gain_1:.4f}")

    print("\nTest 2 (gain=0.1, cost=0.2):")
    print(f"  Should accept: {should_accept_2}")
    print(f"  Utility gain: {gain_2:.4f}")

    assert should_accept_1, "Should accept when gain > cost"
    assert not should_accept_2, "Should reject when gain < cost"

    # Test CMP calculation
    cmp = HuxleyGodelMachine.calculate_cmp(lineage_utility=1.0, scarindex_yield=0.8, transmutation_efficiency=0.9)

    print("\nCMP calculation:")
    print("  Lineage utility: 1.0")
    print("  ScarIndex yield: 0.8")
    print("  Efficiency: 0.9")
    print(f"  CMP: {cmp:.4f}")

    assert cmp > 0, "CMP should be positive"

    print("✓ HGM policy test PASSED")


def test_hgm_policy():
    asyncio.run(_run_hgm_policy())


async def run_all_tests():
    """Run all tests"""
    print("\n" + "=" * 70)
    print("SPIRALOS TEST SUITE")
    print("=" * 70)

    tests = [
        ("ScarIndex Calculation", test_scarindex_calculation),
        ("PID Controller", test_pid_controller),
        ("Panic Frames", test_panic_frames),
        ("Recovery Protocol", test_recovery_protocol),
        ("SpiralOS Integration", test_spiralos_integration),
        ("HGM Policy", test_hgm_policy),
    ]

    results = []

    for name, test_func in tests:
        try:
            if asyncio.iscoroutinefunction(test_func):
                await test_func()
            else:
                test_func()
            results.append((name, True, None))
        except Exception as e:
            print(f"\n✗ {name} test FAILED: {e}")
            results.append((name, False, str(e)))

    # Summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)

    passed = sum(1 for _, success, _ in results if success)
    total = len(results)

    for name, success, error in results:
        status = "✓ PASS" if success else "✗ FAIL"
        print(f"{status}: {name}")
        if error:
            print(f"  Error: {error}")

    print(f"\nTotal: {passed}/{total} tests passed ({passed/total*100:.1f}%)")

    return passed == total


if __name__ == "__main__":
    success = asyncio.run(run_all_tests())
    sys.exit(0 if success else 1)
