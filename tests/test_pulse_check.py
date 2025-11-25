import os
import json
from datetime import datetime, timezone
from pathlib import Path

from pulse_check import run_pulse_check


def test_missing_env_keys(monkeypatch, tmp_path):
    # Ensure environment variables are absent so the check reads from the provided file.
    for var in ("SUPABASE_URL", "SUPABASE_KEY"):
        monkeypatch.delenv(var, raising=False)

    env_path = tmp_path / "local.env"

    exit_code, lines = run_pulse_check(env_path=env_path, emit=lambda _: None)

    assert exit_code == 1
    assert any("keys are MISSING" in line for line in lines)


def test_skip_handshake_when_not_required(monkeypatch, tmp_path):
    env_path = tmp_path / "local.env"
    env_path.write_text(
        "\n".join(
            [
                "SUPABASE_URL=https://example.supabase.co",
                "SUPABASE_KEY=anon-key",
            ]
        )
    )

    for var in ("SUPABASE_URL", "SUPABASE_KEY"):
        monkeypatch.delenv(var, raising=False)

    exit_code, lines = run_pulse_check(
        env_path=env_path,
        require_supabase=False,
        emit=lambda _: None,
    )

    assert exit_code == 0
    assert any("handshake skipped" in line for line in lines)
    assert any("Keys detected" in line for line in lines)
    # Ensure the Supabase target string is surfaced for observability
    assert any("example.supabase.co" in line for line in lines)


def test_heartbeat_audit_offline(monkeypatch, tmp_path):
    env_path = tmp_path / "local.env"
    env_path.write_text(
        "\n".join(
            [
                "SUPABASE_URL=https://example.supabase.co",
                "SUPABASE_KEY=anon-key",
            ]
        )
    )

    for var in ("SUPABASE_URL", "SUPABASE_KEY"):
        monkeypatch.delenv(var, raising=False)

    fixture = tmp_path / "heartbeat.json"
    fixture.write_text(
        json.dumps(
            [
                {"created_at": "2025-01-01T00:00:00Z"},
                {"created_at": "2025-01-01T05:00:00Z"},
            ]
        )
    )

    exit_code, lines = run_pulse_check(
        env_path=env_path,
        require_supabase=False,
        audit_heartbeats=True,
        heartbeat_fixture=fixture,
        allowed_gap_minutes=360,
        now=datetime(2025, 1, 1, 6, tzinfo=timezone.utc),
        emit=lambda _: None,
    )

    assert exit_code == 0
    assert any("Guardian heartbeat audit" in line for line in lines)
    assert any("Records scanned: 2" in line for line in lines)


def test_heartbeat_audit_flags_stale(monkeypatch, tmp_path):
    env_path = tmp_path / "local.env"
    env_path.write_text(
        "\n".join(
            [
                "SUPABASE_URL=https://example.supabase.co",
                "SUPABASE_KEY=anon-key",
            ]
        )
    )

    for var in ("SUPABASE_URL", "SUPABASE_KEY"):
        monkeypatch.delenv(var, raising=False)

    fixture = tmp_path / "stale_heartbeat.json"
    fixture.write_text(json.dumps([{"created_at": "2024-12-31T00:00:00Z"}]))

    exit_code, lines = run_pulse_check(
        env_path=env_path,
        require_supabase=False,
        audit_heartbeats=True,
        heartbeat_fixture=fixture,
        allowed_gap_minutes=10,
        now=datetime(2025, 1, 1, tzinfo=timezone.utc),
        emit=lambda _: None,
    )

    assert exit_code == 2
    assert any("Records scanned" in line for line in lines)
