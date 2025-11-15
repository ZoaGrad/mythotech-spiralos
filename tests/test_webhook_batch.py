import asyncio
import sys
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from core.config import SupabaseSettings
from core.supabase_integration import SupabaseClient


def test_process_commit_batch_single(monkeypatch):
    mock_client = MagicMock()
    response_obj = SimpleNamespace(data=[{"batch_id": "batch-1", "commits_processed": 1}], status_code=201, error=None)
    rpc_builder = MagicMock()
    rpc_builder.execute.return_value = response_obj
    mock_client.rpc.return_value = rpc_builder

    supabase = SupabaseClient(
        client=mock_client,
        settings=SupabaseSettings(url="https://example.supabase.co", service_role_key="service-key"),
    )

    async def fake_retry(func, operation):
        assert operation == 'process_push_batch.rpc'
        return func()

    monkeypatch.setattr(supabase, '_execute_with_retry', fake_retry)
    monkeypatch.setattr(supabase, '_ensure_client', lambda: mock_client)

    result = asyncio.run(supabase.process_commit_batch([{"id": "abc", "message": "fix"}]))
    mock_client.rpc.assert_called_once_with('process_push_batch', {'commits': [{'id': 'abc', 'message': 'fix'}]})
    assert result.table == 'process_push_batch'
    assert result.payload['batch_id'] == 'batch-1'


def test_process_commit_batch_handles_many_commits(monkeypatch):
    mock_client = MagicMock()
    response_obj = SimpleNamespace(data=[{"batch_id": "batch-many", "commits_processed": 3}], status_code=200, error=None)
    rpc_builder = MagicMock()
    rpc_builder.execute.return_value = response_obj
    mock_client.rpc.return_value = rpc_builder

    supabase = SupabaseClient(
        client=mock_client,
        settings=SupabaseSettings(url="https://example.supabase.co", service_role_key="service-key"),
    )

    async def fake_retry(func, operation):
        return func()

    monkeypatch.setattr(supabase, '_execute_with_retry', fake_retry)
    monkeypatch.setattr(supabase, '_ensure_client', lambda: mock_client)

    commits = [
        {"id": "c1", "message": "m1"},
        {"id": "c2", "message": "m2"},
        {"id": "c3", "message": "m3"},
    ]
    result = asyncio.run(supabase.process_commit_batch(commits))
    assert result.payload['commits_processed'] == 3


def test_process_commit_batch_rejects_invalid_payload():
    supabase = SupabaseClient(
        client=MagicMock(),
        settings=SupabaseSettings(url="https://example.supabase.co", service_role_key="service-key"),
    )

    with pytest.raises(ValueError):
        asyncio.run(supabase.process_commit_batch([]))

    with pytest.raises(ValueError):
        asyncio.run(supabase.process_commit_batch(None))  # type: ignore[arg-type]
