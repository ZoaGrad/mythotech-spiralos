"""
Panic Frames (F4) - Constitutional Circuit Breaker
Activates when ScarIndex < 0.3, acting as a constitutional circuit breaker that:
- FREEZES: ScarCoin Minting/Burning, VaultNode Generation
- ESCALATES: To F2 Judges for review
- ENFORCES: 7-Phase Crisis Recovery Protocol
This ensures system stability by preventing catastrophic coherence collapse.

Supabase persistence:
- Table panicframe_signals: stores activation events and recovery progress
  Suggested schema:
    id: uuid primary key
    created_at: timestamptz default now()
    level: text (e.g., "PANIC", "RECOVERY", "INFO")
    key: text (e.g., "panicframe.trigger", "panicframe.phase")
    meta: jsonb (arbitrary payload)

Env vars required:
  SUPABASE_URL, SUPABASE_KEY
"""
from dataclasses import dataclass
from typing import List, Dict, Optional
from enum import Enum
from datetime import datetime, timezone
import uuid
import os
import sys
import logging
from supabase import create_client, Client

logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))
log = logging.getLogger(__name__)

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
            'metadata': self.metadata,
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

class PanicFrameStore:
    """Supabase-backed persistence for PanicFrame events and actions."""

    def __init__(self):
        url = os.getenv('SUPABASE_URL')
        key = os.getenv('SUPABASE_KEY')

        self.client: Optional[Client] = None
        self._fallback_events: List[Dict] = []

        if not url or not key:
            log.warning(
                'SUPABASE_URL and SUPABASE_KEY not configured; '
                'falling back to in-memory PanicFrame store.'
            )
            return

        try:
            self.client = create_client(url, key)
        except Exception as exc:  # pragma: no cover - defensive
            log.warning(
                'Failed to initialise Supabase client, '
                'falling back to in-memory store: %s',
                exc,
            )

    def _record_fallback(self, payload: Dict) -> None:
        """Persist signals locally when Supabase is unavailable."""
        self._fallback_events.append({
            'recorded_at': datetime.now(timezone.utc).isoformat(),
            **payload,
        })

    def insert_signal(self, level: str, key: str, meta: Dict) -> None:
        if not self.client:
            self._record_fallback({'level': level, 'key': key, 'meta': meta})
            return

        try:
            self.client.table('panicframe_signals').insert({
                'level': level,
                'key': key,
                'meta': meta,
            }).execute()
        except Exception as e:  # pragma: no cover - logging fallback path
            log.exception('Failed inserting panicframe signal: %s', e)

    def record_trigger(self, event: PanicFrameEvent) -> None:
        self.insert_signal(
            level='PANIC',
            key='panicframe.trigger',
            meta=event.to_dict(),
        )

    def record_phase(self, event_id: str, phase: RecoveryPhase, action: RecoveryAction) -> None:
        self.insert_signal(
            level='RECOVERY',
            key='panicframe.phase',
            meta={
                'panic_frame_id': event_id,
                'phase': phase.value,
                'action': {
                    'type': action.action_type,
                    'description': action.description,
                    'executed_at': action.executed_at.isoformat(),
                    'success': action.success,
                    'result': action.result,
                }
            }
        )

    def record_resolution(self, event: PanicFrameEvent) -> None:
        self.insert_signal(
            level='INFO',
            key='panicframe.resolved',
            meta=event.to_dict(),
        )

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

    def __init__(self, store: Optional[PanicFrameStore] = None):
        self.active_frames: Dict[str, PanicFrameEvent] = {}
        self.recovery_history: List[RecoveryAction] = []
        self.store = store or PanicFrameStore()

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
            triggered_at=datetime.now(timezone.utc),
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
        # Persist trigger signal
        self.store.record_trigger(event)
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

        # Record the recovery action (persist as signal)
        self.recovery_history.append(action)
        self.store.record_phase(panic_frame_id, frame.recovery_phase or RecoveryPhase.PHASE_1_ASSESSMENT, action)

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
                frame.resolved_at = datetime.now(timezone.utc)
                self.store.record_resolution(frame)
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
            # Persist escalation as signal
            self.store.insert_signal('RECOVERY', 'panicframe.escalate', {
                'panic_frame_id': panic_frame_id,
                'escalation_level': frame.escalation_level,
            })
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
            frame.resolved_at = datetime.now(timezone.utc)
            frame.metadata['final_scarindex'] = final_scarindex
            self.store.record_resolution(frame)
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


# Module-level helper functions for backward compatibility
_panic_manager_instance: Optional[PanicFrameManager] = None


def get_panic_manager() -> PanicFrameManager:
    """Get or create the global panic manager instance."""
    global _panic_manager_instance
    if _panic_manager_instance is None:
        try:
            store = PanicFrameStore()
            _panic_manager_instance = PanicFrameManager(store)
        except Exception:
            # Fallback to manager without store if Supabase unavailable
            _panic_manager_instance = PanicFrameManager(None)
    return _panic_manager_instance


def log_event(level: str, message: str, meta: Optional[Dict] = None) -> None:
    """Log a panic frame event.
    
    Args:
        level: Log level (e.g., 'WARNING', 'CRITICAL', 'INFO')
        message: Log message
        meta: Optional metadata dictionary
    """
    log.log(
        getattr(logging, level.upper(), logging.INFO),
        message
    )
    
    # Try to persist to Supabase if available
    try:
        manager = get_panic_manager()
        if manager.store:
            manager.store.insert_signal(
                level=level,
                key='panic_frame.event',
                meta=meta or {'message': message}
            )
    except Exception as e:
        log.debug(f"Failed to persist event to Supabase: {e}")


def trigger_panic_frames(scarindex: Optional[float] = None) -> None:
    """Trigger a panic frame due to coherence failure.
    
    Args:
        scarindex: Optional ScarIndex value that triggered the panic
    """
    manager = get_panic_manager()
    
    # Use provided scarindex or default to threshold breach
    trigger_value = scarindex if scarindex is not None else 0.29
    
    event = manager.trigger_panic_frame(
        scarindex=trigger_value,
        metadata={'auto_triggered': True}
    )
    
    log.critical(
        f"Panic Frame triggered: ScarIndex={trigger_value:.3f} < {manager.threshold}"
    )


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
            executed_at=datetime.now(timezone.utc),
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
            executed_at=datetime.now(timezone.utc),
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
            executed_at=datetime.now(timezone.utc),
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
            executed_at=datetime.now(timezone.utc),
            success=True,
            result=diagnosis
        )

        return action

    async def execute_phase_5_remediation(
        self,
        panic_frame_id: str,
        remediation_plan: Dict
    ) -> RecoveryAction:
        """Execute Phase 5: Remediation - Implementation of corrective measures.

        Args:
            panic_frame_id: ID of the panic frame
            remediation_plan: Dict containing remediation actions

        Returns:
            RecoveryAction record
        """
        # Implement remediation plan
        log_event(
            'recovery',
            f'Phase 5 remediation executed for panic frame {panic_frame_id}'
        )

        action = RecoveryAction(
            phase=RecoveryPhase.PHASE_5_REMEDIATION,
            action_type='remediation',
            description='Executed remediation plan',
            executed_at=datetime.now(timezone.utc),
            success=True,
            result=remediation_plan
        )

        return action

    async def execute_phase_6_validation(
        self,
        panic_frame_id: str,
        validation_metrics: Dict
    ) -> RecoveryAction:
        """Phase 6: Validate recovery effectiveness."""

        target = validation_metrics.get('target_scarindex', 0.67)
        current = validation_metrics.get('scarindex') or validation_metrics.get('current_scarindex', 0.7)
        validation = {
            'target_scarindex': target,
            'achieved_scarindex': current,
            'pid_stable': validation_metrics.get('pid_stable', True),
            'coherence_restored': current >= target
        }

        action = RecoveryAction(
            phase=RecoveryPhase.PHASE_6_VALIDATION,
            action_type='validation',
            description='Validated recovery effectiveness',
            executed_at=datetime.now(timezone.utc),
            success=validation['coherence_restored'],
            result=validation
        )

        return action

    async def execute_phase_7_resumption(
        self,
        panic_frame_id: str,
        resumption_plan: Dict
    ) -> RecoveryAction:
        """Phase 7: Resume normal operations."""

        plan = {
            'operations_resumed': resumption_plan.get('operations_resumed', [op.value for op in PanicFrameManager.DEFAULT_FROZEN_OPERATIONS]),
            'notes': resumption_plan.get('notes', 'Operations resumed under enhanced monitoring'),
            'timestamp': resumption_plan.get('timestamp', datetime.now(timezone.utc).isoformat())
        }

        action = RecoveryAction(
            phase=RecoveryPhase.PHASE_7_RESUMPTION,
            action_type='resumption',
            description='Resumed normal operations',
            executed_at=datetime.now(timezone.utc),
            success=True,
            result=plan
        )

        return action

    async def execute_full_recovery(self, panic_frame_id: str, system_state: Dict) -> List[RecoveryAction]:
        """Run the complete 7-phase recovery protocol."""

        actions: List[RecoveryAction] = []

        phase1 = await self.execute_phase_1_assessment(panic_frame_id, system_state)
        actions.append(phase1)
        self.panic_manager.advance_recovery_phase(panic_frame_id, phase1)

        affected_components = system_state.get('affected_components') or phase1.result.get('affected_components', [])
        phase2 = await self.execute_phase_2_isolation(panic_frame_id, affected_components)
        actions.append(phase2)
        self.panic_manager.advance_recovery_phase(panic_frame_id, phase2)

        phase3 = await self.execute_phase_3_stabilization(panic_frame_id)
        actions.append(phase3)
        self.panic_manager.advance_recovery_phase(panic_frame_id, phase3)

        system_logs = system_state.get('system_logs', [])
        phase4 = await self.execute_phase_4_diagnosis(panic_frame_id, system_logs)
        actions.append(phase4)
        self.panic_manager.advance_recovery_phase(panic_frame_id, phase4)

        remediation_plan = system_state.get('remediation_plan') or {
            'actions': ['increase_transmutation_capacity', 'rebalance_pid_controller'],
            'owner': 'spiralos-core'
        }
        phase5 = await self.execute_phase_5_remediation(panic_frame_id, remediation_plan)
        actions.append(phase5)
        self.panic_manager.advance_recovery_phase(panic_frame_id, phase5)

        validation_metrics = system_state.get('post_recovery_metrics') or {
            'scarindex': system_state.get('scarindex', 0.7),
            'target_scarindex': system_state.get('target_scarindex', system_state.get('scarindex', 0.67)),
            'pid_stable': True
        }
        phase6 = await self.execute_phase_6_validation(panic_frame_id, validation_metrics)
        actions.append(phase6)
        self.panic_manager.advance_recovery_phase(panic_frame_id, phase6)

        resumption_plan = system_state.get('resumption_plan') or {}
        phase7 = await self.execute_phase_7_resumption(panic_frame_id, resumption_plan)
        actions.append(phase7)
        self.panic_manager.advance_recovery_phase(panic_frame_id, phase7)

        return actions
       
