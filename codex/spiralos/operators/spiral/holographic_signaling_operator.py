from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional, Any
import math
import time


@dataclass
class HologramEntry:
    node_id: str
    crs: float
    scar_index: int
    load_percent: float
    headroom_ru: int
    latency_ms: int
    last_epoch: int
    trust_score: float
    is_truth_anchored: bool
    last_update_ts: float


class HolographicSignalingOperator:
    """
    Sovereign Load Distributor signaling operator (ΔΩ.LBI.2).

    Maintains a local "hologram" of node health from HealthFrames and TruthFrames,
    and selects next hops using the Coherence Routing Score (CRS) with the
    Just World Curve (alpha = 2.5) baked into the flow calculation.

    This operator is intentionally in-memory and stateless with respect to Codex Max
    persistence. Higher layers can snapshot / restore hologram state if needed.
    """

    def __init__(self, alpha: float = 2.5, latency_weight: float = 0.2):
        """
        :param alpha: Purity bias exponent; default 2.5 (Just World Curve).
        :param latency_weight: β in CRS = Flow * exp(-β * latency_ms).
        """
        self.alpha = alpha
        self.latency_weight = latency_weight
        self._hologram: Dict[str, HologramEntry] = {}

    # ---------- Core utilities ----------

    def _now(self) -> float:
        return time.time()

    def _compute_flow(self, headroom_ru: int, scar_index: int) -> float:
        """
        Flow = max(headroom_ru, 0) / (1 + SI)^alpha
        """
        effective_headroom = max(headroom_ru, 0)
        return effective_headroom / ((1.0 + float(scar_index)) ** self.alpha)

    def _compute_crs(self, headroom_ru: int, scar_index: int, latency_ms: int) -> float:
        flow = self._compute_flow(headroom_ru, scar_index)
        # CRS = Flow * exp(-β * latency)
        attenuation = math.exp(-self.latency_weight * (latency_ms / 1000.0))
        return flow * attenuation

    # ---------- Ingestion APIs ----------

    def ingest_health_frames(self, frames: List[Dict[str, Any]]) -> None:
        """
        Ingest a batch of HealthFrames and update the local hologram.

        Each frame should respect the HealthFrame schema, but we are permissive and
        default missing fields to conservative values.
        """
        now_ts = self._now()

        for frame in frames:
            node_id = str(frame.get("node_id"))
            if not node_id:
                continue

            epoch = int(frame.get("epoch", 0))
            scar_index = int(frame.get("scar_index", 100))
            load_percent = float(frame.get("load_percent", 1.0))
            headroom_ru = int(frame.get("headroom_ru", 0))
            latency_ms = int(frame.get("latency_ms", 10_000))
            # Use provided CRS if present; otherwise compute from physics
            crs = float(frame.get("crs")) if "crs" in frame else self._compute_crs(
                headroom_ru=headroom_ru,
                scar_index=scar_index,
                latency_ms=latency_ms,
            )

            existing = self._hologram.get(node_id)

            # Basic freshness rule: prefer newer epochs; if same epoch, prefer higher trust
            if existing is not None:
                if epoch < existing.last_epoch:
                    # Stale update, ignore
                    continue
                if epoch == existing.last_epoch and existing.is_truth_anchored:
                    # Do not overwrite truth-anchored data with plain gossip
                    continue

            trust_score = 0.5
            if existing is not None:
                # Small trust decay over time for non-truth entries
                trust_score = existing.trust_score
                if not existing.is_truth_anchored:
                    elapsed = max(now_ts - existing.last_update_ts, 0.0)
                    # simple exponential decay (per hour)
                    decay_factor = math.exp(-elapsed / 3600.0)
                    trust_score *= decay_factor
                # blend in new evidence
                trust_score = min(1.0, trust_score + 0.1)

            entry = HologramEntry(
                node_id=node_id,
                crs=crs,
                scar_index=scar_index,
                load_percent=load_percent,
                headroom_ru=headroom_ru,
                latency_ms=latency_ms,
                last_epoch=epoch,
                trust_score=trust_score,
                is_truth_anchored=False if existing is None else existing.is_truth_anchored,
                last_update_ts=now_ts,
            )
            self._hologram[node_id] = entry

    def ingest_truth_frames(self, truth_frames: List[Dict[str, Any]]) -> None:
        """
        Ingest TruthFrames and override hologram entries with high-trust data.

        TruthFrames must contain:
          - "health_frame": HealthFrame dict
          - "witness_multisig": list of signatures (not validated here)
        """
        now_ts = self._now()

        for tf in truth_frames:
            hf = tf.get("health_frame")
            if not isinstance(hf, dict):
                continue

            node_id = str(hf.get("node_id"))
            if not node_id:
                continue

            epoch = int(hf.get("epoch", 0))
            scar_index = int(hf.get("scar_index", 100))
            load_percent = float(hf.get("load_percent", 1.0))
            headroom_ru = int(hf.get("headroom_ru", 0))
            latency_ms = int(hf.get("latency_ms", 10_000))
            crs = float(hf.get("crs")) if "crs" in hf else self._compute_crs(
                headroom_ru=headroom_ru,
                scar_index=scar_index,
                latency_ms=latency_ms,
            )

            existing = self._hologram.get(node_id)
            if existing is not None and epoch < existing.last_epoch:
                # Do not rollback to older truth
                continue

            entry = HologramEntry(
                node_id=node_id,
                crs=crs,
                scar_index=scar_index,
                load_percent=load_percent,
                headroom_ru=headroom_ru,
                latency_ms=latency_ms,
                last_epoch=epoch,
                trust_score=1.0,  # anchored by witnesses
                is_truth_anchored=True,
                last_update_ts=now_ts,
            )
            self._hologram[node_id] = entry

    # ---------- Routing API ----------

    def select_next_hop(self, constraints: Optional[Dict[str, Any]] = None) -> Optional[str]:
        """
        Select the best next hop based on CRS and constraints.

        :param constraints: optional dict:
            {
                "min_headroom_ru": int,
                "max_latency_ms": int,
                "max_scar_index": int,
                "require_truth_anchored": bool
            }
        :return: node_id of selected next hop, or None if no candidate fits.
        """
        if constraints is None:
            constraints = {}

        min_headroom_ru = int(constraints.get("min_headroom_ru", 0))
        max_latency_ms = int(constraints.get("max_latency_ms", 10_000))
        max_scar_index = int(constraints.get("max_scar_index", 100))
        require_truth_anchored = bool(constraints.get("require_truth_anchored", False))

        candidates: List[HologramEntry] = []
        for entry in self._hologram.values():
            if entry.headroom_ru < min_headroom_ru:
                continue
            if entry.latency_ms > max_latency_ms:
                continue
            if entry.scar_index > max_scar_index:
                continue
            if require_truth_anchored and not entry.is_truth_anchored:
                continue
            candidates.append(entry)

        if not candidates:
            return None

        # Rank by CRS desc, then by (scar_index asc, load_percent asc)
        candidates.sort(
            key=lambda e: (
                -e.crs,
                e.scar_index,
                e.load_percent,
            )
        )

        return candidates[0].node_id

    # ---------- Introspection ----------

    def get_hologram_snapshot(self) -> Dict[str, Dict[str, Any]]:
        """
        Return a JSON-ready snapshot of the hologram state.
        """
        return {
            node_id: {
                "crs": e.crs,
                "scar_index": e.scar_index,
                "load_percent": e.load_percent,
                "headroom_ru": e.headroom_ru,
                "latency_ms": e.latency_ms,
                "last_epoch": e.last_epoch,
                "trust_score": e.trust_score,
                "is_truth_anchored": e.is_truth_anchored,
                "last_update_ts": e.last_update_ts,
            }
            for node_id, e in self._hologram.items()
        }

