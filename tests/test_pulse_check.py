import os
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
