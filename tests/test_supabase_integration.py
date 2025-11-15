import asyncio
from pathlib import Path
import sys
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

sys.path.append(str(Path(__file__).resolve().parents[1]))

from core.config import SupabaseSettings
from core.supabase_integration import PersistenceResponse, SupabaseClient


def test_insert_ache_event_returns_persistence_response(monkeypatch):
    async def _run() -> PersistenceResponse:
        mock_client = MagicMock()
        supabase = SupabaseClient(
            client=mock_client,
            settings=SupabaseSettings(
                url="https://example.supabase.co",
                service_role_key="service-key",
            ),
        )

        response_obj = SimpleNamespace(data=[{'id': 'evt-123', 'source': 'guardian'}], status_code=201, error=None)

        async def fake_execute(func, operation):
            return response_obj

        monkeypatch.setattr(supabase, '_ensure_client', lambda: mock_client)
        monkeypatch.setattr(supabase, '_execute_with_retry', fake_execute)

        return await supabase.insert_ache_event(
            source='guardian',
            content={'commit_id': 'abc'},
            ache_level=0.4,
            metadata={'region': 'ΔΩ'}
        )

    result = asyncio.run(_run())
    assert isinstance(result, PersistenceResponse)
    assert result.table == 'ache_events'
    assert result.inserted_id == 'evt-123'
    assert result.status_code == 201
    assert result.payload['source'] == 'guardian'


def test_insert_vaultnode_executes_retry_chain(monkeypatch):
    async def _run():
        mock_client = MagicMock()
        response_obj = SimpleNamespace(data=[{'id': 'vault-1'}], status_code=200, error=None)

        async def fake_execute(func, operation):
            assert operation == 'vaultnodes.insert'
            return func()

        table_builder = MagicMock()
        insert_builder = MagicMock()
        insert_builder.execute.return_value = response_obj
        table_builder.insert.return_value = insert_builder
        mock_client.table.return_value = table_builder

        supabase = SupabaseClient(
            client=mock_client,
            settings=SupabaseSettings(
                url="https://example.supabase.co",
                service_role_key="service-key",
            ),
        )
        monkeypatch.setattr(supabase, '_ensure_client', lambda: mock_client)
        monkeypatch.setattr(supabase, '_execute_with_retry', fake_execute)

        return await supabase.insert_vaultnode(
            node_type='scarindex',
            reference_id='scar-123',
            state_hash='hash',
            previous_hash=None,
            audit_log={'action': 'scarindex'}
        )

    result = asyncio.run(_run())
    assert result.inserted_id == 'vault-1'
    assert result.table == 'vaultnodes'


def test_execute_with_retry_records_panic_on_failure(monkeypatch):
    async def _run():
        supabase = SupabaseClient(
            client=MagicMock(),
            max_retries=1,
            settings=SupabaseSettings(
                url="https://example.supabase.co",
                service_role_key="service-key",
            ),
        )
        recorded = []

        monkeypatch.setattr(supabase, '_record_panic_frame', lambda operation, error: recorded.append((operation, str(error))))

        with pytest.raises(RuntimeError):
            await supabase._execute_with_retry(lambda: (_ for _ in ()).throw(RuntimeError('boom')), 'test.op')

        return recorded

    recorded = asyncio.run(_run())
    assert recorded[0][0] == 'test.op'
    assert 'boom' in recorded[0][1]
