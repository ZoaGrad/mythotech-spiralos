import importlib
import sys
import time
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

import pytest
from fastapi.testclient import TestClient
from jose import jwt

from core.config import reset_settings_cache


def build_payload(suffix: str = "1") -> dict:
    return {
        "transmutation_id": f"transmutation-{suffix}",
        "scarindex_before": 0.2,
        "scarindex_after": 0.5,
        "transmutation_efficiency": 0.9,
        "owner_address": "guardian-wallet",
        "oracle_signatures": ["sig-1", "sig-2"],
    }


@pytest.fixture()
def guardian_client(monkeypatch):
    monkeypatch.setenv("GUARDIAN_API_KEYS", '["test-key"]')
    monkeypatch.setenv("GUARDIAN_JWT_SECRET", "super-secret")
    monkeypatch.setenv("GUARDIAN_ALLOWED_ORIGINS", '["https://spiralos.io"]')
    monkeypatch.setenv("GUARDIAN_RATE_LIMIT_PER_MINUTE", "2")
    monkeypatch.setenv("GUARDIAN_RATE_WINDOW_SECONDS", "60")
    reset_settings_cache()
    module = importlib.reload(importlib.import_module("holoeconomy.scarcoin_bridge_api"))
    module._guardian_rate_state.clear()
    client = TestClient(module.app)
    token = jwt.encode({"sub": "guardian", "role": "guardian"}, "super-secret", algorithm="HS256")
    yield module, client, token
    module._guardian_rate_state.clear()
    reset_settings_cache()


def test_missing_guardian_headers_rejected(guardian_client):
    _, client, _ = guardian_client
    response = client.post("/api/v1/scarcoin/mint", json=build_payload())
    assert response.status_code == 401
    assert "X-Guardian-Key" in response.json()["detail"]


def test_invalid_jwt_rejected(guardian_client):
    _, client, _ = guardian_client
    response = client.post(
        "/api/v1/scarcoin/mint",
        json=build_payload(),
        headers={"X-Guardian-Key": "test-key", "Authorization": "Bearer broken"},
    )
    assert response.status_code == 401


def test_expired_jwt_rejected(guardian_client):
    _, client, _ = guardian_client
    expired_token = jwt.encode(
        {"sub": "guardian", "role": "guardian", "exp": int(time.time()) - 10},
        "super-secret",
        algorithm="HS256",
    )
    response = client.post(
        "/api/v1/scarcoin/mint",
        json=build_payload("expired"),
        headers={
            "X-Guardian-Key": "test-key",
            "Authorization": f"Bearer {expired_token}",
        },
    )
    assert response.status_code == 401


def test_valid_guardian_request_succeeds(guardian_client):
    _, client, token = guardian_client
    response = client.post(
        "/api/v1/scarcoin/mint",
        json=build_payload("valid"),
        headers={
            "X-Guardian-Key": "test-key",
            "Authorization": f"Bearer {token}",
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True


def test_rate_limit_enforced(guardian_client):
    module, client, token = guardian_client
    for attempt in range(2):
        response = client.post(
            "/api/v1/scarcoin/mint",
            json=build_payload(str(attempt)),
            headers={
                "X-Guardian-Key": "test-key",
                "Authorization": f"Bearer {token}",
            },
        )
        assert response.status_code == 200

    third_response = client.post(
        "/api/v1/scarcoin/mint",
        json=build_payload("limit"),
        headers={
            "X-Guardian-Key": "test-key",
            "Authorization": f"Bearer {token}",
        },
    )
    assert third_response.status_code == 429
    module._guardian_rate_state.clear()
