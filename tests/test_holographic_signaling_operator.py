import asyncio
import hashlib
from datetime import datetime

import pytest

from codex.operators.spiral.holographic_signaling_operator import (
    HolographicSignalingOperator,
    HealthFrame,
    TruthFrame,
    HologramEntry,
    NodeID,
    sign_data,
    verify_signature,
)
from spiralos.core.config import DEFAULT_GLS_REF, LoomParameterMesh, get_current_gls_ref


class TransactionRequest:
    def __init__(self, transaction_id, required_resource_units, payload_size_bytes):
        self.transaction_id = transaction_id
        self.required_resource_units = required_resource_units
        self.payload_size_bytes = payload_size_bytes


class RoutingDecision:
    def __init__(self, next_hop_node_id, estimated_crs, estimated_latency_ms):
        self.next_hop_node_id = next_hop_node_id
        self.estimated_crs = estimated_crs
        self.estimated_latency_ms = estimated_latency_ms


class P2PMessage:
    def __init__(self, sender, receiver, message_type, payload, metadata=None):
        self.sender = sender
        self.receiver = receiver
        self.message_type = message_type
        self.payload = payload
        self.metadata = metadata if metadata is not None else {}


class MessageType:
    HEALTH_FRAME_GOSSIP = "HEALTH_FRAME_GOSSIP"
    TRUTH_FRAME_BROADCAST = "TRUTH_FRAME_BROADCAST"
    REQUEST_HEALTH_FRAME = "REQUEST_HEALTH_FRAME"
    HEALTH_FRAME_RESPONSE = "HEALTH_FRAME_RESPONSE"


# Mock external functions for cryptographic operations

def verify_signature(node_id: str, payload: bytes, signature: str) -> bool:
    expected_sig_prefix = f"mock_sig_of_{hashlib.sha256(payload).hexdigest()}"
    return signature.startswith(expected_sig_prefix)


def sign_data(node_id: str, payload: bytes) -> str:
    return f"mock_sig_of_{hashlib.sha256(payload).hexdigest()}"


MOCK_GLS_REF = DEFAULT_GLS_REF


class MockP2PClient:
    def __init__(self, node_id):
        self.node_id = node_id


class MockScarIndexOracle:
    def __init__(self):
        self.scar_indices = {}

    async def get_individual_scar_index(self, node_id):
        return self.scar_indices.get(node_id, 0)


class MockLoomBurdenManager:
    def __init__(self):
        self.current_epoch = 0

    def get_current_epoch(self):
        return self.current_epoch

    async def get_node_resource_metrics(self, node_id):
        return None


class MockEpochManager:
    def __init__(self):
        self.epoch = 0

    def get_current_epoch(self):
        return self.epoch

    def advance_epoch(self):
        self.epoch += 1


class MockVaultNodeRegistry:
    def __init__(self):
        self.nodes = {}


class MockWitnessClient:
    def __init__(self):
        self.events = []


@pytest.fixture
def setup_operator():
    node_id = NodeID("test_node")
    p2p_client = MockP2PClient(node_id)
    scar_index_oracle = MockScarIndexOracle()
    loom_burden_manager = MockLoomBurdenManager()
    epoch_manager = MockEpochManager()
    vault_node_registry = MockVaultNodeRegistry()
    witness_client = MockWitnessClient()
    loom_params = LoomParameterMesh()

    operator = HolographicSignalingOperator(
        node_id=node_id,
        p2p_client=p2p_client,
        scar_index_oracle=scar_index_oracle,
        loom_burden_manager=loom_burden_manager,
        epoch_manager=epoch_manager,
        vault_node_registry=vault_node_registry,
        witness_client=witness_client,
        loom_params=loom_params,
    )

    return operator, p2p_client, scar_index_oracle, loom_burden_manager, epoch_manager


def test_reject_negative_latency(setup_operator):
    operator, _, _, _, epoch_manager = setup_operator

    bad_hf = HealthFrame(
        node_id=NodeID("bad_node"),
        epoch=epoch_manager.get_current_epoch(),
        scar_index=5,
        load_percent=0.2,
        headroom_ru=5000,
        latency_ms=-50,
        lbi2_crs=0.0,
        gls_ref=MOCK_GLS_REF,
    )
    bad_hf.signature = sign_data(bad_hf.node_id, bad_hf.get_signed_payload())

    initial_hologram_size = len(operator.local_hologram)
    asyncio.run(operator.update_local_hologram([bad_hf]))

    assert len(operator.local_hologram) == initial_hologram_size
    assert NodeID("bad_node") not in operator.local_hologram

    existing_node_id = NodeID("node_2")
    operator.local_hologram[existing_node_id] = HologramEntry(
        HealthFrame(
            node_id=existing_node_id,
            epoch=epoch_manager.get_current_epoch() - 1,
            scar_index=5,
            load_percent=0.2,
            headroom_ru=5000,
            latency_ms=50,
            lbi2_crs=100.0,
            gls_ref=MOCK_GLS_REF,
            signature="dummy_sig",
        )
    )
    initial_trust = operator.local_hologram[existing_node_id].trust_score

    bad_hf_for_existing_node = HealthFrame(
        node_id=existing_node_id,
        epoch=epoch_manager.get_current_epoch(),
        scar_index=10,
        load_percent=0.2,
        headroom_ru=5000,
        latency_ms=-50,
        lbi2_crs=0.0,
        gls_ref=MOCK_GLS_REF,
    )
    bad_hf_for_existing_node.signature = sign_data(
        bad_hf_for_existing_node.node_id, bad_hf_for_existing_node.get_signed_payload()
    )

    asyncio.run(operator.update_local_hologram([bad_hf_for_existing_node]))
    assert existing_node_id in operator.local_hologram
    assert operator.local_hologram[existing_node_id].trust_score < initial_trust
    assert operator.local_hologram[existing_node_id].last_seen_frame.latency_ms != -50


def test_replay_attack_guard(setup_operator):
    operator, _, _, _, epoch_manager = setup_operator

    current_epoch = epoch_manager.get_current_epoch()

    hf1 = HealthFrame(
        node_id=NodeID("test_node_2"),
        epoch=current_epoch,
        scar_index=5,
        load_percent=0.2,
        headroom_ru=5000,
        latency_ms=50,
        lbi2_crs=0.0,
        gls_ref=MOCK_GLS_REF,
    )
    hf1.signature = sign_data(hf1.node_id, hf1.get_signed_payload())

    asyncio.run(operator.update_local_hologram([hf1]))
    assert NodeID("test_node_2") in operator.local_hologram
    initial_received_at = operator.local_hologram[NodeID("test_node_2")].received_at

    asyncio.run(asyncio.sleep(0.01))
    asyncio.run(operator.update_local_hologram([hf1]))

    assert operator.local_hologram[NodeID("test_node_2")].received_at == initial_received_at
    assert operator.local_hologram[NodeID("test_node_2")].trust_score == HologramEntry(hf1).trust_score

    epoch_manager.advance_epoch()
    hf1_new_epoch = HealthFrame(
        node_id=NodeID("test_node_2"),
        epoch=epoch_manager.get_current_epoch(),
        scar_index=5,
        load_percent=0.2,
        headroom_ru=5000,
        latency_ms=50,
        lbi2_crs=0.0,
        gls_ref=MOCK_GLS_REF,
    )
    hf1_new_epoch.signature = sign_data(hf1_new_epoch.node_id, hf1_new_epoch.get_signed_payload())

    asyncio.run(asyncio.sleep(0.01))
    asyncio.run(operator.update_local_hologram([hf1_new_epoch]))

    assert operator.local_hologram[NodeID("test_node_2")].received_at > initial_received_at
    assert operator.local_hologram[NodeID("test_node_2")].last_seen_frame.epoch == epoch_manager.get_current_epoch()


def test_load_percent_penalty(setup_operator):
    operator, _, _, _, epoch_manager = setup_operator

    hf_overloaded = HealthFrame(
        node_id=NodeID("overloaded_node"),
        epoch=epoch_manager.get_current_epoch(),
        scar_index=5,
        load_percent=1.2,
        headroom_ru=1000,
        latency_ms=10,
        lbi2_crs=0.0,
        gls_ref=MOCK_GLS_REF,
    )
    hf_overloaded.signature = sign_data(hf_overloaded.node_id, hf_overloaded.get_signed_payload())

    initial_hologram_size = len(operator.local_hologram)
    asyncio.run(operator.update_local_hologram([hf_overloaded]))

    assert NodeID("overloaded_node") in operator.local_hologram
    assert operator.local_hologram[NodeID("overloaded_node")].trust_score < HologramEntry(hf_overloaded).trust_score


def test_reject_mismatched_gls_ref(setup_operator):
    operator, _, _, _, epoch_manager = setup_operator

    bad_gls_hf = HealthFrame(
        node_id=NodeID("mismatched_gls_node"),
        epoch=epoch_manager.get_current_epoch(),
        scar_index=5,
        load_percent=0.2,
        headroom_ru=5000,
        latency_ms=50,
        lbi2_crs=0.0,
        gls_ref="wrong_ref",
    )
    bad_gls_hf.signature = sign_data(bad_gls_hf.node_id, bad_gls_hf.get_signed_payload())

    initial_hologram_size = len(operator.local_hologram)
    asyncio.run(operator.update_local_hologram([bad_gls_hf]))

    assert len(operator.local_hologram) == initial_hologram_size
    assert NodeID("mismatched_gls_node") not in operator.local_hologram


# --- ΔΩ.LBI.3 Tests ---


def test_healing_node_gets_crs_boost(setup_operator):
    operator, _, scar_index_oracle, _, epoch_manager = setup_operator
    healing_node_id = NodeID("healing_node")
    initial_scar_index = 30

    hf_initial = HealthFrame(
        node_id=healing_node_id,
        epoch=epoch_manager.get_current_epoch(),
        scar_index=initial_scar_index,
        load_percent=0.5,
        headroom_ru=5000,
        latency_ms=50,
        lbi2_crs=100.0,
        gls_ref=MOCK_GLS_REF,
    )
    hf_initial.signature = sign_data(healing_node_id, hf_initial.get_signed_payload())
    asyncio.run(operator.update_local_hologram([hf_initial]))

    scar_index_oracle.scar_indices[healing_node_id] = initial_scar_index

    entry = operator.local_hologram[healing_node_id]
    assert entry.metabolic_factor == 1.0
    assert entry.last_epoch_scar_index == initial_scar_index

    for i in range(1, 4):
        epoch_manager.advance_epoch()
        current_epoch = epoch_manager.get_current_epoch()

        scar_index_oracle.scar_indices[healing_node_id] = max(0, initial_scar_index - (i * 5))

        tf = TruthFrame(
            health_frame=HealthFrame(
                node_id=healing_node_id,
                epoch=current_epoch,
                scar_index=scar_index_oracle.scar_indices[healing_node_id],
                load_percent=0.5,
                headroom_ru=5000,
                latency_ms=50,
                lbi2_crs=100.0,
                gls_ref=MOCK_GLS_REF,
                signature="dummy_sig",
            ),
            witness_multisig=["sig1"],
            witness_epoch=current_epoch,
        )
        asyncio.run(operator.ingest_truth_frame(tf))

        asyncio.run(operator.on_epoch_tick(current_epoch))

        assert entry.metabolic_factor > 1.0
        assert entry.metabolic_factor <= operator.M_MAX
        assert entry.truthframes_this_epoch == 0
        assert entry.violations_this_epoch == 0

    assert entry.metabolic_factor > 1.0
    assert (entry.cached_crs * entry.metabolic_factor) > entry.cached_crs


def test_rotten_node_gets_suppressed(setup_operator):
    operator, _, scar_index_oracle, _, epoch_manager = setup_operator
    rotten_node_id = NodeID("rotten_node")
    initial_scar_index = 10

    hf_initial = HealthFrame(
        node_id=rotten_node_id,
        epoch=epoch_manager.get_current_epoch(),
        scar_index=initial_scar_index,
        load_percent=0.5,
        headroom_ru=5000,
        latency_ms=50,
        lbi2_crs=100.0,
        gls_ref=MOCK_GLS_REF,
    )
    hf_initial.signature = sign_data(rotten_node_id, hf_initial.get_signed_payload())
    asyncio.run(operator.update_local_hologram([hf_initial]))

    scar_index_oracle.scar_indices[rotten_node_id] = initial_scar_index
    entry = operator.local_hologram[rotten_node_id]

    for i in range(1, 4):
        epoch_manager.advance_epoch()
        current_epoch = epoch_manager.get_current_epoch()

        scar_index_oracle.scar_indices[rotten_node_id] = min(100, initial_scar_index + (i * 10))
        asyncio.run(operator.report_node_violation(rotten_node_id, "LBI.1_breach", 1))

        asyncio.run(operator.on_epoch_tick(current_epoch))

        assert entry.metabolic_factor < 1.0
        assert entry.metabolic_factor >= operator.M_MIN

    assert entry.metabolic_factor < 1.0
    assert (entry.cached_crs * entry.metabolic_factor) < entry.cached_crs


def test_idle_node_slow_decay(setup_operator):
    operator, _, scar_index_oracle, _, epoch_manager = setup_operator
    idle_node_id = NodeID("idle_node")
    initial_scar_index = 5

    hf_initial = HealthFrame(
        node_id=idle_node_id,
        epoch=epoch_manager.get_current_epoch(),
        scar_index=initial_scar_index,
        load_percent=0.1,
        headroom_ru=8000,
        latency_ms=30,
        lbi2_crs=200.0,
        gls_ref=MOCK_GLS_REF,
    )
    hf_initial.signature = sign_data(idle_node_id, hf_initial.get_signed_payload())
    asyncio.run(operator.update_local_hologram([hf_initial]))

    scar_index_oracle.scar_indices[idle_node_id] = initial_scar_index
    entry = operator.local_hologram[idle_node_id]
    initial_metabolic_factor = entry.metabolic_factor

    for _ in range(1, 5):
        epoch_manager.advance_epoch()
        current_epoch = epoch_manager.get_current_epoch()
        scar_index_oracle.scar_indices[idle_node_id] = initial_scar_index

        asyncio.run(operator.on_epoch_tick(current_epoch))

        assert entry.metabolic_factor == initial_metabolic_factor


def test_metabolism_does_not_touch_scarindex(setup_operator):
    operator, _, scar_index_oracle, _, epoch_manager = setup_operator
    node_id = NodeID("test_node_3")
    initial_scar_index = 25

    hf_initial = HealthFrame(
        node_id=node_id,
        epoch=epoch_manager.get_current_epoch(),
        scar_index=initial_scar_index,
        load_percent=0.5,
        headroom_ru=5000,
        latency_ms=50,
        lbi2_crs=100.0,
        gls_ref=MOCK_GLS_REF,
    )
    hf_initial.signature = sign_data(node_id, hf_initial.get_signed_payload())
    asyncio.run(operator.update_local_hologram([hf_initial]))
    scar_index_oracle.scar_indices[node_id] = initial_scar_index

    epoch_manager.advance_epoch()
    current_epoch = epoch_manager.get_current_epoch()
    scar_index_oracle.scar_indices[node_id] = 20
    tf = TruthFrame(health_frame=hf_initial, witness_multisig=["sig"], witness_epoch=current_epoch)
    asyncio.run(operator.ingest_truth_frame(tf))
    asyncio.run(operator.on_epoch_tick(current_epoch))

    assert scar_index_oracle.scar_indices[node_id] == 20


def test_metabolic_factor_bounds(setup_operator):
    operator, _, scar_index_oracle, _, epoch_manager = setup_operator
    node_id = NodeID("bounded_node")
    initial_scar_index = 50

    hf_initial = HealthFrame(
        node_id=node_id,
        epoch=epoch_manager.get_current_epoch(),
        scar_index=initial_scar_index,
        load_percent=0.5,
        headroom_ru=5000,
        latency_ms=50,
        lbi2_crs=100.0,
        gls_ref=MOCK_GLS_REF,
    )
    hf_initial.signature = sign_data(node_id, hf_initial.get_signed_payload())
    asyncio.run(operator.update_local_hologram([hf_initial]))
    scar_index_oracle.scar_indices[node_id] = initial_scar_index
    entry = operator.local_hologram[node_id]

    epoch_manager.advance_epoch()
    current_epoch = epoch_manager.get_current_epoch()
    scar_index_oracle.scar_indices[node_id] = 0
    for _ in range(10):
        tf = TruthFrame(health_frame=hf_initial, witness_multisig=["sig"], witness_epoch=current_epoch)
        asyncio.run(operator.ingest_truth_frame(tf))
    asyncio.run(operator.on_epoch_tick(current_epoch))
    assert entry.metabolic_factor == operator.M_MAX

    epoch_manager.advance_epoch()
    current_epoch = epoch_manager.get_current_epoch()
    scar_index_oracle.scar_indices[node_id] = 100
    for _ in range(10):
        asyncio.run(operator.report_node_violation(node_id, "Fraud", 1))
    asyncio.run(operator.on_epoch_tick(current_epoch))
    assert entry.metabolic_factor == operator.M_MIN


def test_metabolic_parameters_respect_loom_mesh():
    node_id = NodeID("custom_mesh_node")

    custom_loom_params = LoomParameterMesh(lbi3_beta=0.5, lbi3_w_heal=10.0)

    p2p_client = MockP2PClient(node_id)
    scar_index_oracle = MockScarIndexOracle()
    loom_burden_manager = MockLoomBurdenManager()
    epoch_manager = MockEpochManager()
    vault_node_registry = MockVaultNodeRegistry()
    witness_client = MockWitnessClient()

    operator_custom = HolographicSignalingOperator(
        node_id=node_id,
        p2p_client=p2p_client,
        scar_index_oracle=scar_index_oracle,
        loom_burden_manager=loom_burden_manager,
        epoch_manager=epoch_manager,
        vault_node_registry=vault_node_registry,
        witness_client=witness_client,
        loom_params=custom_loom_params,
    )

    hf_initial = HealthFrame(
        node_id=node_id,
        epoch=epoch_manager.get_current_epoch(),
        scar_index=30,
        load_percent=0.5,
        headroom_ru=5000,
        latency_ms=50,
        lbi2_crs=100.0,
        gls_ref=MOCK_GLS_REF,
    )
    hf_initial.signature = sign_data(node_id, hf_initial.get_signed_payload())

    asyncio.run(operator_custom.update_local_hologram([hf_initial]))
    scar_index_oracle.scar_indices[node_id] = 20

    epoch_manager.advance_epoch()
    current_epoch = epoch_manager.get_current_epoch()
    asyncio.run(operator_custom.on_epoch_tick(current_epoch))

    entry = operator_custom.local_hologram[node_id]
    assert entry.metabolic_factor == operator_custom.M_MAX
    assert operator_custom.BETA == pytest.approx(0.5)
    assert operator_custom.W_HEAL == pytest.approx(10.0)
