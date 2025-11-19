#!/usr/bin/env python3
"""
Test script to verify the minting system fixes for SpiralOS Overwatch app.

Fixes implemented:
1. Updated economy.py to use 'reason' column in mint_events table
2. Added schema migration for backward compatibility
3. Fixed dashboard.py to handle both old and new schemas
4. Updated vault.py to use consistent column names (event_type, payload_json)
5. Fixed bootstrap.py to use correct mint() signature

This script verifies all components work together correctly.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.economy import ScarCoinMintingEngine
from core.vault import VaultEventLogger
import sqlite3


def test_economy_mint():
    """Test the minting engine with various contexts"""
    print("Testing Economy Minting Engine...")
    
    engine = ScarCoinMintingEngine()
    initial_supply = engine.total_supply
    
    # Test with dict context
    engine.mint(100, {'source': 'test_dict', 'scarindex': 0.8})
    
    # Test with string context
    engine.mint(50, 'test_string')
    
    # Test with None context
    engine.mint(25, None)
    
    final_supply = engine.total_supply
    assert final_supply == initial_supply + 175, "Supply calculation incorrect"
    
    print("✅ Economy minting tests passed")
    return True


def test_vault_logging():
    """Test the vault event logger"""
    print("Testing Vault Event Logger...")
    
    vault = VaultEventLogger()
    vault.log_event('TEST_EVENT', {'test': True, 'value': 123})
    
    # Verify the event was logged
    conn = sqlite3.connect(os.path.join(os.getcwd(), "spiral_data", "vault.db"))
    cursor = conn.cursor()
    cursor.execute("SELECT event_type, payload_json FROM vault_events WHERE event_type = 'TEST_EVENT' ORDER BY ts DESC LIMIT 1")
    result = cursor.fetchone()
    conn.close()
    
    assert result is not None, "Event not logged"
    assert result[0] == 'TEST_EVENT', "Event type incorrect"
    assert 'test' in result[1], "Payload not stored correctly"
    
    print("✅ Vault logging tests passed")
    return True


def test_database_schema():
    """Test that database schemas are correct"""
    print("Testing Database Schemas...")
    
    # Check economy database
    conn = sqlite3.connect(os.path.join(os.getcwd(), "spiral_data", "economy.db"))
    cursor = conn.cursor()
    cursor.execute("PRAGMA table_info(mint_events)")
    columns = [col[1] for col in cursor.fetchall()]
    conn.close()
    
    assert 'reason' in columns, "economy.db: reason column missing"
    assert 'context' in columns, "economy.db: context column missing"
    
    # Check vault database
    conn = sqlite3.connect(os.path.join(os.getcwd(), "spiral_data", "vault.db"))
    cursor = conn.cursor()
    cursor.execute("PRAGMA table_info(vault_events)")
    columns = [col[1] for col in cursor.fetchall()]
    conn.close()
    
    assert 'event_type' in columns, "vault.db: event_type column missing"
    assert 'payload_json' in columns, "vault.db: payload_json column missing"
    
    print("✅ Database schema tests passed")
    return True


def test_dashboard_queries():
    """Test that dashboard queries work correctly"""
    print("Testing Dashboard Queries...")
    
    import pandas as pd
    
    # Test economy feed query
    ECON_DB = os.path.join(os.getcwd(), 'spiral_data', 'economy.db')
    conn = sqlite3.connect(ECON_DB)
    try:
        df = pd.read_sql_query(
            "SELECT datetime(ts, 'unixepoch', 'localtime') as Time, "
            "amount as SCAR, "
            "COALESCE(reason, context, 'N/A') as Reason "
            "FROM mint_events ORDER BY ts DESC LIMIT 5", 
            conn
        )
        assert not df.empty, "Economy feed query returned no results"
    finally:
        conn.close()
    
    # Test vault logs query
    VAULT_DB = os.path.join(os.getcwd(), 'spiral_data', 'vault.db')
    conn = sqlite3.connect(VAULT_DB)
    try:
        df = pd.read_sql_query(
            "SELECT datetime(ts, 'unixepoch', 'localtime') as Time, "
            "event_type as Event, "
            "payload_json as Payload "
            "FROM vault_events ORDER BY ts DESC LIMIT 5", 
            conn
        )
        # May be empty on fresh install, so just check it doesn't error
    finally:
        conn.close()
    
    print("✅ Dashboard query tests passed")
    return True


def main():
    """Run all tests"""
    print("=" * 70)
    print("SpiralOS Overwatch - Minting System Verification")
    print("=" * 70)
    print()
    
    tests = [
        test_economy_mint,
        test_vault_logging,
        test_database_schema,
        test_dashboard_queries,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ {test.__name__} failed: {e}")
            failed += 1
        print()
    
    print("=" * 70)
    print(f"Test Results: {passed} passed, {failed} failed")
    print("=" * 70)
    
    if failed == 0:
        print("\n✅ All tests passed! The minting system is working correctly.")
        print("\nYou can now run the dashboard with:")
        print("  streamlit run core/dashboard.py")
        return 0
    else:
        print(f"\n❌ {failed} test(s) failed. Please review the errors above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
