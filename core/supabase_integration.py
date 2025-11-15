"""
Supabase Integration - C6 Ledger Storage

Integrates SpiralOS with Supabase backend for:
- Persistent storage of Ache events, ScarIndex calculations, and system state
- VaultNode ledger management
- Smart Contract transaction logging
- Real-time coherence monitoring
"""

import asyncio
import json
import logging
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Callable, Dict, List, Optional

from postgrest import APIError
from supabase import Client, create_client

from .scarindex import ScarIndexResult, CoherenceComponents, AcheMeasurement, ScarIndexOracle
from .panic_frames import PanicFrameEvent, PanicFrameManager
from .ache_pid_controller import PIDState
from .config import SupabaseSettings, get_supabase_settings


logger = logging.getLogger(__name__)


@dataclass
class PersistenceResponse:
    """Unified response for Supabase persistence operations."""

    table: str
    status_code: int
    inserted_id: Optional[str]
    payload: Dict[str, Any]


class SupabaseClient:
    """Client for interacting with Supabase backend resources."""

    def __init__(
        self,
        client: Optional[Client] = None,
        max_retries: int = 3,
        settings: Optional[SupabaseSettings] = None,
    ) -> None:
        """Initialize Supabase client with Guardian panic logging."""

        self._settings = settings
        self.client: Optional[Client] = client
        self.max_retries = max_retries
        self.panic_manager = PanicFrameManager()

    @property
    def settings(self) -> SupabaseSettings:
        """Lazily resolve Supabase settings to allow injection in tests."""

        if self._settings is None:
            self._settings = get_supabase_settings()
        return self._settings

    def _build_client(self) -> Optional[Client]:
        """Create a Supabase client from environment credentials."""

        url = str(self.settings.url)
        key = self.settings.service_role_key or self.settings.anon_key

        if not url or not key:
            logger.warning('Supabase credentials missing; persistence disabled')
            return None

        try:
            return create_client(url, key)
        except Exception as exc:  # pragma: no cover - external dependency
            logger.error('Failed to initialize Supabase client: %s', exc)
            return None

    def _ensure_client(self) -> Client:
        if not self.client:
            self.client = self._build_client()
        if not self.client:
            raise RuntimeError('Supabase client not configured')
        return self.client

    def _record_panic_frame(self, operation: str, error: Exception) -> None:
        """Log persistence failures through the PanicFrame pipeline."""

        metadata = {
            'operation': operation,
            'error': str(error),
            'timestamp': datetime.now(timezone.utc).isoformat()
        }
        self.panic_manager.store.insert_signal(
            level='CRITICAL',
            key='persistence.supabase_error',
            meta=metadata
        )

    def _handle_supabase_error(self, operation: str, error: Exception) -> None:
        logger.error('Supabase operation %s failed: %s', operation, error)
        self._record_panic_frame(operation, error)

    async def _execute_with_retry(
        self,
        func: Callable[[], Any],
        operation: str
    ) -> Any:
        attempt = 0
        delay = 0.5

        while True:
            try:
                result = await asyncio.to_thread(func)
                response_error = getattr(result, 'error', None)
                if response_error:
                    raise APIError(message=str(response_error))
                return result
            except Exception as exc:
                self._handle_supabase_error(operation, exc)
                attempt += 1
                if attempt >= self.max_retries:
                    raise
                await asyncio.sleep(delay)
                delay *= 2

    @staticmethod
    def _extract_first_row(result: Any) -> Dict[str, Any]:
        data = getattr(result, 'data', None)
        if isinstance(data, list) and data:
            return data[0]
        if isinstance(data, dict):
            return data
        return {}
    
    async def insert_ache_event(
        self,
        source: str,
        content: Dict,
        ache_level: float,
        metadata: Optional[Dict] = None
    ) -> PersistenceResponse:
        """Insert an Ache event into Supabase with retries and auditing."""

        client = self._ensure_client()
        payload = {
            'source': source or 'unknown',
            'source_id': content.get('commit_id'),
            'content': content or {},
            'ache_level': max(0.0, min(1.0, ache_level)),
            'metadata': metadata or {}
        }

        result = await self._execute_with_retry(
            lambda: client.table('ache_events').insert(payload).execute(),
            'ache_events.insert'
        )
        row = self._extract_first_row(result)
        return PersistenceResponse(
            table='ache_events',
            status_code=getattr(result, 'status_code', 200),
            inserted_id=row.get('id'),
            payload=row or payload
        )
    
    async def insert_scarindex_calculation(
        self,
        result: ScarIndexResult,
        ache_event_id: Optional[str] = None
    ) -> PersistenceResponse:
        """Insert a ScarIndex calculation row."""

        client = self._ensure_client()
        record = result.to_dict()
        if ache_event_id:
            record['ache_event_id'] = ache_event_id
        record['metadata'] = record.get('metadata', {})

        supabase_result = await self._execute_with_retry(
            lambda: client.table('scarindex_calculations').insert(record).execute(),
            'scarindex_calculations.insert'
        )
        row = self._extract_first_row(supabase_result)
        return PersistenceResponse(
            table='scarindex_calculations',
            status_code=getattr(supabase_result, 'status_code', 200),
            inserted_id=row.get('id'),
            payload=row or record
        )

    async def insert_verification_records(
        self,
        records: List[Dict]
    ) -> List[PersistenceResponse]:
        """Batch insert verification records."""

        if not records:
            return []

        client = self._ensure_client()
        result = await self._execute_with_retry(
            lambda: client.table('verification_records').insert(records).execute(),
            'verification_records.insert'
        )
        payloads = getattr(result, 'data', []) or []
        return [
            PersistenceResponse(
                table='verification_records',
                status_code=getattr(result, 'status_code', 200),
                inserted_id=row.get('id'),
                payload=row
            )
            for row in payloads
        ]

    async def process_commit_batch(
        self,
        commits: List[Dict[str, Any]]
    ) -> PersistenceResponse:
        """Invoke the process_push_batch RPC with retry semantics."""

        if not isinstance(commits, list) or not commits:
            raise ValueError('Commits payload is required for process_push_batch')

        client = self._ensure_client()
        result = await self._execute_with_retry(
            lambda: client.rpc('process_push_batch', {'commits': commits}).execute(),
            'process_push_batch.rpc'
        )
        payload = self._extract_first_row(result)
        return PersistenceResponse(
            table='process_push_batch',
            status_code=getattr(result, 'status_code', 200),
            inserted_id=payload.get('batch_id'),
            payload=payload or {'commits': len(commits)}
        )

    async def insert_panic_frame(
        self,
        event: PanicFrameEvent
    ) -> PersistenceResponse:
        """Insert a Panic Frame event into Supabase."""

        client = self._ensure_client()
        payload = event.to_dict()
        result = await self._execute_with_retry(
            lambda: client.table('panic_frames').insert(payload).execute(),
            'panic_frames.insert'
        )
        row = self._extract_first_row(result)
        return PersistenceResponse(
            table='panic_frames',
            status_code=getattr(result, 'status_code', 200),
            inserted_id=row.get('id'),
            payload=row or payload
        )

    async def update_pid_state(
        self,
        state: PIDState
    ) -> PersistenceResponse:
        """Upsert PID controller state."""

        client = self._ensure_client()
        payload = state.to_dict()
        result = await self._execute_with_retry(
            lambda: client.table('pid_controller_state').upsert(payload).execute(),
            'pid_controller_state.upsert'
        )
        row = self._extract_first_row(result)
        return PersistenceResponse(
            table='pid_controller_state',
            status_code=getattr(result, 'status_code', 200),
            inserted_id=row.get('id'),
            payload=row or payload
        )

    async def insert_vaultnode(
        self,
        node_type: str,
        reference_id: str,
        state_hash: str,
        previous_hash: Optional[str],
        audit_log: Dict,
        github_commit_sha: Optional[str] = None,
        github_path: Optional[str] = None
    ) -> PersistenceResponse:
        """Insert a VaultNode ledger entry."""

        client = self._ensure_client()
        record = {
            'node_type': node_type or 'unknown',
            'reference_id': reference_id or 'unknown',
            'state_hash': state_hash or '',
            'previous_hash': previous_hash,
            'audit_log': audit_log or {},
            'github_commit_sha': github_commit_sha,
            'github_path': github_path
        }

        result = await self._execute_with_retry(
            lambda: client.table('vaultnodes').insert(record).execute(),
            'vaultnodes.insert'
        )
        row = self._extract_first_row(result)
        return PersistenceResponse(
            table='vaultnodes',
            status_code=getattr(result, 'status_code', 200),
            inserted_id=row.get('id'),
            payload=row or record
        )

    async def insert_smart_contract_txn(
        self,
        txn_type: str,
        from_state: Optional[str],
        to_state: Optional[str],
        scarcoin_delta: Optional[float] = None,
        is_frozen: bool = False,
        frozen_by: Optional[str] = None
    ) -> PersistenceResponse:
        """Insert a smart contract transaction row."""

        client = self._ensure_client()
        record = {
            'txn_type': txn_type,
            'from_state': from_state,
            'to_state': to_state,
            'scarcoin_delta': scarcoin_delta,
            'is_valid': True,
            'is_frozen': is_frozen,
            'frozen_by': frozen_by,
            'metadata': {}
        }

        result = await self._execute_with_retry(
            lambda: client.table('smart_contract_txns').insert(record).execute(),
            'smart_contract_txns.insert'
        )
        row = self._extract_first_row(result)
        return PersistenceResponse(
            table='smart_contract_txns',
            status_code=getattr(result, 'status_code', 200),
            inserted_id=row.get('id'),
            payload=row or record
        )

    async def get_current_coherence_status(self) -> Optional[Dict]:
        """
        Get current system coherence status
        
        Returns:
            Current coherence status from v_system_coherence view
        """
        # This would query the v_system_coherence view
        # For now, return a placeholder
        return {
            'scarindex': 0.7,
            'coherence_status': 'STABLE',
            'active_panic_frames': 0
        }
    
    async def get_active_panic_frames(self) -> List[Dict]:
        """
        Get all active Panic Frames
        
        Returns:
            List of active Panic Frame records
        """
        # This would query the v_active_panic_frames view
        return []
    
    async def get_pid_current_state(self) -> Optional[Dict]:
        """
        Get current PID controller state
        
        Returns:
            Current PID state from v_pid_current_state view
        """
        # This would query the v_pid_current_state view
        return None


class GitHubIntegration:
    """
    GitHub Integration for VaultNode storage
    
    Stores audit logs and state snapshots in GitHub repository
    for immutable record-keeping.
    """
    
    def __init__(self, repo: str = "ZoaGrad/emotion-sdk-tuner-"):
        """
        Initialize GitHub integration
        
        Args:
            repo: GitHub repository in format "owner/repo"
        """
        self.repo = repo
    
    async def commit_vaultnode(
        self,
        vaultnode_data: Dict,
        file_path: str,
        commit_message: str
    ) -> str:
        """
        Commit a VaultNode to GitHub
        
        Args:
            vaultnode_data: VaultNode data to commit
            file_path: Path in repository
            commit_message: Commit message
            
        Returns:
            Commit SHA
        """
        # In production, this would use GitHub API
        # For now, return a placeholder SHA
        return "placeholder_commit_sha"
    
    async def create_audit_trail(
        self,
        scarindex_id: str,
        calculation_data: Dict
    ) -> Dict:
        """
        Create an audit trail entry in GitHub
        
        Args:
            scarindex_id: ID of ScarIndex calculation
            calculation_data: Full calculation data
            
        Returns:
            Audit trail metadata
        """
        file_path = f"audit_trail/{datetime.now(timezone.utc).strftime('%Y/%m/%d')}/{scarindex_id}.json"
        
        commit_sha = await self.commit_vaultnode(
            vaultnode_data=calculation_data,
            file_path=file_path,
            commit_message=f"Audit trail for ScarIndex {scarindex_id}"
        )
        
        return {
            'file_path': file_path,
            'commit_sha': commit_sha,
            'timestamp': datetime.now(timezone.utc).isoformat()
        }


class SpiralOSBackend:
    """
    Unified backend interface for SpiralOS
    
    Coordinates between Supabase storage and GitHub audit trails.
    """
    
    def __init__(self):
        self.supabase = SupabaseClient()
        self.github = GitHubIntegration()
    
    async def process_ache_event(
        self,
        source: str,
        content: Dict,
        ache_level: float,
        coherence_components: CoherenceComponents
    ) -> Dict:
        """
        Process a complete Ache event through the system
        
        This orchestrates:
        1. Store Ache event
        2. Calculate ScarIndex
        3. Create VaultNode
        4. Commit to GitHub
        5. Update PID controller
        
        Args:
            source: Source of Ache
            content: Ache content
            ache_level: Initial Ache level
            coherence_components: Calculated coherence scores
            
        Returns:
            Complete processing result
        """
        # 1. Store Ache event
        ache_event_response = await self.supabase.insert_ache_event(
            source=source,
            content=content,
            ache_level=ache_level
        )
        ache_event = ache_event_response.payload

        # 2. Calculate and store ScarIndex
        ache_measurement = AcheMeasurement(
            before=ache_level,
            after=ache_level * 0.5  # Simplified transmutation
        )
        
        c_i_list = [coherence_components.narrative, coherence_components.social, coherence_components.economic, coherence_components.technical]
        scarindex_result = ScarIndexOracle.calculate(
            N=len(c_i_list),
            c_i_list=c_i_list,
            p_i_avg=sum(c_i_list) / len(c_i_list),
            decays_count=0,
            ache=ache_measurement
        )
        
        scarindex_record_response = await self.supabase.insert_scarindex_calculation(
            result=scarindex_result,
            ache_event_id=ache_event_response.inserted_id
        )
        scarindex_record = scarindex_record_response.payload

        # 3. Create VaultNode
        import hashlib
        state_hash = hashlib.sha256(
            json.dumps(scarindex_record, sort_keys=True).encode()
        ).hexdigest()

        vaultnode_response = await self.supabase.insert_vaultnode(
            node_type='scarindex',
            reference_id=scarindex_result.id,
            state_hash=state_hash,
            previous_hash=None,  # Would link to previous VaultNode
            audit_log={
                'action': 'scarindex_calculation',
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'result': scarindex_record
            }
        )
        vaultnode = vaultnode_response.payload
        
        # 4. Commit to GitHub
        github_audit = await self.github.create_audit_trail(
            scarindex_id=scarindex_result.id,
            calculation_data=scarindex_record
        )
        
        # 5. Check for Panic Frame trigger
        panic_manager = PanicFrameManager()
        if panic_manager.should_trigger(scarindex_result.scarindex):
            panic_frame = panic_manager.trigger_panic_frame(
                scarindex=scarindex_result.scarindex,
                metadata={'scarindex_id': scarindex_result.id}
            )
            
            await self.supabase.insert_panic_frame(panic_frame)

        return {
            'ache_event': ache_event,
            'scarindex': scarindex_record,
            'vaultnode': vaultnode,
            'github_audit': github_audit,
            'scarindex_value': scarindex_result.scarindex,
            'is_valid_transmutation': scarindex_result.is_valid
        }
    
    async def get_system_status(self) -> Dict:
        """
        Get comprehensive system status
        
        Returns:
            System status including coherence, panic frames, and PID state
        """
        coherence = await self.supabase.get_current_coherence_status()
        panic_frames = await self.supabase.get_active_panic_frames()
        pid_state = await self.supabase.get_pid_current_state()
        
        return {
            'coherence': coherence,
            'active_panic_frames': len(panic_frames),
            'panic_frames': panic_frames,
            'pid_state': pid_state,
            'timestamp': datetime.now(timezone.utc).isoformat()
        }


# Example usage
async def example_ache_processing():
    """Example of processing an Ache event through the system"""
    backend = SpiralOSBackend()
    
    # Example Ache event
    result = await backend.process_ache_event(
        source='user_input',
        content={
            'type': 'feature_proposal',
            'description': 'Add real-time coherence monitoring dashboard'
        },
        ache_level=0.6,
        coherence_components=CoherenceComponents(
            narrative=0.8,
            social=0.7,
            economic=0.6,
            technical=0.9
        )
    )
    
    print("Ache Event Processed:")
    print(f"  ScarIndex: {result['scarindex_value']:.4f}")
    print(f"  Valid Transmutation: {result['is_valid_transmutation']}")
    print(f"  VaultNode Hash: {result['vaultnode']['state_hash'][:16]}...")
    print(f"  GitHub Commit: {result['github_audit']['commit_sha']}")
    
    return result


if __name__ == '__main__':
    asyncio.run(example_ache_processing())
