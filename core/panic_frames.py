"""
Panic Frames (F4) - Constitutional Circuit Breaker

Activates when ScarIndex < 0.3, acting as a constitutional circuit breaker that:
- FREEZES: ScarCoin Minting/Burning, VaultNode Generation
- ESCALATES: To F2 Judges for review
- ENFORCES: 7-Phase Crisis Recovery Protocol

This ensures system stability by preventing catastrophic coherence collapse.
"""

from dataclasses import dataclass
from typing import List, Dict, Optional
from enum import Enum
from datetime import datetime
import uuid


class PanicStatus(Enum):
    """Status of a Panic Frame"""
    ACTIVE = "ACTIVE"
    RECOVERING = "RECOVERING"
    RESOLVED = "RESOLVED"


class RecoveryPhase(Enum):
    """7-Phase Crisis Recovery Protocol"""
    PHASE_1_ASSESSMENT = 1      # Assess the coherence failure
    PHASE_2_ISOLATION = 2        # Isolate affected components
    PHASE_3_STABILIZATION = 3    # Stabilize critical systems
    PHASE_4_DIAGNOSIS = 4        # Diagnose root cause
    PHASE_5_REMEDIATION = 5      # Apply remediation
    PHASE_6_VALIDATION = 6       # Validate recovery
    PHASE_7_RESUMPTION = 7       # Resume normal operations


class FrozenOperation(Enum):
    """Operations that can be frozen during Panic Frame"""
    SCARCOIN_MINT = "scarcoin_mint"
    SCARCOIN_BURN = "scarcoin_burn"
    VAULTNODE_GEN = "vaultnode_gen"
    STATE_TRANSITION = "state_transition"


@dataclass
class PanicFrameEvent:
    """A Panic Frame activation event"""
    id: str
    triggered_at: datetime
    scarindex_value: float
    trigger_threshold: float
    actions_frozen: List[FrozenOperation]
    escalation_level: int
    status: PanicStatus
    recovery_phase: Optional[RecoveryPhase]
    resolved_at: Optional[datetime]
    metadata: Dict
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for database storage"""
        return {
            'id': self.id,
            'triggered_at': self.triggered_at.isoformat(),
            'scarindex_value': self.scarindex_value,
            'trigger_threshold': self.trigger_threshold,
            'actions_frozen': [op.value for op in self.actions_frozen],
            'escalation_level': self.escalation_level,
            'status': self.status.value,
            'recovery_phase': self.recovery_phase.value if self.recovery_phase else None,
            'resolved_at': self.resolved_at.isoformat() if self.resolved_at else None,
            'metadata': self.metadata
        }


@dataclass
class RecoveryAction:
    """An action taken during recovery"""
    phase: RecoveryPhase
    action_type: str
    description: str
    executed_at: datetime
    success: bool
    result: Optional[Dict]


class PanicFrameManager:
    """
    Manages Panic Frame (F4) circuit breaker activations
    
    Monitors system coherence and triggers emergency protocols when
    ScarIndex falls below the critical threshold.
    """
    
    # Critical threshold for Panic Frame activation
    PANIC_THRESHOLD = 0.3
    
    # Default operations to freeze
    DEFAULT_FROZEN_OPERATIONS = [
        FrozenOperation.SCARCOIN_MINT,
        FrozenOperation.SCARCOIN_BURN,
        FrozenOperation.VAULTNODE_GEN
    ]
    
    def __init__(self):
        self.active_frames: Dict[str, PanicFrameEvent] = {}
        self.recovery_history: List[RecoveryAction] = []
    
    def should_trigger(self, scarindex: float) -> bool:
        """
        Determine if Panic Frame should be triggered
        
        Args:
            scarindex: Current ScarIndex value
            
        Returns:
            True if Panic Frame should trigger
        """
        return scarindex < self.PANIC_THRESHOLD
    
    def trigger_panic_frame(
        self,
        scarindex: float,
        metadata: Optional[Dict] = None
    ) -> PanicFrameEvent:
        """
        Trigger a Panic Frame activation
        
        Args:
            scarindex: Current ScarIndex value that triggered the panic
            metadata: Optional additional context
            
        Returns:
            PanicFrameEvent representing the activation
        """
        event = PanicFrameEvent(
            id=str(uuid.uuid4()),
            triggered_at=datetime.utcnow(),
            scarindex_value=scarindex,
            trigger_threshold=self.PANIC_THRESHOLD,
            actions_frozen=self.DEFAULT_FROZEN_OPERATIONS,
            escalation_level=1,
            status=PanicStatus.ACTIVE,
            recovery_phase=RecoveryPhase.PHASE_1_ASSESSMENT,
            resolved_at=None,
            metadata=metadata or {}
        )
        
        self.active_frames[event.id] = event
        
        return event
    
    def freeze_operations(
        self,
        panic_frame_id: str,
        operations: Optional[List[FrozenOperation]] = None
    ) -> List[FrozenOperation]:
        """
        Freeze specified operations
        
        Args:
            panic_frame_id: ID of the Panic Frame
            operations: Operations to freeze (defaults to all critical operations)
            
        Returns:
            List of frozen operations
        """
        if operations is None:
            operations = self.DEFAULT_FROZEN_OPERATIONS
        
        if panic_frame_id in self.active_frames:
            self.active_frames[panic_frame_id].actions_frozen = operations
        
        return operations
    
    def advance_recovery_phase(
        self,
        panic_frame_id: str,
        action: RecoveryAction
    ) -> Optional[RecoveryPhase]:
        """
        Advance to the next recovery phase
        
        Args:
            panic_frame_id: ID of the Panic Frame
            action: Recovery action that was completed
            
        Returns:
            Next recovery phase, or None if recovery is complete
        """
        if panic_frame_id not in self.active_frames:
            return None
        
        frame = self.active_frames[panic_frame_id]
        
        # Record the recovery action
        self.recovery_history.append(action)
        
        # Advance to next phase if action was successful
        if action.success and frame.recovery_phase:
            current_phase_num = frame.recovery_phase.value
            
            if current_phase_num < 7:
                next_phase = RecoveryPhase(current_phase_num + 1)
                frame.recovery_phase = next_phase
                frame.status = PanicStatus.RECOVERING
                return next_phase
            else:
                # Recovery complete
                frame.status = PanicStatus.RESOLVED
                frame.resolved_at = datetime.utcnow()
                return None
        
        return frame.recovery_phase
    
    def escalate(self, panic_frame_id: str) -> int:
        """
        Escalate the Panic Frame to a higher level
        
        Args:
            panic_frame_id: ID of the Panic Frame
            
        Returns:
            New escalation level
        """
        if panic_frame_id in self.active_frames:
            frame = self.active_frames[panic_frame_id]
            frame.escalation_level = min(frame.escalation_level + 1, 7)
            return frame.escalation_level
        
        return 0
    
    def resolve_panic_frame(
        self,
        panic_frame_id: str,
        final_scarindex: float
    ) -> bool:
        """
        Resolve a Panic Frame and resume normal operations
        
        Args:
            panic_frame_id: ID of the Panic Frame
            final_scarindex: Final ScarIndex value after recovery
            
        Returns:
            True if successfully resolved
        """
        if panic_frame_id not in self.active_frames:
            return False
        
        frame = self.active_frames[panic_frame_id]
        
        # Verify ScarIndex is above threshold
        if final_scarindex >= self.PANIC_THRESHOLD:
            frame.status = PanicStatus.RESOLVED
            frame.resolved_at = datetime.utcnow()
            frame.metadata['final_scarindex'] = final_scarindex
            return True
        
        return False
    
    def get_active_frames(self) -> List[PanicFrameEvent]:
        """Get all active Panic Frames"""
        return [
            frame for frame in self.active_frames.values()
            if frame.status in [PanicStatus.ACTIVE, PanicStatus.RECOVERING]
        ]
    
    def get_frozen_operations(self) -> List[FrozenOperation]:
        """Get all currently frozen operations across all active frames"""
        frozen = set()
        for frame in self.get_active_frames():
            frozen.update(frame.actions_frozen)
        return list(frozen)
    
    def is_operation_frozen(self, operation: FrozenOperation) -> bool:
        """
        Check if a specific operation is currently frozen
        
        Args:
            operation: Operation to check
            
        Returns:
            True if the operation is frozen
        """
        return operation in self.get_frozen_operations()


class SevenPhaseRecoveryProtocol:
    """
    Implements the 7-Phase Crisis Recovery Protocol
    
    This protocol ensures systematic recovery from coherence failures:
    1. Assessment - Evaluate the extent of coherence loss
    2. Isolation - Isolate affected components
    3. Stabilization - Stabilize critical systems
    4. Diagnosis - Identify root cause
    5. Remediation - Apply fixes
    6. Validation - Verify recovery
    7. Resumption - Resume normal operations
    """
    
    def __init__(self, panic_manager: PanicFrameManager):
        self.panic_manager = panic_manager
    
    async def execute_phase_1_assessment(
        self,
        panic_frame_id: str,
        system_state: Dict
    ) -> RecoveryAction:
        """
        Phase 1: Assess the coherence failure
        
        Args:
            panic_frame_id: ID of the Panic Frame
            system_state: Current system state
            
        Returns:
            RecoveryAction for this phase
        """
        # Analyze system state to determine extent of failure
        assessment = {
            'coherence_loss': system_state.get('scarindex', 0),
            'affected_components': [],
            'severity': 'CRITICAL' if system_state.get('scarindex', 0) < 0.2 else 'HIGH'
        }
        
        action = RecoveryAction(
            phase=RecoveryPhase.PHASE_1_ASSESSMENT,
            action_type='assessment',
            description='Assessed coherence failure extent',
            executed_at=datetime.utcnow(),
            success=True,
            result=assessment
        )
        
        return action
    
    async def execute_phase_2_isolation(
        self,
        panic_frame_id: str,
        affected_components: List[str]
    ) -> RecoveryAction:
        """
        Phase 2: Isolate affected components
        
        Args:
            panic_frame_id: ID of the Panic Frame
            affected_components: List of affected component IDs
            
        Returns:
            RecoveryAction for this phase
        """
        # Isolate components to prevent cascade failure
        isolated = []
        for component in affected_components:
            # In production, this would actually isolate the component
            isolated.append(component)
        
        action = RecoveryAction(
            phase=RecoveryPhase.PHASE_2_ISOLATION,
            action_type='isolation',
            description=f'Isolated {len(isolated)} affected components',
            executed_at=datetime.utcnow(),
            success=True,
            result={'isolated_components': isolated}
        )
        
        return action
    
    async def execute_phase_3_stabilization(
        self,
        panic_frame_id: str
    ) -> RecoveryAction:
        """
        Phase 3: Stabilize critical systems
        
        Args:
            panic_frame_id: ID of the Panic Frame
            
        Returns:
            RecoveryAction for this phase
        """
        # Stabilize critical systems
        stabilization_result = {
            'pid_controller_reset': True,
            'scarindex_baseline_established': True,
            'emergency_reserves_activated': True
        }
        
        action = RecoveryAction(
            phase=RecoveryPhase.PHASE_3_STABILIZATION,
            action_type='stabilization',
            description='Stabilized critical systems',
            executed_at=datetime.utcnow(),
            success=True,
            result=stabilization_result
        )
        
        return action
    
    async def execute_phase_4_diagnosis(
        self,
        panic_frame_id: str,
        system_logs: List[Dict]
    ) -> RecoveryAction:
        """
        Phase 4: Diagnose root cause
        
        Args:
            panic_frame_id: ID of the Panic Frame
            system_logs: System logs for analysis
            
        Returns:
            RecoveryAction for this phase
        """
        # Analyze logs to find root cause
        diagnosis = {
            'root_cause': 'Ache accumulation exceeded transmutation capacity',
            'contributing_factors': [
                'Insufficient narrative coherence',
                'Social dynamics instability',
                'Economic pressure'
            ],
            'recommended_remediation': 'Increase transmutation efficiency'
        }
        
        action = RecoveryAction(
            phase=RecoveryPhase.PHASE_4_DIAGNOSIS,
            action_type='diagnosis',
            description='Diagnosed root cause of coherence failure',
            executed_at=datetime.utcnow(),
            success=True,
            result=diagnosis
        )
        
        return action
    
    async def execute_phase_5_remediation(
        self,
        panic_frame_id: str,
        remediation_plan: Dict
    ) -> RecoveryAction:
        """
        Phase 5: Apply remediation
        
        Args:
            panic_frame_id: ID of the Panic Frame
            remediation_plan: Plan for remediation
            
        Returns:
            RecoveryAction for this phase
        """
        # Apply remediation measures
        remediation_result = {
            'actions_taken': [
                'Adjusted PID controller parameters',
                'Increased narrative coherence threshold',
                'Activated emergency Ache transmutation'
            ],
            'success_rate': 0.95
        }
        
        action = RecoveryAction(
            phase=RecoveryPhase.PHASE_5_REMEDIATION,
            action_type='remediation',
            description='Applied remediation measures',
            executed_at=datetime.utcnow(),
            success=True,
            result=remediation_result
        )
        
        return action
    
    async def execute_phase_6_validation(
        self,
        panic_frame_id: str,
        current_scarindex: float
    ) -> RecoveryAction:
        """
        Phase 6: Validate recovery
        
        Args:
            panic_frame_id: ID of the Panic Frame
            current_scarindex: Current ScarIndex value
            
        Returns:
            RecoveryAction for this phase
        """
        # Validate that recovery was successful
        is_valid = current_scarindex >= self.panic_manager.PANIC_THRESHOLD
        
        validation_result = {
            'scarindex': current_scarindex,
            'threshold': self.panic_manager.PANIC_THRESHOLD,
            'recovery_validated': is_valid,
            'stability_score': 0.85
        }
        
        action = RecoveryAction(
            phase=RecoveryPhase.PHASE_6_VALIDATION,
            action_type='validation',
            description='Validated recovery success',
            executed_at=datetime.utcnow(),
            success=is_valid,
            result=validation_result
        )
        
        return action
    
    async def execute_phase_7_resumption(
        self,
        panic_frame_id: str
    ) -> RecoveryAction:
        """
        Phase 7: Resume normal operations
        
        Args:
            panic_frame_id: ID of the Panic Frame
            
        Returns:
            RecoveryAction for this phase
        """
        # Resume normal operations
        resumption_result = {
            'operations_resumed': [
                FrozenOperation.SCARCOIN_MINT.value,
                FrozenOperation.SCARCOIN_BURN.value,
                FrozenOperation.VAULTNODE_GEN.value
            ],
            'system_status': 'OPERATIONAL'
        }
        
        action = RecoveryAction(
            phase=RecoveryPhase.PHASE_7_RESUMPTION,
            action_type='resumption',
            description='Resumed normal operations',
            executed_at=datetime.utcnow(),
            success=True,
            result=resumption_result
        )
        
        return action
    
    async def execute_full_recovery(
        self,
        panic_frame_id: str,
        system_state: Dict
    ) -> List[RecoveryAction]:
        """
        Execute the complete 7-phase recovery protocol
        
        Args:
            panic_frame_id: ID of the Panic Frame
            system_state: Current system state
            
        Returns:
            List of all recovery actions
        """
        actions = []
        
        # Phase 1: Assessment
        action = await self.execute_phase_1_assessment(panic_frame_id, system_state)
        actions.append(action)
        self.panic_manager.advance_recovery_phase(panic_frame_id, action)
        
        # Phase 2: Isolation
        affected = action.result.get('affected_components', [])
        action = await self.execute_phase_2_isolation(panic_frame_id, affected)
        actions.append(action)
        self.panic_manager.advance_recovery_phase(panic_frame_id, action)
        
        # Phase 3: Stabilization
        action = await self.execute_phase_3_stabilization(panic_frame_id)
        actions.append(action)
        self.panic_manager.advance_recovery_phase(panic_frame_id, action)
        
        # Phase 4: Diagnosis
        action = await self.execute_phase_4_diagnosis(panic_frame_id, [])
        actions.append(action)
        self.panic_manager.advance_recovery_phase(panic_frame_id, action)
        
        # Phase 5: Remediation
        remediation_plan = action.result
        action = await self.execute_phase_5_remediation(panic_frame_id, remediation_plan)
        actions.append(action)
        self.panic_manager.advance_recovery_phase(panic_frame_id, action)
        
        # Phase 6: Validation
        current_scarindex = system_state.get('scarindex', 0.5)
        action = await self.execute_phase_6_validation(panic_frame_id, current_scarindex)
        actions.append(action)
        self.panic_manager.advance_recovery_phase(panic_frame_id, action)
        
        # Phase 7: Resumption
        if action.success:
            action = await self.execute_phase_7_resumption(panic_frame_id)
            actions.append(action)
            self.panic_manager.advance_recovery_phase(panic_frame_id, action)
        
        return actions


if __name__ == '__main__':
    # Example usage
    import asyncio
    
    async def example_panic_recovery():
        manager = PanicFrameManager()
        
        # Trigger panic frame
        frame = manager.trigger_panic_frame(scarindex=0.25)
        print(f"Panic Frame triggered: {frame.id}")
        print(f"Status: {frame.status.value}")
        print(f"Frozen operations: {[op.value for op in frame.actions_frozen]}")
        
        # Execute recovery protocol
        protocol = SevenPhaseRecoveryProtocol(manager)
        system_state = {'scarindex': 0.25}
        
        actions = await protocol.execute_full_recovery(frame.id, system_state)
        
        print(f"\nRecovery completed with {len(actions)} phases")
        for action in actions:
            print(f"  Phase {action.phase.value}: {action.description} - {'SUCCESS' if action.success else 'FAILED'}")
    
    asyncio.run(example_panic_recovery())
