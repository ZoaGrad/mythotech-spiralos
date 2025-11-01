"""Status Report Automation.

Generates a consolidated status report from Supabase data including:
- Judge workloads and availability
- Case assignment stats
- PanicFrame signals summary

Usage:
    python -m core.automation.status_report --out reports/status_YYYYMMDD.json

Env:
    SUPABASE_URL, SUPABASE_KEY, LOG_LEVEL
"""
import os
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, Any

logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format='%(asctime)s - %(levelname)s - %(message)s'
)
log = logging.getLogger(__name__)


def fetch_summary_from_supabase() -> Dict[str, Any]:
    """Fetch summary metrics from Supabase.

    Tables referenced:
    - judges (id, name, workload, max_workload, status)
    - cases (id, status, assigned_judge_id, filing_date)
    - panicframe_signals (id, created_at, level, key, meta)

    NOTE: Replace placeholders with actual Supabase client queries.
    """
    # Placeholders for metrics (wire up supabase client in real deployment)
    judges = []  # SELECT id,name,workload,max_workload,status FROM judges;
    cases_open = 0  # SELECT count(*) FROM cases WHERE status != 'closed';
    cases_unassigned = 0  # SELECT count(*) FROM cases WHERE assigned_judge_id IS NULL AND status != 'closed';
    panic_signals_24h = 0  # SELECT count(*) FROM panicframe_signals WHERE created_at > now()-interval '24 hours';

    judge_capacity = [
        {
            "id": j.get("id"),
            "name": j.get("name"),
            "workload": j.get("workload", 0),
            "max_workload": j.get("max_workload", 0),
            "available": max(j.get("max_workload", 0) - j.get("workload", 0), 0)
        }
        for j in judges
    ]

    return {
        "judges": judge_capacity,
        "cases": {
            "open": cases_open,
            "unassigned": cases_unassigned,
        },
        "panicframe": {
            "signals_last_24h": panic_signals_24h
        },
    }


def build_report() -> Dict[str, Any]:
    summary = fetch_summary_from_supabase()
    now = datetime.utcnow()

    report = {
        "generated_at": now.isoformat() + "Z",
        "summary": summary,
        "notes": [
            "Wire Supabase client to replace placeholders before production.",
            "Ensure RLS policies permit the service role to read needed rows.",
        ],
        "schema_references": {
            "tables": [
                "judges(id, name, workload, max_workload, status)",
                "cases(id, status, assigned_judge_id, filing_date)",
                "panicframe_signals(id, created_at, level, key, meta)",
            ]
        }
    }
    return report


def main(out_path: str | None = None) -> int:
    try:
        if not os.getenv("SUPABASE_URL") or not os.getenv("SUPABASE_KEY"):
            log.warning("SUPABASE_URL/SUPABASE_KEY not set. Using placeholder data.")

        report = build_report()
        if out_path:
            os.makedirs(os.path.dirname(out_path), exist_ok=True)
            with open(out_path, "w", encoding="utf-8") as f:
                json.dump(report, f, indent=2)
            log.info(f"Wrote status report: {out_path}")
        else:
            print(json.dumps(report, indent=2))
        return 0
    except Exception as e:
        log.exception("Status report generation failed")
        return 1


if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--out", help="Output path for JSON report", default=None)
    args = p.parse_args()
    raise SystemExit(main(args.out))
