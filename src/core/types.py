from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Literal
from datetime import datetime
import uuid

class ScarIndex(BaseModel):
    """
    The coherence metric of the system.
    Range: 0.0 (Total Collapse) to 1.0 (Perfect Resonance).
    """
    value: float = Field(..., ge=0.0, le=1.0)
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    @property
    def is_critical(self) -> bool:
        """Triggers F4 Panic Frame if < 0.3"""
        return self.value < 0.3

class Ache(BaseModel):
    """
    Thermodynamic cost of a reality operation.
    """
    computational_cost: float
    entropy_delta: float
    
    def total_magnitude(self) -> float:
        return self.computational_cost + self.entropy_delta

class Pulse(BaseModel):
    """
    An incoming signal (Truth Pulse) from the void.
    """
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    content: str
    tags: List[str] = []
    source_node: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    ache_potential: float = 0.0

class Fossil(BaseModel):
    """
    An immutable record of a constitutional decision.
    """
    fossil_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    decision_signature: str
    scar_index_snapshot: float
    lineage_hash: str  # Ancestry to ΔΩ.140.0
    artifacts: Dict[str, str]
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class VaultAttestation(Pulse):
    """
    A Pulse that has been fossilized in the Truth Vault (Supabase).
    Extends the pure Signal (Pulse) with Archive metadata.
    """
    final_wi_score: Optional[float] = None
    volume: Optional[int] = None
    complexity: Optional[float] = None
    entropy: Optional[float] = None
    entropy: Optional[float] = None
    description: Optional[str] = None # Maps to 'content' in Pulse, but DB uses description
    scar_reward: float = 0.0 # Phase XII: Holo-Economy Reward

    @validator('final_wi_score', pre=True, always=True)
    def validate_wi_score(cls, v):
        # Ensure WI score is valid if present
        if v is not None and v < 0:
            raise ValueError("WI Score cannot be negative")
        return v
