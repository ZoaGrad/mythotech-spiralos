"""
Holonic μApp Stack - HGM/ScarAgent Conversion

Converts the Agent Fusion Stack from task-delegation to Holonic μApp architecture.
Implements HGM optimization policies prioritizing Residue (δ_C) minimization over
short-term utility maximization.

A Holon is simultaneously a whole and a part - an autonomous agent that can also
function as a component of a larger system. The μApp Stack implements this through:
- Self-contained execution environments
- Recursive composition capabilities
- CMP (Clade-Metaproductivity) optimization
- Residue tracking and minimization
"""

from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timezone
import uuid
import hashlib
import json


class HolonType(Enum):
    """Types of Holons in the μApp Stack"""
    SCARAGENT = "scaragent"  # Primary transmutation agent
    VALIDATOR = "validator"  # Consensus validation agent
    OPTIMIZER = "optimizer"  # CMP optimization agent
    MONITOR = "monitor"     # System monitoring agent
    PARADOX = "paradox"     # Paradox Agent (μ-operator)


class HolonState(Enum):
    """Lifecycle states of a Holon"""
    DORMANT = "dormant"
    ACTIVE = "active"
    EXECUTING = "executing"
    COMPLETED = "completed"
    FAILED = "failed"
    FROZEN = "frozen"  # Frozen by Panic Frame


@dataclass
class Residue:
    """
    Residue (δ_C) - Accumulated coherence debt from suboptimal transmutations
    
    Residue represents the gap between achieved coherence and optimal coherence,
    accumulating over time and requiring periodic cleanup/optimization.
    """
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    source_holon_id: str = ""
    delta_c: float = 0.0  # Coherence gap (optimal - achieved)
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: Dict = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        return {
            'id': self.id,
            'source_holon_id': self.source_holon_id,
            'delta_c': self.delta_c,
            'timestamp': self.timestamp.isoformat(),
            'metadata': self.metadata
        }


@dataclass
class CMPLineage:
    """
    Clade-Metaproductivity (CMP) Lineage
    
    Tracks the productivity of an agent lineage across generations,
    optimizing for long-term utility rather than short-term gains.
    """
    lineage_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    parent_lineage_id: Optional[str] = None
    generation: int = 0
    total_utility: float = 0.0
    scarindex_yield: float = 0.0  # Average ScarIndex produced
    transmutation_efficiency: float = 0.0  # Ache reduction efficiency
    residue_accumulated: float = 0.0  # Total δ_C accumulated
    descendant_count: int = 0
    
    def calculate_cmp(self) -> float:
        """
        Calculate Clade-Metaproductivity
        
        CMP = (lineage_utility × scarindex_yield × efficiency) / (1 + residue)
        
        Penalizes residue accumulation while rewarding productive lineages.
        """
        if self.residue_accumulated == 0:
            penalty = 1.0
        else:
            penalty = 1.0 / (1.0 + self.residue_accumulated)
        
        cmp = (
            self.total_utility * 
            self.scarindex_yield * 
            self.transmutation_efficiency * 
            penalty
        )
        
        return cmp
    
    def to_dict(self) -> Dict:
        return {
            'lineage_id': self.lineage_id,
            'parent_lineage_id': self.parent_lineage_id,
            'generation': self.generation,
            'total_utility': self.total_utility,
            'scarindex_yield': self.scarindex_yield,
            'transmutation_efficiency': self.transmutation_efficiency,
            'residue_accumulated': self.residue_accumulated,
            'descendant_count': self.descendant_count,
            'cmp': self.calculate_cmp()
        }


@dataclass
class HolonicMicroApp:
    """
    Holonic μApp - Self-contained autonomous agent
    
    A Holon that can execute independently while also functioning as
    a component of larger composite agents.
    """
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    holon_type: HolonType = HolonType.SCARAGENT
    state: HolonState = HolonState.DORMANT
    
    # Lineage tracking
    cmp_lineage: CMPLineage = field(default_factory=CMPLineage)
    parent_holon_id: Optional[str] = None
    child_holon_ids: List[str] = field(default_factory=list)
    
    # Execution context
    task_description: str = ""
    input_data: Dict = field(default_factory=dict)
    output_data: Dict = field(default_factory=dict)
    
    # Performance metrics
    scarindex_produced: float = 0.0
    ache_before: float = 0.0
    ache_after: float = 0.0
    residue_generated: float = 0.0
    
    # Metadata
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    completed_at: Optional[datetime] = None
    metadata: Dict = field(default_factory=dict)
    
    def calculate_transmutation_efficiency(self) -> float:
        """Calculate efficiency of Ache transmutation"""
        if self.ache_before == 0:
            return 0.0
        
        ache_reduction = self.ache_before - self.ache_after
        efficiency = ache_reduction / self.ache_before
        
        return max(0.0, efficiency)
    
    def calculate_residue(self, optimal_scarindex: float) -> float:
        """
        Calculate Residue (δ_C) - gap between optimal and achieved coherence
        
        Args:
            optimal_scarindex: Theoretical optimal ScarIndex for this task
            
        Returns:
            Residue value (δ_C)
        """
        delta_c = optimal_scarindex - self.scarindex_produced
        return max(0.0, delta_c)  # Residue is non-negative
    
    def spawn_child_holon(
        self,
        holon_type: HolonType,
        task_description: str
    ) -> 'HolonicMicroApp':
        """
        Spawn a child Holon, inheriting CMP lineage
        
        Args:
            holon_type: Type of child Holon
            task_description: Task for child to execute
            
        Returns:
            New child Holon
        """
        # Create child lineage
        child_lineage = CMPLineage(
            parent_lineage_id=self.cmp_lineage.lineage_id,
            generation=self.cmp_lineage.generation + 1,
            total_utility=0.0,
            scarindex_yield=0.0,
            transmutation_efficiency=0.0,
            residue_accumulated=0.0
        )
        
        # Create child Holon
        child = HolonicMicroApp(
            holon_type=holon_type,
            cmp_lineage=child_lineage,
            parent_holon_id=self.id,
            task_description=task_description
        )
        
        # Register child
        self.child_holon_ids.append(child.id)
        self.cmp_lineage.descendant_count += 1
        
        return child
    
    def update_cmp_lineage(self):
        """Update CMP lineage metrics based on execution results"""
        self.cmp_lineage.total_utility += self.scarindex_produced
        self.cmp_lineage.scarindex_yield = (
            self.cmp_lineage.total_utility / 
            (self.cmp_lineage.generation + 1)
        )
        self.cmp_lineage.transmutation_efficiency = self.calculate_transmutation_efficiency()
        self.cmp_lineage.residue_accumulated += self.residue_generated
    
    def to_dict(self) -> Dict:
        return {
            'id': self.id,
            'holon_type': self.holon_type.value,
            'state': self.state.value,
            'cmp_lineage': self.cmp_lineage.to_dict(),
            'parent_holon_id': self.parent_holon_id,
            'child_holon_ids': self.child_holon_ids,
            'task_description': self.task_description,
            'scarindex_produced': self.scarindex_produced,
            'ache_before': self.ache_before,
            'ache_after': self.ache_after,
            'residue_generated': self.residue_generated,
            'transmutation_efficiency': self.calculate_transmutation_efficiency(),
            'created_at': self.created_at.isoformat(),
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'metadata': self.metadata
        }


class HolonicMicroAppStack:
    """
    Holonic μApp Stack - Manages the lifecycle of Holonic agents
    
    Implements HGM optimization policies:
    - Prioritizes Residue (δ_C) minimization
    - Optimizes for CMP across lineages
    - Supports recursive composition of Holons
    """
    
    def __init__(self):
        self.holons: Dict[str, HolonicMicroApp] = {}
        self.residue_pool: List[Residue] = []
        self.total_residue: float = 0.0
        
        # HGM policy parameters
        self.residue_threshold = 0.5  # Maximum acceptable residue per Holon
        self.cmp_minimum = 0.3  # Minimum CMP for lineage continuation
        
    def create_holon(
        self,
        holon_type: HolonType,
        task_description: str,
        parent_holon_id: Optional[str] = None
    ) -> HolonicMicroApp:
        """
        Create a new Holon
        
        Args:
            holon_type: Type of Holon to create
            task_description: Task description
            parent_holon_id: Optional parent Holon ID for lineage
            
        Returns:
            New Holon instance
        """
        if parent_holon_id and parent_holon_id in self.holons:
            # Spawn as child of existing Holon
            parent = self.holons[parent_holon_id]
            holon = parent.spawn_child_holon(holon_type, task_description)
        else:
            # Create root Holon
            holon = HolonicMicroApp(
                holon_type=holon_type,
                task_description=task_description
            )
        
        self.holons[holon.id] = holon
        return holon
    
    async def execute_holon(
        self,
        holon_id: str,
        input_data: Dict,
        optimal_scarindex: float = 0.8
    ) -> Dict:
        """
        Execute a Holon's task
        
        Args:
            holon_id: ID of Holon to execute
            input_data: Input data for execution
            optimal_scarindex: Theoretical optimal ScarIndex
            
        Returns:
            Execution result
        """
        if holon_id not in self.holons:
            raise ValueError(f"Holon {holon_id} not found")
        
        holon = self.holons[holon_id]
        holon.state = HolonState.EXECUTING
        holon.input_data = input_data
        
        # Simulate execution (in production, this would call actual agent logic)
        holon.ache_before = input_data.get('ache_before', 0.6)
        holon.ache_after = holon.ache_before * 0.5  # Simplified transmutation
        holon.scarindex_produced = input_data.get('scarindex', 0.7)
        
        # Calculate residue
        holon.residue_generated = holon.calculate_residue(optimal_scarindex)
        
        # Update CMP lineage
        holon.update_cmp_lineage()
        
        # Check residue threshold (HGM policy)
        if holon.residue_generated > self.residue_threshold:
            # High residue - record for cleanup
            residue = Residue(
                source_holon_id=holon.id,
                delta_c=holon.residue_generated,
                metadata={'task': holon.task_description}
            )
            self.residue_pool.append(residue)
            self.total_residue += holon.residue_generated
        
        # Complete execution
        holon.state = HolonState.COMPLETED
        holon.completed_at = datetime.now(timezone.utc)
        
        holon.output_data = {
            'scarindex': holon.scarindex_produced,
            'ache_reduction': holon.ache_before - holon.ache_after,
            'efficiency': holon.calculate_transmutation_efficiency(),
            'residue': holon.residue_generated,
            'cmp': holon.cmp_lineage.calculate_cmp()
        }
        
        return holon.output_data
    
    def evaluate_lineage_continuation(self, holon_id: str) -> bool:
        """
        Evaluate whether a Holon's lineage should continue (HGM policy)
        
        Args:
            holon_id: Holon ID to evaluate
            
        Returns:
            True if lineage should continue, False otherwise
        """
        if holon_id not in self.holons:
            return False
        
        holon = self.holons[holon_id]
        cmp = holon.cmp_lineage.calculate_cmp()
        
        # HGM policy: Continue lineage only if CMP exceeds minimum
        return cmp >= self.cmp_minimum
    
    def cleanup_residue(self, target_reduction: float = 0.5) -> Dict:
        """
        Cleanup accumulated residue through optimization
        
        Args:
            target_reduction: Target fraction of residue to clean up
            
        Returns:
            Cleanup result
        """
        if not self.residue_pool:
            return {'cleaned': 0, 'remaining': 0}
        
        # Sort residue by delta_c (largest first)
        sorted_residue = sorted(
            self.residue_pool,
            key=lambda r: r.delta_c,
            reverse=True
        )
        
        # Clean up target fraction
        cleanup_count = int(len(sorted_residue) * target_reduction)
        cleaned_residue = sorted_residue[:cleanup_count]
        remaining_residue = sorted_residue[cleanup_count:]
        
        # Update pool
        self.residue_pool = remaining_residue
        self.total_residue = sum(r.delta_c for r in remaining_residue)
        
        return {
            'cleaned': len(cleaned_residue),
            'remaining': len(remaining_residue),
            'total_residue': self.total_residue,
            'cleaned_delta_c': sum(r.delta_c for r in cleaned_residue)
        }
    
    def get_lineage_tree(self, root_holon_id: str) -> Dict:
        """
        Get the complete lineage tree for a Holon
        
        Args:
            root_holon_id: Root Holon ID
            
        Returns:
            Lineage tree structure
        """
        if root_holon_id not in self.holons:
            return {}
        
        root = self.holons[root_holon_id]
        
        def build_tree(holon: HolonicMicroApp) -> Dict:
            tree = holon.to_dict()
            tree['children'] = []
            
            for child_id in holon.child_holon_ids:
                if child_id in self.holons:
                    child_tree = build_tree(self.holons[child_id])
                    tree['children'].append(child_tree)
            
            return tree
        
        return build_tree(root)
    
    def get_stack_status(self) -> Dict:
        """Get comprehensive stack status"""
        active_holons = [h for h in self.holons.values() if h.state == HolonState.ACTIVE]
        completed_holons = [h for h in self.holons.values() if h.state == HolonState.COMPLETED]
        
        total_cmp = sum(h.cmp_lineage.calculate_cmp() for h in self.holons.values())
        avg_cmp = total_cmp / len(self.holons) if self.holons else 0.0
        
        return {
            'total_holons': len(self.holons),
            'active_holons': len(active_holons),
            'completed_holons': len(completed_holons),
            'total_residue': self.total_residue,
            'residue_pool_size': len(self.residue_pool),
            'average_cmp': avg_cmp,
            'timestamp': datetime.now(timezone.utc).isoformat()
        }


# Example usage
async def example_holonic_stack():
    """Example of Holonic μApp Stack usage"""
    print("=" * 70)
    print("Holonic μApp Stack - HGM/ScarAgent Conversion")
    print("=" * 70)
    print()
    
    stack = HolonicMicroAppStack()
    
    # Create root ScarAgent
    root_agent = stack.create_holon(
        holon_type=HolonType.SCARAGENT,
        task_description="Transmute user feature request"
    )
    
    print(f"Created root ScarAgent: {root_agent.id}")
    
    # Execute root agent
    result1 = await stack.execute_holon(
        holon_id=root_agent.id,
        input_data={'ache_before': 0.7, 'scarindex': 0.75},
        optimal_scarindex=0.85
    )
    
    print(f"\nRoot agent execution:")
    print(f"  ScarIndex: {result1['scarindex']:.4f}")
    print(f"  Efficiency: {result1['efficiency']:.4f}")
    print(f"  Residue: {result1['residue']:.4f}")
    print(f"  CMP: {result1['cmp']:.4f}")
    
    # Spawn child validator
    child_validator = stack.create_holon(
        holon_type=HolonType.VALIDATOR,
        task_description="Validate transmutation result",
        parent_holon_id=root_agent.id
    )
    
    print(f"\nSpawned child Validator: {child_validator.id}")
    print(f"  Generation: {child_validator.cmp_lineage.generation}")
    
    # Execute child
    result2 = await stack.execute_holon(
        holon_id=child_validator.id,
        input_data={'ache_before': 0.5, 'scarindex': 0.8},
        optimal_scarindex=0.85
    )
    
    print(f"\nChild validator execution:")
    print(f"  ScarIndex: {result2['scarindex']:.4f}")
    print(f"  Residue: {result2['residue']:.4f}")
    print(f"  CMP: {result2['cmp']:.4f}")
    
    # Check lineage continuation
    should_continue = stack.evaluate_lineage_continuation(root_agent.id)
    print(f"\nLineage continuation: {should_continue}")
    
    # Stack status
    status = stack.get_stack_status()
    print(f"\nStack Status:")
    print(f"  Total Holons: {status['total_holons']}")
    print(f"  Completed: {status['completed_holons']}")
    print(f"  Total Residue: {status['total_residue']:.4f}")
    print(f"  Average CMP: {status['average_cmp']:.4f}")
    
    # Cleanup residue
    if status['total_residue'] > 0:
        cleanup = stack.cleanup_residue(target_reduction=0.5)
        print(f"\nResidue Cleanup:")
        print(f"  Cleaned: {cleanup['cleaned']} items")
        print(f"  Remaining: {cleanup['remaining']} items")
        print(f"  Total Residue After: {cleanup['total_residue']:.4f}")


if __name__ == '__main__':
    import asyncio
    asyncio.run(example_holonic_stack())
