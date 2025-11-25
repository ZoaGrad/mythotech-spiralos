import os
import pathlib
from typing import Callable, Iterable, List, Tuple

from dotenv import load_dotenv


LineEmitter = Callable[[str], None]


HEADER = "-" * 30


def emit_block(lines: Iterable[str], emit: LineEmitter) -> None:
    for line in lines:
        emit(line)


def run_pulse_check(
    env_path: pathlib.Path | str = pathlib.Path(".env"),
    *,
    require_supabase: bool = False,
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
        emit: Optional callback to receive log lines (defaults to ``print``).

    Returns:
        A tuple of ``(exit_code, lines)`` where ``exit_code`` mirrors the process
        exit status (``0`` for success, non-zero for failures) and ``lines``
        contains the rendered log lines for inspection or testing.
    """

    env_path = pathlib.Path(env_path)
    output_lines: List[str] = []

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

    if not require_supabase:
        emit_block([
            "⚠️  Supabase handshake skipped (use --require-supabase to enable).",
            HEADER,
        ], _emit)
        return 0, output_lines

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
    except Exception as e:  # noqa: BLE001 - top-level guard for connectivity failures.
        emit_block([
            f"❌ CONNECTION FAILED: {e}",
            HEADER,
        ], _emit)
        return 2, output_lines

    _emit(HEADER)
    return 0, output_lines


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

    args = parser.parse_args()
    exit_code, _ = run_pulse_check(
        env_path=args.env_path,
        require_supabase=args.require_supabase,
    )
    raise SystemExit(exit_code)


if __name__ == "__main__":
    main()
