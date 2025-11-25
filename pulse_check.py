import json
import os
import pathlib
from datetime import datetime, timedelta, timezone
from typing import Callable, Iterable, List, Tuple

from dotenv import load_dotenv

from core.guardian.heartbeat_audit import audit_heartbeat_retention, normalize_records


LineEmitter = Callable[[str], None]


HEADER = "-" * 30


def emit_block(lines: Iterable[str], emit: LineEmitter) -> None:
    for line in lines:
        emit(line)


def run_pulse_check(
    env_path: pathlib.Path | str = pathlib.Path(".env"),
    *,
    require_supabase: bool = False,
    audit_heartbeats: bool = False,
    heartbeat_fixture: pathlib.Path | None = None,
    now: datetime | None = None,
    allowed_gap_minutes: int = 60,
    emit: LineEmitter | None = None,
) -> Tuple[int, List[str]]:
    """Run SpiralOS connectivity diagnostics.

    The check is intentionally safe-by-default: it avoids printing secrets and
    will only attempt a Supabase handshake when explicitly requested via
    ``require_supabase``.

    Args:
        env_path: Path to the environment file containing Supabase credentials.
        require_supabase: When ``True``, attempt to instantiate a Supabase
            client and optionally read the ``scar_index`` table.
        audit_heartbeats: When ``True``, run offline heartbeat retention checks
            against the provided fixture and optionally reconcile against
            live Supabase data.
        heartbeat_fixture: Optional path to a JSON fixture containing heartbeat
            records. Defaults to ``data/audit/heartbeat_retention.json``.
        now: Override the reference time used for the audit (useful for tests).
        allowed_gap_minutes: Maximum tolerated gap before reporting drift.
        emit: Optional callback to receive log lines (defaults to ``print``).

    Returns:
        A tuple of ``(exit_code, lines)`` where ``exit_code`` mirrors the process
        exit status (``0`` for success, non-zero for failures) and ``lines``
        contains the rendered log lines for inspection or testing.
    """

    env_path = pathlib.Path(env_path)
    output_lines: List[str] = []
    exit_code = 0
    reference_time = now or datetime.now(timezone.utc)

    def _emit(line: str) -> None:
        output_lines.append(line)
        (emit or print)(line)

    emit_block([
        HEADER,
        ">>> SYSTEM PULSE CHECK",
        HEADER,
        f"Current working directory: {os.getcwd()}",
        f".env file exists: {env_path.resolve()} -> {env_path.exists()}",
    ], _emit)

    # Avoid leaking secrets; only report presence of the file.
    load_dotenv(env_path)

    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")

    if not url or not key:
        emit_block([
            "❌ CRITICAL: .env keys are MISSING.",
            "   Action: Create a .env file with SUPABASE_URL and SUPABASE_KEY.",
            f"   SUPABASE_URL present: {bool(url)}",
            f"   SUPABASE_KEY present: {bool(key)}",
            HEADER,
        ], _emit)
        return 1, output_lines

    emit_block([
        "✅ Keys detected.",
        f"   Target: {url}",
    ], _emit)

    heartbeat_result = None

    if audit_heartbeats:
        fixture_path = heartbeat_fixture or pathlib.Path("data/audit/heartbeat_retention.json")
        try:
            records = json.loads(pathlib.Path(fixture_path).read_text())
        except FileNotFoundError:
            records = []
            _emit(f"⚠️  Heartbeat fixture missing: {fixture_path}")
        except json.JSONDecodeError as e:  # noqa: BLE001 - user-controlled fixture
            records = []
            _emit(f"⚠️  Heartbeat fixture unreadable: {e}")

        heartbeat_result = audit_heartbeat_retention(
            records,
            now=reference_time,
            allowed_gap_minutes=allowed_gap_minutes,
        )

        last_seen = heartbeat_result.get("last_seen")
        largest_gap = heartbeat_result.get("largest_gap_minutes")
        emit_block([
            "📡 Guardian heartbeat audit (offline)",
            f"   Records scanned: {heartbeat_result['count']}",
            f"   Last seen: {last_seen.isoformat() if last_seen else 'n/a'}",
            f"   Largest gap (min): {largest_gap}",
            f"   Allowed gap (min): {allowed_gap_minutes}",
            HEADER,
        ], _emit)

        if not heartbeat_result["is_healthy"]:
            exit_code = max(exit_code, 2)

    if not require_supabase:
        emit_block([
            "⚠️  Supabase handshake skipped (use --require-supabase to enable).",
            HEADER,
        ], _emit)
        return exit_code, output_lines

    try:
        from supabase import create_client  # Imported lazily to avoid hard dependency unless requested.

        _emit(">>> Attempting handshake with Supabase...")
        supabase = create_client(url, key)
        _emit("✅ Client created successfully.")

        try:
            supabase.table("scar_index").select("*").limit(1).execute()
            emit_block([
                "✅ DATABASE READ: SUCCESS.",
                "   The Golem is AWAKE.",
            ], _emit)
        except Exception as db_e:  # noqa: BLE001 - capture and report operational DB errors.
            emit_block([
                f"⚠️  Auth worked, but table read failed: {db_e}",
                "   (Connected but the table may be missing/empty.)",
            ], _emit)

        if audit_heartbeats:
            try:
                response = (
                    supabase.table("guardian_heartbeats")
                    .select("created_at")
                    .order("created_at", desc=True)
                    .limit(1)
                    .execute()
                )
                online_records = normalize_records(response.data or [])
                online_last = online_records[-1] if online_records else None

                if online_last:
                    delta = None
                    if heartbeat_result and heartbeat_result.get("last_seen"):
                        delta = (online_last - heartbeat_result["last_seen"]) / timedelta(minutes=1)  # type: ignore[index]

                    emit_block([
                        "🌐 Supabase heartbeat reconciliation",
                        f"   Latest online heartbeat: {online_last.isoformat()}",
                        (
                            f"   Online/offline drift (min): {delta:.2f}"
                            if delta is not None
                            else "   Drift: unavailable (offline fixture missing)"
                        ),
                    ], _emit)
            except Exception as hb_e:  # noqa: BLE001 - reconcile errors are informational
                emit_block([
                    f"⚠️  Heartbeat reconciliation failed: {hb_e}",
                    "   Proceeding with offline audit results only.",
                ], _emit)
    except Exception as e:  # noqa: BLE001 - top-level guard for connectivity failures.
        emit_block([
            f"❌ CONNECTION FAILED: {e}",
            HEADER,
        ], _emit)
        return 2, output_lines

    _emit(HEADER)
    return exit_code, output_lines


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="SpiralOS pulse check")
    parser.add_argument(
        "--env-path",
        type=pathlib.Path,
        default=pathlib.Path(".env"),
        help="Path to the .env file containing SUPABASE_URL and SUPABASE_KEY",
    )
    parser.add_argument(
        "--require-supabase",
        action="store_true",
        help="Attempt a live Supabase handshake (may require network access)",
    )
    parser.add_argument(
        "--audit-heartbeats",
        action="store_true",
        help="Run offline heartbeat retention checks and reconcile online data when available",
    )
    parser.add_argument(
        "--heartbeat-fixture",
        type=pathlib.Path,
        default=None,
        help="Override the default heartbeat fixture path",
    )
    parser.add_argument(
        "--allowed-gap-minutes",
        type=int,
        default=60,
        help="Maximum tolerated gap/age before the audit reports drift",
    )

    args = parser.parse_args()
    exit_code, _ = run_pulse_check(
        env_path=args.env_path,
        require_supabase=args.require_supabase,
        audit_heartbeats=args.audit_heartbeats,
        heartbeat_fixture=args.heartbeat_fixture,
        allowed_gap_minutes=args.allowed_gap_minutes,
    )
    raise SystemExit(exit_code)


if __name__ == "__main__":
    main()
