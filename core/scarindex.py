import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any
from core.db import get_supabase
from core.logging_config import setup_logging

# Setup logging
logger = setup_logging()

class ScarIndex:
    def __init__(self):
        self.supabase = get_supabase()

# --- Legacy/Integration Support Classes ---
from dataclasses import dataclass, field
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
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self):
        return {
            "id": self.id,
            "scarindex": self.scarindex,
            "is_valid": self.is_valid,
            "metadata": self.metadata
        }

class ScarIndexOracle:
    @staticmethod
    def calculate(N: int, c_i_list: List[float], p_i_avg: float, decays_count: int, ache: AcheMeasurement) -> ScarIndexResult:
        """
        Calculate ScarIndex based on components.
        This is a placeholder for the full Oracle logic to support legacy integration.
        """
        # Simple average for now
        score = sum(c_i_list) / N if N > 0 else 0.0
        
        # Apply Ache penalty (simplified)
        ache_factor = (ache.before - ache.after) * 0.1
        score -= ache_factor
        
        return ScarIndexResult(
            id=str(uuid.uuid4()),
            scarindex=max(0.0, min(1.0, score)),
            is_valid=True,
            metadata={
                "N": N,
                "p_i_avg": p_i_avg,
                "decays": decays_count,
                "ache_delta": ache.before - ache.after
            }
        )

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
                .gte("timestamp", since) \
                .execute()
            
            events = resp.data or []
            
            # Calculate ScarIndex
            scarindex_value = self._calculate_scarindex(events)
            
            # Determine if Panic Frame is triggered
            panic_triggered = scarindex_value < 0.3
            
            # Persist to coherence_signals
            signal_data = {
                "timestamp": datetime.utcnow().isoformat(),
                "scarindex_value": scarindex_value,
                "panic_frame_triggered": panic_triggered,
                "control_action_taken": "monitor" if not panic_triggered else "alert",
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
        Placeholder logic: 1.0 (perfect) minus penalty per event.
        """
        if not events:
            return 1.0
        
        # Simple decay model: each event reduces coherence slightly
        # This is a placeholder for the actual complex math
        penalty = len(events) * 0.01
        return max(0.0, 1.0 - penalty)

# Singleton instance
scar_index = ScarIndex()
