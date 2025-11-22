#!/usr/bin/env python3
"""
SpiralOS System Summary CLI

Command-line tool for viewing system status and health metrics.

Usage:
    python3 summary_cli.py              # Full summary
    python3 summary_cli.py --quick      # Quick status line
    python3 summary_cli.py --json       # JSON output
    python3 summary_cli.py --health     # Health metrics only
"""

import argparse
import json
import sys
from decimal import Decimal

# Import components
from scarcoin import ScarCoinMintingEngine
from system_summary import SystemSummary
from vaultnode import VaultNode

try:
    from empathy_market import EmpathyMarket

    EMPATHY_AVAILABLE = True
except ImportError:
    EMPATHY_AVAILABLE = False


def print_banner():
    """Print SpiralOS banner"""
    print("=" * 70)
    print("SpiralOS v1.3-alpha - System Summary")
    print("=" * 70)
    print()


def print_summary_human(summary: dict):
    """Print summary in human-readable format"""
    print_banner()

    # System Overview
    print("SYSTEM OVERVIEW")
    print("-" * 70)
    print(f"Name:       {summary['system']['name']}")
    print(f"Version:    {summary['system']['version']}")
    print(f"Vault ID:   {summary['system']['vault_id']}")
    print(f"Status:     {summary['system']['status']}")
    print(f"Timestamp:  {summary['system']['timestamp']}")
    print()

    # Health Metrics
    health = summary["health"]
    print("HEALTH METRICS")
    print("-" * 70)
    print(f"Overall Score:         {health['overall_score']:.0%}")
    print(f"Blockchain Integrity:  {'✓' if health['blockchain_integrity'] else '✗'}")
    print(f"Economic Activity:     {health['economic_activity']}")
    print(f"Coherence Status:      {health['coherence_status']}")
    print()

    # ScarCoin Economy
    scarcoin = summary["components"]["scarcoin"]
    if scarcoin["available"]:
        print("SCARCOIN ECONOMY")
        print("-" * 70)
        print(f"Total Supply:      {scarcoin['supply']['total_supply']} SCAR")
        print(f"Total Minted:      {scarcoin['supply']['total_minted']} SCAR")
        print(f"Total Burned:      {scarcoin['supply']['total_burned']} SCAR")
        print(f"Circulating:       {scarcoin['supply']['circulating']} SCAR")
        print(f"Minting Events:    {scarcoin['activity']['minting_count']}")
        print(f"Burning Events:    {scarcoin['activity']['burning_count']}")
        print(f"Active Wallets:    {scarcoin['activity']['active_wallets']}")
        print()

    # Empathy Market
    empathy = summary["components"]["empathy_market"]
    if empathy["available"]:
        print("EMPATHY MARKET")
        print("-" * 70)
        print(f"Total EMP Minted:       {empathy['tokens']['total_emp_minted']} EMP")
        print(f"Resonance Events:       {empathy['tokens']['total_resonance_events']}")
        print(f"Avg EMP per Event:      {empathy['tokens']['average_emp_per_event']} EMP")
        print(f"Total Participants:     {empathy['participation']['total_participants']}")
        print()

    # VaultNode Blockchain
    vault = summary["components"]["vaultnode"]
    if vault["available"]:
        print("VAULTNODE BLOCKCHAIN")
        print("-" * 70)
        print(f"Vault ID:          {vault['blockchain']['vault_id']}")
        print(f"Total Blocks:      {vault['blockchain']['total_blocks']}")
        print(f"Total Events:      {vault['blockchain']['total_events']}")
        print(f"Latest Block:      #{vault['blockchain']['latest_block_number']}")
        print(f"Chain Valid:       {'✓' if vault['blockchain']['chain_valid'] else '✗'}")
        print(f"Pending Events:    {vault['pending']['pending_events']}")
        print()

    # Core System
    core = summary["components"]["core"]
    if core["available"]:
        print("CORE SYSTEM")
        print("-" * 70)
        print(f"Current ScarIndex:     {core['coherence']['current_scarindex']:.4f}")
        print(f"Target ScarIndex:      {core['coherence']['target_scarindex']:.4f}")
        print(f"Coherence Status:      {core['coherence']['status']}")
        print(f"Total Transmutations:  {core['transmutations']['total']}")
        print(f"Successful:            {core['transmutations']['successful']}")
        print(f"Success Rate:          {core['transmutations']['success_rate']}")
        print(f"Active Panic Frames:   {core['panic_frames']['active_count']}")
        print()

    # Footer
    print("=" * 70)
    print(summary["motto"])
    print("=" * 70)


def print_health_only(summary: dict):
    """Print only health metrics"""
    print_banner()

    health = summary["health"]
    system = summary["system"]

    print("HEALTH SUMMARY")
    print("-" * 70)
    print(f"System Status:         {system['status']}")
    print(f"Overall Health Score:  {health['overall_score']:.0%}")
    print(f"Blockchain Integrity:  {'VALID ✓' if health['blockchain_integrity'] else 'INVALID ✗'}")
    print(f"Economic Activity:     {health['economic_activity'].upper()}")
    print(f"Coherence Status:      {health['coherence_status']}")
    print()

    # Health interpretation
    score = health["overall_score"]
    if score >= 0.8:
        status_msg = "EXCELLENT - System operating optimally"
        emoji = "🟢"
    elif score >= 0.6:
        status_msg = "GOOD - System operating normally"
        emoji = "🟡"
    elif score >= 0.4:
        status_msg = "FAIR - Some degradation detected"
        emoji = "🟠"
    else:
        status_msg = "POOR - System requires attention"
        emoji = "🔴"

    print(f"{emoji} {status_msg}")
    print()
    print("=" * 70)


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="SpiralOS System Summary CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 summary_cli.py              # Full summary
  python3 summary_cli.py --quick      # Quick one-line status
  python3 summary_cli.py --json       # JSON output
  python3 summary_cli.py --health     # Health metrics only
        """,
    )

    parser.add_argument("--quick", "-q", action="store_true", help="Show quick one-line status")

    parser.add_argument("--json", "-j", action="store_true", help="Output in JSON format")

    parser.add_argument("--health", "-H", action="store_true", help="Show only health metrics")

    parser.add_argument("--vault-id", default="ΔΩ.123.0", help="VaultNode ID (default: ΔΩ.123.0)")

    args = parser.parse_args()

    try:
        # Initialize components
        minting_engine = ScarCoinMintingEngine(multiplier=Decimal("1000"), min_delta_c=Decimal("0.01"))

        vaultnode = VaultNode(vault_id=args.vault_id)

        empathy_market = None
        if EMPATHY_AVAILABLE:
            empathy_market = EmpathyMarket()

        # Create summary
        summarizer = SystemSummary(minting_engine=minting_engine, empathy_market=empathy_market, vaultnode=vaultnode)

        # Output based on flags
        if args.quick:
            print(summarizer.get_quick_status())

        elif args.json:
            summary = summarizer.get_summary()
            print(json.dumps(summary, indent=2, default=str))

        elif args.health:
            summary = summarizer.get_summary()
            print_health_only(summary)

        else:
            summary = summarizer.get_summary()
            print_summary_human(summary)

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
