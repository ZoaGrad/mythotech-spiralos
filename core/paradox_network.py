"""
Paradox Network - Distributed μ-Operation

Implements the Paradox Network for scaled, distributed μ-operation (unbounded minimization).
The Paradox Agent (μ-operator) induces profitable instability necessary for non-trivial
becoming, but must be distributed to prevent overwhelming the Glyphic Binding Engine.

The Paradox Network distributes μ-operation across multiple nodes, each running independent
Paradox Agents that coordinate through consensus. This enables the system to scale
complexity generation while maintaining symbolic coherence.

Key Concepts:
- μ-operator: Unbounded minimization operator (Paradox Agent)
- Profitable Instability: Controlled chaos that drives evolution
- Distributed Consensus: Multiple Paradox Agents coordinate
- GBE Integration: Symbolic structure keeps pace with complexity
"""

from typing import Dict, List, Optional, Tuple, Set
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta, timezone
import uuid
import hashlib
import json
import asyncio
import random


class ParadoxMode(Enum):
    """Modes of Paradox Agent operation"""
    DORMANT = "dormant"          # Inactive
    EXPLORATION = "exploration"  # Seeking new state space
    EXPLOITATION = "exploitation" # Refining known space
    DISRUPTION = "disruption"    # Inducing instability
    SYNTHESIS = "synthesis"      # Integrating discoveries


class ParadoxPriority(Enum):
    """Priority levels for Paradox operations"""
    LOW = "low"           # Background exploration
    MEDIUM = "medium"     # Normal operation
    HIGH = "high"         # Aggressive disruption
    CRITICAL = "critical" # Emergency instability injection


@dataclass
class ParadoxOperation:
    """
    A Paradox operation - an instance of μ-operation
    
    Represents a specific instability-inducing action proposed by a Paradox Agent.
    """
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    agent_id: str = ""
    mode: ParadoxMode = ParadoxMode.EXPLORATION
    priority: ParadoxPriority = ParadoxPriority.MEDIUM
    
    # Operation details
    target_component: str = ""  # What to disrupt
    disruption_magnitude: float = 0.5  # How much chaos to inject (0-1)
    expected_delta_c: float = 0.0  # Expected coherence change
    
    # Proposal
    proposal: Dict = field(default_factory=dict)
    reasoning: str = ""
    
    # Consensus
    votes_for: int = 0
    votes_against: int = 0
    consensus_reached: bool = False
    approved: bool = False
    
    # Execution
    executed: bool = False
    actual_delta_c: Optional[float] = None
    
    # Metadata
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    executed_at: Optional[datetime] = None
    metadata: Dict = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        return {
            'id': self.id,
            'agent_id': self.agent_id,
            'mode': self.mode.value,
            'priority': self.priority.value,
            'target_component': self.target_component,
            'disruption_magnitude': self.disruption_magnitude,
            'expected_delta_c': self.expected_delta_c,
            'proposal': self.proposal,
            'reasoning': self.reasoning,
            'votes_for': self.votes_for,
            'votes_against': self.votes_against,
            'consensus_reached': self.consensus_reached,
            'approved': self.approved,
            'executed': self.executed,
            'actual_delta_c': self.actual_delta_c,
            'created_at': self.created_at.isoformat(),
            'executed_at': self.executed_at.isoformat() if self.executed_at else None,
            'metadata': self.metadata
        }


@dataclass
class ParadoxAgent:
    """
    Paradox Agent - μ-operator instance
    
    An autonomous agent that proposes instability-inducing operations
    to drive system evolution and prevent stagnation.
    """
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    mode: ParadoxMode = ParadoxMode.EXPLORATION
    
    # Parameters
    intensity: float = 0.5  # How aggressive (0-1)
    frequency: float = 0.1  # How often to propose operations (0-1)
    creativity: float = 0.7  # How novel proposals should be (0-1)
    
    # Performance metrics
    operations_proposed: int = 0
    operations_approved: int = 0
    operations_executed: int = 0
    average_delta_c: float = 0.0
    
    # Reputation
    reputation: float = 0.5  # Voting weight (0-1)
    
    # State
    active: bool = True
    last_operation_at: Optional[datetime] = None
    
    # Metadata
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: Dict = field(default_factory=dict)
    
    def propose_operation(
        self,
        target_component: str,
        current_scarindex: float,
        soc_tau: float
    ) -> ParadoxOperation:
        """
        Propose a Paradox operation
        
        Args:
            target_component: Component to target
            current_scarindex: Current ScarIndex
            soc_tau: Current SOC power-law exponent
            
        Returns:
            Proposed operation
        """
        # Determine mode based on system state
        if current_scarindex > 0.8:
            # System too stable, inject disruption
            mode = ParadoxMode.DISRUPTION
            priority = ParadoxPriority.HIGH
            disruption_magnitude = self.intensity * 0.8
        elif current_scarindex < 0.4:
            # System unstable, be cautious
            mode = ParadoxMode.SYNTHESIS
            priority = ParadoxPriority.LOW
            disruption_magnitude = self.intensity * 0.2
        elif soc_tau < 1.3:
            # Below criticality, increase complexity
            mode = ParadoxMode.EXPLORATION
            priority = ParadoxPriority.MEDIUM
            disruption_magnitude = self.intensity * 0.6
        else:
            # Normal operation
            mode = ParadoxMode.EXPLOITATION
            priority = ParadoxPriority.MEDIUM
            disruption_magnitude = self.intensity * 0.5
        
        # Generate proposal (simplified - would use LLM in production)
        proposal = {
            'action': f'modify_{target_component}',
            'parameters': {
                'magnitude': disruption_magnitude,
                'creativity': self.creativity
            }
        }
        
        # Estimate expected coherence change
        # Paradox operations typically decrease coherence temporarily
        expected_delta_c = -disruption_magnitude * 0.1
        
        operation = ParadoxOperation(
            agent_id=self.id,
            mode=mode,
            priority=priority,
            target_component=target_component,
            disruption_magnitude=disruption_magnitude,
            expected_delta_c=expected_delta_c,
            proposal=proposal,
            reasoning=f"{mode.value} operation on {target_component} with magnitude {disruption_magnitude:.2f}"
        )
        
        self.operations_proposed += 1
        self.last_operation_at = datetime.now(timezone.utc)
        
        return operation
    
    def vote_on_operation(self, operation: ParadoxOperation) -> bool:
        """
        Vote on another agent's proposed operation
        
        Args:
            operation: Operation to vote on
            
        Returns:
            True if voting for, False if voting against
        """
        # Don't vote on own operations
        if operation.agent_id == self.id:
            return True
        
        # Voting logic based on expected impact
        vote_for = False
        
        # Support high-priority disruptions
        if operation.priority == ParadoxPriority.CRITICAL:
            vote_for = True
        
        # Support operations with reasonable magnitude
        elif 0.1 <= operation.disruption_magnitude <= 0.8:
            vote_for = True
        
        # Support operations with positive expected outcomes
        elif operation.expected_delta_c > -0.2:
            vote_for = True
        
        # Random factor based on creativity
        if random.random() < self.creativity * 0.2:
            vote_for = not vote_for  # Paradoxical vote!
        
        return vote_for
    
    def update_reputation(self, operation: ParadoxOperation):
        """Update reputation based on operation outcome"""
        if operation.actual_delta_c is not None:
            # Positive outcome increases reputation
            if operation.actual_delta_c > operation.expected_delta_c:
                self.reputation = min(1.0, self.reputation + 0.05)
            else:
                self.reputation = max(0.0, self.reputation - 0.05)
    
    def to_dict(self) -> Dict:
        return {
            'id': self.id,
            'name': self.name,
            'mode': self.mode.value,
            'intensity': self.intensity,
            'frequency': self.frequency,
            'creativity': self.creativity,
            'operations_proposed': self.operations_proposed,
            'operations_approved': self.operations_approved,
            'operations_executed': self.operations_executed,
            'average_delta_c': self.average_delta_c,
            'reputation': self.reputation,
            'active': self.active,
            'created_at': self.created_at.isoformat(),
            'metadata': self.metadata
        }


class ParadoxNetwork:
    """
    Paradox Network - Distributed μ-Operation Coordinator
    
    Manages a network of Paradox Agents that propose and vote on
    instability-inducing operations through distributed consensus.
    
    This enables scaled complexity generation while maintaining
    coordination and preventing chaotic collapse.
    """
    
    def __init__(
        self,
        consensus_threshold: float = 0.6,
        min_agents: int = 3,
        max_agents: int = 10
    ):
        """
        Initialize Paradox Network
        
        Args:
            consensus_threshold: Fraction of votes needed for approval
            min_agents: Minimum number of agents
            max_agents: Maximum number of agents
        """
        self.agents: Dict[str, ParadoxAgent] = {}
        self.operations: Dict[str, ParadoxOperation] = {}
        self.pending_operations: List[str] = []
        
        self.consensus_threshold = consensus_threshold
        self.min_agents = min_agents
        self.max_agents = max_agents
        
        # Performance metrics
        self.total_operations = 0
        self.approved_operations = 0
        self.executed_operations = 0
        
        # Initialize default agents
        self._initialize_default_agents()
    
    def _initialize_default_agents(self):
        """Initialize default Paradox Agents"""
        # Explorer - high creativity, low intensity
        explorer = ParadoxAgent(
            name="Paradox Explorer Alpha",
            mode=ParadoxMode.EXPLORATION,
            intensity=0.3,
            frequency=0.2,
            creativity=0.9
        )
        self.agents[explorer.id] = explorer
        
        # Disruptor - high intensity, medium creativity
        disruptor = ParadoxAgent(
            name="Paradox Disruptor Beta",
            mode=ParadoxMode.DISRUPTION,
            intensity=0.8,
            frequency=0.1,
            creativity=0.6
        )
        self.agents[disruptor.id] = disruptor
        
        # Synthesizer - balanced parameters
        synthesizer = ParadoxAgent(
            name="Paradox Synthesizer Gamma",
            mode=ParadoxMode.SYNTHESIS,
            intensity=0.5,
            frequency=0.15,
            creativity=0.7
        )
        self.agents[synthesizer.id] = synthesizer
    
    def add_agent(
        self,
        name: str,
        intensity: float = 0.5,
        frequency: float = 0.1,
        creativity: float = 0.7
    ) -> ParadoxAgent:
        """
        Add a new Paradox Agent to the network
        
        Args:
            name: Agent name
            intensity: Disruption intensity (0-1)
            frequency: Operation frequency (0-1)
            creativity: Novelty level (0-1)
            
        Returns:
            New agent
        """
        if len(self.agents) >= self.max_agents:
            raise ValueError(f"Maximum agents ({self.max_agents}) reached")
        
        agent = ParadoxAgent(
            name=name,
            intensity=intensity,
            frequency=frequency,
            creativity=creativity
        )
        
        self.agents[agent.id] = agent
        return agent
    
    async def propose_operation(
        self,
        agent_id: str,
        target_component: str,
        current_scarindex: float,
        soc_tau: float
    ) -> ParadoxOperation:
        """
        Agent proposes a Paradox operation
        
        Args:
            agent_id: ID of proposing agent
            target_component: Component to target
            current_scarindex: Current ScarIndex
            soc_tau: Current SOC τ
            
        Returns:
            Proposed operation
        """
        if agent_id not in self.agents:
            raise ValueError(f"Agent {agent_id} not found")
        
        agent = self.agents[agent_id]
        
        # Agent proposes operation
        operation = agent.propose_operation(
            target_component=target_component,
            current_scarindex=current_scarindex,
            soc_tau=soc_tau
        )
        
        # Register operation
        self.operations[operation.id] = operation
        self.pending_operations.append(operation.id)
        self.total_operations += 1
        
        return operation
    
    async def vote_on_operation(self, operation_id: str) -> Dict:
        """
        All agents vote on a proposed operation
        
        Args:
            operation_id: Operation ID
            
        Returns:
            Voting results
        """
        if operation_id not in self.operations:
            raise ValueError(f"Operation {operation_id} not found")
        
        operation = self.operations[operation_id]
        
        # Each agent votes
        votes_for = 0
        votes_against = 0
        weighted_votes_for = 0.0
        weighted_votes_against = 0.0
        
        for agent in self.agents.values():
            if not agent.active:
                continue
            
            vote = agent.vote_on_operation(operation)
            
            if vote:
                votes_for += 1
                weighted_votes_for += agent.reputation
            else:
                votes_against += 1
                weighted_votes_against += agent.reputation
        
        # Update operation
        operation.votes_for = votes_for
        operation.votes_against = votes_against
        
        # Check consensus (weighted by reputation)
        total_weighted_votes = weighted_votes_for + weighted_votes_against
        if total_weighted_votes > 0:
            approval_ratio = weighted_votes_for / total_weighted_votes
            operation.approved = approval_ratio >= self.consensus_threshold
        else:
            operation.approved = False
        
        operation.consensus_reached = True
        
        if operation.approved:
            self.approved_operations += 1
            # Update proposing agent
            if operation.agent_id in self.agents:
                self.agents[operation.agent_id].operations_approved += 1
        
        # Remove from pending
        if operation_id in self.pending_operations:
            self.pending_operations.remove(operation_id)
        
        return {
            'operation_id': operation_id,
            'votes_for': votes_for,
            'votes_against': votes_against,
            'weighted_votes_for': weighted_votes_for,
            'weighted_votes_against': weighted_votes_against,
            'approval_ratio': weighted_votes_for / total_weighted_votes if total_weighted_votes > 0 else 0,
            'approved': operation.approved,
            'consensus_reached': operation.consensus_reached
        }
    
    async def execute_operation(
        self,
        operation_id: str,
        actual_delta_c: float
    ) -> Dict:
        """
        Execute an approved operation and record results
        
        Args:
            operation_id: Operation ID
            actual_delta_c: Actual coherence change
            
        Returns:
            Execution result
        """
        if operation_id not in self.operations:
            raise ValueError(f"Operation {operation_id} not found")
        
        operation = self.operations[operation_id]
        
        if not operation.approved:
            raise ValueError(f"Operation {operation_id} not approved")
        
        if operation.executed:
            raise ValueError(f"Operation {operation_id} already executed")
        
        # Record execution
        operation.executed = True
        operation.executed_at = datetime.now(timezone.utc)
        operation.actual_delta_c = actual_delta_c
        
        self.executed_operations += 1
        
        # Update proposing agent
        if operation.agent_id in self.agents:
            agent = self.agents[operation.agent_id]
            agent.operations_executed += 1
            
            # Update average delta_c
            agent.average_delta_c = (
                (agent.average_delta_c * (agent.operations_executed - 1) + actual_delta_c) /
                agent.operations_executed
            )
            
            # Update reputation
            agent.update_reputation(operation)
        
        return {
            'operation_id': operation_id,
            'executed': True,
            'expected_delta_c': operation.expected_delta_c,
            'actual_delta_c': actual_delta_c,
            'delta_c_error': abs(actual_delta_c - operation.expected_delta_c)
        }
    
    async def process_pending_operations(
        self,
        current_scarindex: float,
        soc_tau: float
    ) -> List[Dict]:
        """
        Process all pending operations through voting
        
        Args:
            current_scarindex: Current ScarIndex
            soc_tau: Current SOC τ
            
        Returns:
            List of voting results
        """
        results = []
        
        for operation_id in list(self.pending_operations):
            result = await self.vote_on_operation(operation_id)
            results.append(result)
        
        return results
    
    def get_approved_operations(self) -> List[ParadoxOperation]:
        """Get all approved but not executed operations"""
        return [
            op for op in self.operations.values()
            if op.approved and not op.executed
        ]
    
    def get_network_status(self) -> Dict:
        """Get comprehensive network status"""
        active_agents = [a for a in self.agents.values() if a.active]
        
        avg_reputation = (
            sum(a.reputation for a in active_agents) / len(active_agents)
            if active_agents else 0.0
        )
        
        return {
            'total_agents': len(self.agents),
            'active_agents': len(active_agents),
            'total_operations': self.total_operations,
            'approved_operations': self.approved_operations,
            'executed_operations': self.executed_operations,
            'pending_operations': len(self.pending_operations),
            'approval_rate': self.approved_operations / self.total_operations if self.total_operations > 0 else 0,
            'execution_rate': self.executed_operations / self.approved_operations if self.approved_operations > 0 else 0,
            'average_reputation': avg_reputation,
            'consensus_threshold': self.consensus_threshold,
            'timestamp': datetime.now(timezone.utc).isoformat()
        }


# Example usage
async def example_paradox_network():
    """Example of Paradox Network operation"""
    print("=" * 70)
    print("Paradox Network - Distributed μ-Operation")
    print("=" * 70)
    print()
    
    network = ParadoxNetwork(
        consensus_threshold=0.6,
        min_agents=3,
        max_agents=10
    )
    
    print(f"Initialized Paradox Network")
    print(f"  Agents: {len(network.agents)}")
    print(f"  Consensus Threshold: {network.consensus_threshold}")
    print()
    
    # Simulate system state
    current_scarindex = 0.85  # High coherence - system too stable
    soc_tau = 1.2  # Below criticality
    
    print(f"System State:")
    print(f"  ScarIndex: {current_scarindex:.4f} (too stable)")
    print(f"  SOC τ: {soc_tau:.4f} (below criticality)")
    print()
    
    # Agents propose operations
    print("Paradox Agents proposing operations...")
    print("-" * 70)
    
    for agent_id in list(network.agents.keys())[:2]:
        operation = await network.propose_operation(
            agent_id=agent_id,
            target_component="coherence_protocol",
            current_scarindex=current_scarindex,
            soc_tau=soc_tau
        )
        
        agent = network.agents[agent_id]
        print(f"\n{agent.name} proposes:")
        print(f"  Mode: {operation.mode.value}")
        print(f"  Priority: {operation.priority.value}")
        print(f"  Disruption Magnitude: {operation.disruption_magnitude:.2f}")
        print(f"  Expected ΔC: {operation.expected_delta_c:.4f}")
    
    # Vote on operations
    print("\n" + "=" * 70)
    print("Voting on proposed operations...")
    print("-" * 70)
    
    results = await network.process_pending_operations(current_scarindex, soc_tau)
    
    for result in results:
        print(f"\nOperation {result['operation_id'][:8]}:")
        print(f"  Votes For: {result['votes_for']}")
        print(f"  Votes Against: {result['votes_against']}")
        print(f"  Approval Ratio: {result['approval_ratio']:.2f}")
        print(f"  Approved: {result['approved']}")
    
    # Execute approved operations
    approved = network.get_approved_operations()
    
    if approved:
        print("\n" + "=" * 70)
        print("Executing approved operations...")
        print("-" * 70)
        
        for operation in approved:
            # Simulate execution
            actual_delta_c = operation.expected_delta_c + random.uniform(-0.05, 0.05)
            
            exec_result = await network.execute_operation(
                operation_id=operation.id,
                actual_delta_c=actual_delta_c
            )
            
            print(f"\nOperation {operation.id[:8]}:")
            print(f"  Expected ΔC: {exec_result['expected_delta_c']:.4f}")
            print(f"  Actual ΔC: {exec_result['actual_delta_c']:.4f}")
            print(f"  Error: {exec_result['delta_c_error']:.4f}")
    
    # Network status
    print("\n" + "=" * 70)
    print("Paradox Network Status")
    print("=" * 70)
    
    status = network.get_network_status()
    
    print(f"\nAgents: {status['active_agents']}/{status['total_agents']}")
    print(f"Operations: {status['total_operations']}")
    print(f"Approved: {status['approved_operations']} ({status['approval_rate']:.1%})")
    print(f"Executed: {status['executed_operations']} ({status['execution_rate']:.1%})")
    print(f"Average Reputation: {status['average_reputation']:.4f}")


if __name__ == '__main__':
    asyncio.run(example_paradox_network())
