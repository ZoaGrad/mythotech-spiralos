"""Shared pytest fixtures for isolating Supabase and Guardian dependencies."""

from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Generator
from unittest.mock import MagicMock

import pytest

REPO_ROOT = Path(__file__).resolve().parent
SRC_PATH = REPO_ROOT / "src"

if str(SRC_PATH) not in sys.path:
    sys.path.append(str(SRC_PATH))

try:
    from core.config import reset_settings_cache
except ModuleNotFoundError:  # pragma: no cover - fallback when executed directly
    if str(REPO_ROOT) not in sys.path:
        sys.path.append(str(REPO_ROOT))
    from core.config import reset_settings_cache

DEFAULT_TEST_ENV = {
    "SUPABASE_URL": "http://localhost:54321",
    "SUPABASE_SERVICE_ROLE_KEY": "supabase-service-role-test-key",
    "SUPABASE_ANON_KEY": "supabase-anon-test-key",
    "GUARDIAN_API_KEYS": '["test-key"]',
    "GUARDIAN_JWT_SECRET": "guardian-test-secret",
    "GUARDIAN_ALLOWED_ORIGINS": '["https://spiralos.io"]',
}

for key, value in DEFAULT_TEST_ENV.items():
    os.environ.setdefault(key, value)

_GLOBAL_SUPABASE_CLIENT = MagicMock(name="SupabaseClientStubGlobal")


def _fake_create_client(*args, **kwargs):  # pragma: no cover - helper
    return _GLOBAL_SUPABASE_CLIENT


try:
    import supabase

    supabase.create_client = _fake_create_client
    if hasattr(supabase, "client"):
        supabase.client.create_client = _fake_create_client  # type: ignore[attr-defined]
except ModuleNotFoundError:  # pragma: no cover - dependency optional in docs builds
    pass


@pytest.fixture(autouse=True)
def stub_external_services(monkeypatch: pytest.MonkeyPatch) -> Generator[MagicMock, None, None]:
    """Provide deterministic environment defaults and stub Supabase client creation."""

    monkeypatch.setenv("SUPABASE_URL", "http://localhost:54321")
    monkeypatch.setenv("SUPABASE_SERVICE_ROLE_KEY", "supabase-service-role-test-key")
    monkeypatch.setenv("SUPABASE_ANON_KEY", "supabase-anon-test-key")
    monkeypatch.setenv("GUARDIAN_API_KEYS", '["test-key"]')
    monkeypatch.setenv("GUARDIAN_JWT_SECRET", "guardian-test-secret")
    monkeypatch.setenv("GUARDIAN_ALLOWED_ORIGINS", '["https://spiralos.io"]')

    reset_settings_cache()

    stub_client = MagicMock(name="SupabaseClientStub")

    def _fake_create_client(url: str, key: str) -> MagicMock:  # pragma: no cover - helper
        stub_client.supabase_url = url
        stub_client.supabase_key = key
        return stub_client

    monkeypatch.setattr("core.supabase_integration.create_client", _fake_create_client)

    yield stub_client

    reset_settings_cache()
