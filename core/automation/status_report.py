"""Status Report Automation.

Generates a consolidated status report from Supabase data including:
- Judge workloads and availability
- Case assignment stats
- PanicFrame signals summary

Usage:
    python -m core.automation.status_report --out reports/status_YYYYMMDD.json

Environment Variables:
    SUPABASE_URL: Supabase project URL
    SUPABASE_KEY: Supabase API key
    LOG_LEVEL: Logging level (default: INFO)
"""

import json
import logging
import os
import sys
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional

from supabase import create_client

# Configure logging
logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"), format="%(asctime)s - %(levelname)s - %(message)s")
log = logging.getLogger(__name__)


class StatusReportGenerator:
    """Generates consolidated status reports from Supabase data."""

    def __init__(self):
        """Initialize Supabase client."""
        self.supabase_url = os.getenv("SUPABASE_URL")
        self.supabase_key = os.getenv("SUPABASE_KEY")

        if not self.supabase_url or not self.supabase_key:
            log.error("SUPABASE_URL and SUPABASE_KEY environment variables are required.")
            sys.exit(1)

        try:
            self.supabase = create_client(self.supabase_url, self.supabase_key)
            log.info("Supabase client initialized successfully")
        except Exception as e:
            log.error(f"Failed to initialize Supabase client: {e}")
            sys.exit(1)

    def fetch_judge_summary(self) -> List[Dict[str, Any]]:
        """Fetch judge workload and availability summary.

        Returns:
            List of judge capacity records
        """
        try:
            response = (
                self.supabase.table("judges")
                .select("id, name, current_workload, max_workload, status, specialization")
                .execute()
            )

            judge_capacity = []
            for judge in response.data:
                max_workload = judge.get("max_workload", 20)
                current_workload = judge.get("current_workload", 0)
                available_slots = max(max_workload - current_workload, 0)

                judge_capacity.append(
                    {
                        "id": judge.get("id"),
                        "name": judge.get("name"),
                        "current_workload": current_workload,
                        "max_workload": max_workload,
                        "available_slots": available_slots,
                        "utilization_percent": ((current_workload / max_workload * 100) if max_workload > 0 else 0),
                        "status": judge.get("status", "unknown"),
                        "specialization": judge.get("specialization", []),
                    }
                )

            log.info(f"Fetched summary for {len(judge_capacity)} judges")
            return judge_capacity
        except Exception as e:
            log.error(f"Error fetching judge summary: {e}")
            return []

    def fetch_case_statistics(self) -> Dict[str, Any]:
        """Fetch case assignment statistics from Supabase.

        Returns:
            Dictionary with case statistics
        """
        try:
            # Get all cases
            all_cases = self.supabase.table("cases").select("id, status, assigned_judge_id").execute()

            total_cases = len(all_cases.data)
            open_cases = sum(1 for case in all_cases.data if case.get("status") != "closed")
            unassigned_cases = sum(
                1 for case in all_cases.data if not case.get("assigned_judge_id") and case.get("status") != "closed"
            )
            closed_cases = sum(1 for case in all_cases.data if case.get("status") == "closed")

            # Get case breakdown by status
            status_breakdown = {}
            for case in all_cases.data:
                status = case.get("status", "unknown")
                status_breakdown[status] = status_breakdown.get(status, 0) + 1

            stats = {
                "total": total_cases,
                "open": open_cases,
                "closed": closed_cases,
                "unassigned": unassigned_cases,
                "assigned": total_cases - unassigned_cases - closed_cases,
                "status_breakdown": status_breakdown,
            }

            log.info(f"Case statistics: {stats}")
            return stats
        except Exception as e:
            log.error(f"Error fetching case statistics: {e}")
            return {"total": 0, "open": 0, "closed": 0, "unassigned": 0, "assigned": 0, "status_breakdown": {}}

    def fetch_panicframe_signals(self) -> Dict[str, Any]:
        """Fetch PanicFrame signal summary from Supabase.

        Returns:
            Dictionary with signal statistics
        """
        try:
            now = datetime.now(timezone.utc)
            hour_ago = (now - timedelta(hours=1)).isoformat()
            day_ago = (now - timedelta(days=1)).isoformat()

            # Get all signals
            all_signals = self.supabase.table("panicframe_signals").select("id, created_at, level, key, meta").execute()

            signals_last_hour = 0
            signals_last_24h = 0
            signal_levels = {}

            for signal in all_signals.data:
                created_at = signal.get("created_at")
                level = signal.get("level", "unknown")

                if created_at >= hour_ago:
                    signals_last_hour += 1
                if created_at >= day_ago:
                    signals_last_24h += 1

                signal_levels[level] = signal_levels.get(level, 0) + 1

            stats = {
                "signals_last_hour": signals_last_hour,
                "signals_last_24h": signals_last_24h,
                "total_signals": len(all_signals.data),
                "by_level": signal_levels,
            }

            log.info(f"PanicFrame statistics: {stats}")
            return stats
        except Exception as e:
            log.error(f"Error fetching PanicFrame signals: {e}")
            return {"signals_last_hour": 0, "signals_last_24h": 0, "total_signals": 0, "by_level": {}}

    def build_report(self) -> Dict[str, Any]:
        """Build comprehensive status report.

        Returns:
            Complete status report dictionary
        """
        now = datetime.now(timezone.utc)

        # Fetch all data
        judge_summary = self.fetch_judge_summary()
        case_stats = self.fetch_case_statistics()
        signal_stats = self.fetch_panicframe_signals()

        # Calculate aggregates
        total_judge_capacity = sum(j.get("max_workload", 0) for j in judge_summary)
        total_judge_workload = sum(j.get("current_workload", 0) for j in judge_summary)
        total_available_slots = sum(j.get("available_slots", 0) for j in judge_summary)

        system_utilization = (total_judge_workload / total_judge_capacity * 100) if total_judge_capacity > 0 else 0

        report = {
            "generated_at": now.isoformat() + "Z",
            "summary": {
                "judges": {
                    "total": len(judge_summary),
                    "capacity": total_judge_capacity,
                    "current_workload": total_judge_workload,
                    "available_slots": total_available_slots,
                    "system_utilization_percent": round(system_utilization, 2),
                    "judges": judge_summary,
                },
                "cases": case_stats,
                "panicframe": signal_stats,
            },
            "schema_references": {
                "tables": [
                    "judges (id, name, current_workload, max_workload, status, specialization, f2_score)",
                    "cases (id, case_number, case_type, complexity, filing_date, assigned_judge_id, status)",
                    "panicframe_signals (id, created_at, level, key, meta)",
                ]
            },
            "notes": [
                "Report generated from Supabase production data",
                "All timestamps in UTC",
                "Judge utilization is calculated as current_workload / max_workload",
                "Cases status breakdown includes: pending, assigned, closed, etc.",
            ],
        }

        return report


def main(out_path: Optional[str] = None) -> int:
    """Main entry point for status report generation.

    Args:
        out_path: Optional output file path for report

    Returns:
        Exit code (0 for success, 1 for failure)
    """
    try:
        log.info("Starting status report generation...")

        generator = StatusReportGenerator()
        report = generator.build_report()

        if out_path:
            os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)
            with open(out_path, "w", encoding="utf-8") as f:
                json.dump(report, f, indent=2)
            log.info(f"Wrote status report: {out_path}")
        else:
            print(json.dumps(report, indent=2))

        log.info("Status report generation completed successfully")
        return 0
    except Exception:
        log.exception("Status report generation failed")
        return 1


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Generate consolidated status report from Supabase")
    parser.add_argument("--out", help="Output path for JSON report (if not specified, prints to stdout)", default=None)
    args = parser.parse_args()

    exit_code = main(args.out)
    sys.exit(exit_code)
