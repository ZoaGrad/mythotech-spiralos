"""
Holographic Signaling Operator implementing ΔΩ.LBI.2 with ΔΩ.LBI.3 metabolic overlay.
Self-contained version for testing with mocked dependencies.
"""
from __future__ import annotations

import asyncio
import hashlib
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Optional, Set

from spiralos.core.config import LoomParameterMesh, get_current_gls_ref


class NodeID(str):
    """Simple NodeID wrapper used for hologram keys."""

    def __new__(cls, value: str):
        return str.__new__(cls, value)


@dataclass
class HealthFrame:
    node_id: NodeID
    epoch: int
    scar_index: int
    load_percent: float
    headroom_ru: int
    latency_ms: int
    lbi2_crs: float
    gls_ref: str
    signature: str = ""

    def get_signed_payload(self) -> bytes:
        payload = f"{self.node_id}:{self.epoch}:{self.scar_index}:{self.load_percent}:{self.headroom_ru}:{self.latency_ms}:{self.lbi2_crs}:{self.gls_ref}"
        return payload.encode()


@dataclass
class TruthFrame:
    health_frame: HealthFrame
    witness_multisig: List[str]
    witness_epoch: int


class HologramEntry:
    def __init__(self, frame: HealthFrame):
        self.node_id = frame.node_id
        self.last_seen_frame: HealthFrame = frame
        self.received_at: datetime = datetime.now()
        self.trust_score: float = 1.0
        self.cached_crs = frame.lbi2_crs
        self.cached_scar_index = frame.scar_index
        self.cached_load_percent = frame.load_percent
        # ΔΩ.LBI.3 Metabolic Fields
        self.last_epoch: Optional[int] = None
        self.last_epoch_scar_index: Optional[int] = None
        self.truthframes_this_epoch: int = 0
        self.violations_this_epoch: int = 0
        self.ache_score: float = 0.0
        self.metabolic_factor: float = 1.0


def sign_data(node_id: NodeID, payload: bytes) -> str:
    return f"mock_sig_of_{hashlib.sha256(payload).hexdigest()}"


def verify_signature(node_id: NodeID, payload: bytes, signature: str) -> bool:
    expected = f"mock_sig_of_{hashlib.sha256(payload).hexdigest()}"
    return signature.startswith(expected)


class HolographicSignalingOperator:
    def __init__(
        self,
        node_id: NodeID,
        p2p_client,
        scar_index_oracle,
        loom_burden_manager,
        epoch_manager,
        vault_node_registry,
        witness_client,
        loom_params: LoomParameterMesh,
    ):
        self.node_id = node_id
        self.p2p_client = p2p_client
        self.scar_index_oracle = scar_index_oracle
        self.loom_burden_manager = loom_burden_manager
        self.epoch_manager = epoch_manager
        self.vault_node_registry = vault_node_registry
        self.witness_client = witness_client
        self.loom_params = loom_params

        self.local_hologram: Dict[NodeID, HologramEntry] = {}
        self.peer_list: List[NodeID] = []
        self._processed_signatures_per_epoch: Dict[int, Set[str]] = {}
        self._last_epoch_processed_for_metabolism: int = -1

        self.MIN_TRUST_THRESHOLD = 0.2
        self.ALPHA = 2.5
        self.latency_weight = getattr(self.loom_params, "latency_weight", 0.2)
        # ΔΩ.LBI.3 metabolic parameters (governed via LoomParameterMesh)
        self.W_HEAL = getattr(self.loom_params, "lbi3_w_heal", 0.5)
        self.W_TRUTH = getattr(self.loom_params, "lbi3_w_truth", 0.2)
        self.W_ROT = getattr(self.loom_params, "lbi3_w_rot", 1.0)
        self.BETA = getattr(self.loom_params, "lbi3_beta", 0.05)
        self.M_MIN = getattr(self.loom_params, "lbi3_m_min", 0.5)
        self.M_MAX = getattr(self.loom_params, "lbi3_m_max", 1.5)

    # --- Core update utilities ---
    async def update_local_hologram(self, frames: List[HealthFrame | TruthFrame]):
        for frame in frames:
            is_truth_frame = isinstance(frame, TruthFrame)
            hf_to_process = frame if isinstance(frame, HealthFrame) else frame.health_frame
            node_id = hf_to_process.node_id

            # Signature validation
            if hf_to_process.signature and not verify_signature(node_id, hf_to_process.get_signed_payload(), hf_to_process.signature):
                continue

            current_epoch = self.epoch_manager.get_current_epoch()
            if hf_to_process.epoch > current_epoch:
                continue

            if hf_to_process.epoch == current_epoch:
                processed = self._processed_signatures_per_epoch.setdefault(current_epoch, set())
                if hf_to_process.signature in processed:
                    continue
                processed.add(hf_to_process.signature)

            if hf_to_process.gls_ref != get_current_gls_ref():
                continue

            if hf_to_process.latency_ms < 0:
                if node_id in self.local_hologram:
                    self.local_hologram[node_id].trust_score *= 0.8
                continue

            entry = self.local_hologram.get(node_id)
            if entry is None:
                entry = HologramEntry(hf_to_process)
                entry.last_epoch = current_epoch
                entry.last_epoch_scar_index = hf_to_process.scar_index
                self.local_hologram[node_id] = entry
            else:
                if is_truth_frame or hf_to_process.epoch > entry.last_seen_frame.epoch:
                    entry.last_seen_frame = hf_to_process
                    entry.received_at = datetime.now()

            if hf_to_process.load_percent > 1.0:
                entry.trust_score *= 0.8

            if is_truth_frame:
                entry.truthframes_this_epoch += 1

            entry.cached_crs = hf_to_process.lbi2_crs
            entry.cached_scar_index = hf_to_process.scar_index
            entry.cached_load_percent = hf_to_process.load_percent

    # --- Truth ingestion ---
    async def ingest_truth_frame(self, truth: TruthFrame):
        node_id = truth.health_frame.node_id
        if node_id not in self.local_hologram:
            self.local_hologram[node_id] = HologramEntry(truth.health_frame)
        entry = self.local_hologram[node_id]
        entry.last_seen_frame = truth.health_frame
        entry.received_at = datetime.now()
        entry.trust_score = 1.0
        entry.cached_crs = truth.health_frame.lbi2_crs
        entry.cached_scar_index = truth.health_frame.scar_index
        entry.cached_load_percent = truth.health_frame.load_percent
        entry.truthframes_this_epoch += 1

    # --- Violation reporting ---
    async def report_node_violation(self, node_id: NodeID, violation_type: str, severity: int):
        if node_id in self.local_hologram:
            entry = self.local_hologram[node_id]
            entry.violations_this_epoch += 1

    # --- Metabolism ---
    async def on_epoch_tick(self, current_epoch: int) -> None:
        if current_epoch <= self._last_epoch_processed_for_metabolism:
            return

        self._processed_signatures_per_epoch.pop(current_epoch - 1, None)
        self._processed_signatures_per_epoch.setdefault(current_epoch, set())

        for node_id, entry in self.local_hologram.items():
            current_si = await self.scar_index_oracle.get_individual_scar_index(node_id)

            if entry.last_epoch_scar_index is None or entry.last_epoch is None or entry.last_epoch < current_epoch - 1:
                entry.last_epoch_scar_index = current_si
                entry.last_epoch = current_epoch
                entry.ache_score = 0.0
                entry.metabolic_factor = 1.0
                entry.truthframes_this_epoch = 0
                entry.violations_this_epoch = 0
                continue

            delta_si = current_si - entry.last_epoch_scar_index
            heal_term = max(0, -delta_si) * self.W_HEAL
            truth_term = entry.truthframes_this_epoch * self.W_TRUTH
            rot_term = (max(0, delta_si) + entry.violations_this_epoch) * self.W_ROT
            ache = heal_term + truth_term - rot_term

            metabolic_factor = 1.0 + self.BETA * ache
            entry.metabolic_factor = max(self.M_MIN, min(self.M_MAX, metabolic_factor))
            entry.ache_score = ache
            entry.last_epoch_scar_index = current_si
            entry.last_epoch = current_epoch
            entry.truthframes_this_epoch = 0
            entry.violations_this_epoch = 0

        self._last_epoch_processed_for_metabolism = current_epoch

    # --- Routing ---
    async def select_next_hop(self, tx_request) -> Optional[NodeID]:
        eligible = []
        for node_id, entry in self.local_hologram.items():
            effective_crs = entry.cached_crs * entry.metabolic_factor
            if entry.trust_score > self.MIN_TRUST_THRESHOLD and effective_crs > 0 and entry.last_seen_frame.headroom_ru >= tx_request.required_resource_units:
                eligible.append((node_id, entry, effective_crs))

        if not eligible:
            return None

        eligible.sort(key=lambda x: x[2], reverse=True)
        if len(eligible) > 1 and abs(eligible[0][2] - eligible[1][2]) < 1e-6:
            eligible.sort(key=lambda x: (-x[2], x[1].cached_scar_index, x[1].cached_load_percent, -1.0))

        return eligible[0][0]

    # --- Background operations (stubs) ---
    async def _gossip_health_frame(self, frame: HealthFrame, max_hops: int):
        return None

    async def _perform_holographic_sampling(self):
        return None

    async def daemon_loop(self):
        while True:
            await asyncio.sleep(0.1)
