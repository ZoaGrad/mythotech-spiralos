import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any
from core.db import get_supabase
from core.logging_config import setup_logging

# Setup logging
logger = setup_logging()

from dataclasses import dataclass
import uuid

@dataclass
class AcheMeasurement:
    before: float
    after: float

@dataclass
class CoherenceComponents:
    narrative: float
    social: float
    economic: float
    technical: float

@dataclass
class ScarIndexResult:
    id: str
    scarindex: float
    is_valid: bool
    metadata: Dict[str, Any] = None

    def to_dict(self):
        return {
            "id": self.id,
            "scarindex": self.scarindex,
            "is_valid": self.is_valid,
            "metadata": self.metadata or {}
        }

class ScarIndexOracle:
    @staticmethod
    def calculate(N: int, c_i_list: List[float], p_i_avg: float, decays_count: int, ache: AcheMeasurement) -> ScarIndexResult:
        """
        Calculates the ScarIndex based on coherence components and Ache measurement.
        """
        # Simplified calculation for restoration
        base_score = sum(c_i_list) / N if N > 0 else 0.0
        decay_penalty = decays_count * 0.05
        ache_factor = (ache.before - ache.after) * 0.1
        
        final_score = max(0.0, min(1.0, base_score - decay_penalty + ache_factor))
        
        return ScarIndexResult(
            id=str(uuid.uuid4()),
            scarindex=final_score,
            is_valid=True,
            metadata={
                "N": N,
                "p_i_avg": p_i_avg,
                "decays_count": decays_count,
                "ache_before": ache.before,
                "ache_after": ache.after
            }
        )

class ScarIndex:
    def __init__(self):
        self.supabase = get_supabase()

    def compute_scarindex_for_window(self, minutes: int = 5) -> float:
        """
        Computes ScarIndex based on telemetry events in the last N minutes.
        Persists the result to coherence_signals.
        """
        try:
            since = (datetime.utcnow() - timedelta(minutes=minutes)).isoformat()
            
            # Fetch telemetry events
            resp = self.supabase.table("telemetry_events") \
                .select("*") \
                .gte("event_timestamp", since) \
                .execute()
            
            events = resp.data or []
            
            # Calculate ScarIndex
            scarindex_value = self._calculate_scarindex(events)
            
            # Determine if Panic Frame is triggered
            panic_triggered = scarindex_value < 0.3
            
            if panic_triggered:
                from core.panic_frames import trigger_panic_frames
                trigger_panic_frames(scarindex=scarindex_value)
            
            # Persist to coherence_signals
            signal_data = {
                "timestamp": datetime.utcnow().isoformat(),
                "scarindex_value": scarindex_value,
                "panic_frame_triggered": panic_triggered,
                "control_action_taken": "monitor" if not panic_triggered else "PANIC_FRAME_ACTIVATED",
                "signal_data": {
                    "event_count": len(events),
                    "window_minutes": minutes
                }
            }
            
            self.supabase.table("coherence_signals").insert(signal_data).execute()
            
            logger.info(f"ScarIndex computed: {scarindex_value}", extra={"extra_data": signal_data})
            
            return scarindex_value

        except Exception as e:
            logger.error(f"Error computing ScarIndex: {e}")
            return 0.0

    def _calculate_scarindex(self, events: List[Dict[str, Any]]) -> float:
        """
        Internal logic to calculate ScarIndex from events.
        Weighted decay model based on event types.
        """
        if not events:
            return 1.0
        
        # Weights for different event types (lower is better/neutral, higher is disruptive)
        weights = {
            "github_webhook": 0.01, # Normal activity
            "guardian_heartbeat": 0.0, # Healthy
            "error": 0.1, # System error
            "security_alert": 0.3 # Security breach
        }
        
        total_penalty = 0.0
        for event in events:
            etype = event.get("event_type", "unknown")
            weight = weights.get(etype, 0.05)
            total_penalty += weight
            
        # Normalize to 0.0 - 1.0
        return max(0.0, 1.0 - total_penalty)

# Singleton instance
scar_index = ScarIndex()
