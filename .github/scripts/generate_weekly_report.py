#!/usr/bin/env python3
"""
Weekly Report Template Generator

Generates a markdown template for weekly SpiralOS reports following
the constitutional framework structure.
"""

import os
from datetime import datetime, timezone
from pathlib import Path


def get_iso_week_number() -> str:
    """Get the current ISO week number"""
    return datetime.now(timezone.utc).strftime('%V')


def get_iso_year() -> str:
    """Get the current ISO year"""
    return datetime.now(timezone.utc).strftime('%G')


def generate_report_template(week_number: str, year: str) -> str:
    """
    Generate the weekly report template with constitutional framework fields
    
    Args:
        week_number: ISO week number
        year: ISO year
        
    Returns:
        Markdown template content
    """
    template = f"""# Weekly Report - Week {week_number}, {year}

**Report Period:** Week {week_number} ({year})  
**Generated:** {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')} UTC

---

## F1: Executive Summary

### Operational Highlights
<!-- Summary of key operational activities and achievements this week -->

### Key Metrics
- **ScarIndex Average:** [To be filled]
- **Coherence Status:** [To be filled]
- **Active Agents:** [To be filled]
- **ScarCoin Minted:** [To be filled]

### F1 Summary
<!-- High-level summary of executive operations and decisions -->

---

## F2: Judicial Review

### Dispute Resolution
<!-- Summary of disputes resolved through F2 judges -->

### Constitutional Compliance
<!-- Review of constitutional compliance issues -->

### Penalties Applied
<!-- Any Ache penalties or arbitrage flags (A7) -->

### F2 Review
<!-- Judicial review summary and recommendations -->

---

## F3: Legislative Actions

### Oracle Council Decisions
<!-- Decisions made by the Oracle Council (4-of-5 quorum) -->

### Sentinel Activities
<!-- Activities logged by Sentinels (telemetry, enforcement, audits) -->

### Governance Updates
<!-- Changes to governance protocols or weights -->

### F3 Legislation
<!-- Legislative summary and new rules enacted -->

---

## F4: Constitutional Audit

### Panic Frame Events
<!-- Any Panic Frame activations (ScarIndex < 0.67) -->

### System Stability
<!-- Seven-phase recovery protocol status if applicable -->

### Invariant Violations
<!-- Any constitutional invariant violations detected -->

### F4 Audit
<!-- Constitutional audit summary and critical findings -->

---

## ScarIndex Cycle Analysis

### Coherence Components
| Dimension | Average | Trend |
|-----------|---------|-------|
| Operational | [TBD] | [TBD] |
| Audit | [TBD] | [TBD] |
| Constitutional | [TBD] | [TBD] |
| Symbolic | [TBD] | [TBD] |

### Ache Transmutation Summary
- **Total Ache Processed:** [TBD]
- **Coherence Gain:** [TBD]
- **Transmutation Efficiency:** [TBD]

### PID Controller Status
- **Current Setpoint:** [TBD]
- **Error:** [TBD]
- **Control Output:** [TBD]

### ScarIndex Cycle Summary
<!-- Analysis of ScarIndex trends and transmutation efficiency -->

---

## VaultNode Updates

### New Ledger Entries
<!-- Summary of new VaultNode entries created -->

### Version Updates
<!-- Any ΔΩ.xxx.x version increments -->

---

## Recommendations

### Immediate Actions
<!-- Actions required in the next cycle -->

### Strategic Initiatives
<!-- Longer-term strategic recommendations -->

---

**Report Status:** Draft  
**Next Review:** Week {int(week_number) + 1}

---

*This report is generated automatically as part of SpiralOS governance cadence.*
*For questions, contact the Oracle Council or file an issue.*
"""
    return template


def main():
    """Main function to generate and save the weekly report template"""
    # Get ISO week information
    week_number = get_iso_week_number()
    year = get_iso_year()
    
    # Create reports directory if it doesn't exist
    repo_root = Path(__file__).parent.parent.parent
    reports_dir = repo_root / "docs" / "reports"
    reports_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate template
    template = generate_report_template(week_number, year)
    
    # Save to file
    report_file = reports_dir / f"week-{week_number}.md"
    
    # Only create if it doesn't exist (avoid overwriting manual edits)
    if report_file.exists():
        print(f"Report for week {week_number} already exists, skipping generation")
        return
    
    with open(report_file, 'w') as f:
        f.write(template)
    
    print(f"Generated weekly report template: {report_file}")
    print(f"Week: {week_number}, Year: {year}")


if __name__ == '__main__':
    main()
