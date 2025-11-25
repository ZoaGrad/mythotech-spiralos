import os
import json
from datetime import datetime, timezone
from pathlib import Path

import json
from datetime import datetime, timezone

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


def test_rhythm_check_healthy(monkeypatch, tmp_path):
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

    heartbeat_fixture = tmp_path / "hb.json"
    scarindex_fixture = tmp_path / "scar.json"

    heartbeat_fixture.write_text(
        json.dumps([{"timestamp": "2025-01-01T11:55:00Z"}])
    )
    scarindex_fixture.write_text(
        json.dumps(
            [
                {
                    "bridge_id": "bridge-alpha",
                    "timestamp": "2025-01-01T11:50:00Z",
                    "scar_value": 0.8,
                    "delta": 0.1,
                    "source": "telemetry_normalize",
                    "metadata": {},
                    "created_at": "2025-01-01T11:50:01Z",
                }
            ]
        )
    )

    exit_code, lines = run_pulse_check(
        env_path=env_path,
        require_supabase=False,
        rhythm_check=True,
        schema_drift_check=True,
        heartbeat_fixture=heartbeat_fixture,
        scarindex_fixture=scarindex_fixture,
        now=datetime(2025, 1, 1, 12, tzinfo=timezone.utc),
        emit=lambda _: None,
    )

    assert exit_code == 0
    assert any("Rhythm governance" in line for line in lines)
    assert any("schema matches" in line for line in lines)


def test_rhythm_check_stale_heartbeat(monkeypatch, tmp_path):
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

    heartbeat_fixture = tmp_path / "hb_stale.json"
    scarindex_fixture = tmp_path / "scar_fresh.json"

    heartbeat_fixture.write_text(
        json.dumps([{"timestamp": "2024-12-31T00:00:00Z"}])
    )
    scarindex_fixture.write_text(
        json.dumps(
            [
                {
                    "bridge_id": "bridge-alpha",
                    "timestamp": "2025-01-01T11:50:00Z",
                    "scar_value": 0.8,
                    "delta": 0.1,
                    "source": "telemetry_normalize",
                    "metadata": {},
                    "created_at": "2025-01-01T11:50:01Z",
                }
            ]
        )
    )

    exit_code, lines = run_pulse_check(
        env_path=env_path,
        require_supabase=False,
        rhythm_check=True,
        heartbeat_fixture=heartbeat_fixture,
        scarindex_fixture=scarindex_fixture,
        now=datetime(2025, 1, 1, 12, tzinfo=timezone.utc),
        emit=lambda _: None,
    )

    assert exit_code == 3
    assert any("Heartbeat rhythm stale" in line for line in lines)


def test_rhythm_schema_drift(monkeypatch, tmp_path):
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

    heartbeat_fixture = tmp_path / "hb_ok.json"
    scarindex_fixture = tmp_path / "scar_drift.json"

    heartbeat_fixture.write_text(json.dumps([{"timestamp": "2025-01-01T11:55:00Z"}]))
    scarindex_fixture.write_text(
        json.dumps([
            {
                "bridge_id": "bridge-alpha",
                "timestamp": "2025-01-01T11:50:00Z",
                "scar_value": 0.8,
                "delta": 0.1,
                "source": "telemetry_normalize",
                "metadata": {},
                "created_at": "2025-01-01T11:50:01Z",
                "unexpected": True,
            }
        ])
    )

    exit_code, lines = run_pulse_check(
        env_path=env_path,
        require_supabase=False,
        rhythm_check=True,
        schema_drift_check=True,
        heartbeat_fixture=heartbeat_fixture,
        scarindex_fixture=scarindex_fixture,
        now=datetime(2025, 1, 1, 12, tzinfo=timezone.utc),
        emit=lambda _: None,
    )

    assert exit_code == 5
    assert any("schema drift" in line for line in lines)
