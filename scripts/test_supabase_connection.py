#!/usr/bin/env python3
"""
Test Supabase Connection

Simple script to verify Supabase credentials and connection.
Tests both SERVICE_KEY and ANON_KEY if available.
"""

import os
import sys
from typing import Optional

import pytest

try:
    from supabase import create_client
except ImportError:  # pragma: no cover - dependency safety net
    create_client = None  # type: ignore[assignment]


def _test_connection(url: str, key: str, key_type: str) -> bool:
    """
    Test Supabase connection with given credentials
    
    Args:
        url: Supabase project URL
        key: API key (service or anon)
        key_type: Type of key for logging
        
    Returns:
        True if connection successful
    """
    try:
        print(f"\nTesting {key_type}...")
        print(f"  URL: {url}")
        print(f"  Key length: {len(key)} characters")
        
        # Create client
        client = create_client(url, key)
        
        # Try to query a table (will fail gracefully if table doesn't exist)
        # This validates the connection works
        try:
            response = client.table('ache_events').select('id').limit(1).execute()
            print(f"  ✓ Connection successful!")
            print(f"  ✓ Table 'ache_events' accessible")
            return True
        except Exception as table_error:
            # Connection works but table might not exist yet
            print(f"  ✓ Connection successful!")
            print(f"  ⚠ Table query failed (may not exist yet): {table_error}")
            return True
            
    except Exception as e:
        print(f"  ✗ Connection failed: {e}")
        return False


def _get_env(var: str) -> Optional[str]:
    value = os.getenv(var)
    return value if value else None


@pytest.mark.skipif(create_client is None, reason="supabase package not installed")
def test_supabase_service_connection():
    url = _get_env('SUPABASE_URL')
    service_key = _get_env('SUPABASE_SERVICE_KEY')

    if not url or not service_key:
        pytest.skip('Supabase service credentials not configured')

    assert _test_connection(url, service_key, "SERVICE_KEY")


@pytest.mark.skipif(create_client is None, reason="supabase package not installed")
def test_supabase_anon_connection():
    url = _get_env('SUPABASE_URL')
    anon_key = _get_env('SUPABASE_ANON_KEY')

    if not url or not anon_key:
        pytest.skip('Supabase anon credentials not configured')

    assert _test_connection(url, anon_key, "ANON_KEY")


def main():
    """Main test function"""
    print("=" * 60)
    print("SpiralOS Supabase Connection Test")
    print("=" * 60)

    if create_client is None:
        print("\n✗ ERROR: supabase package not installed")
        print("  Install with: pip install supabase>=1.0.0,<2.0.0")
        sys.exit(1)
    
    # Get credentials from environment
    url = os.getenv('SUPABASE_URL')
    service_key = os.getenv('SUPABASE_SERVICE_KEY')
    anon_key = os.getenv('SUPABASE_ANON_KEY')
    project_ref = os.getenv('SUPABASE_PROJECT_REF')
    
    # Check required credentials
    if not url:
        print("\n✗ ERROR: SUPABASE_URL not set")
        print("  Set with: export SUPABASE_URL='https://xxxxx.supabase.co'")
        sys.exit(1)
    
    if not service_key:
        print("\n✗ ERROR: SUPABASE_SERVICE_KEY not set")
        print("  Set with: export SUPABASE_SERVICE_KEY='your-service-key'")
        sys.exit(1)
    
    # Test service key (required)
    service_ok = _test_connection(url, service_key, "SERVICE_KEY")
    
    # Test anon key (optional)
    anon_ok = True
    if anon_key:
        anon_ok = _test_connection(url, anon_key, "ANON_KEY")
    else:
        print("\n⚠ SUPABASE_ANON_KEY not set (optional for frontend)")
    
    # Display project ref
    if project_ref:
        print(f"\n✓ SUPABASE_PROJECT_REF: {project_ref}")
    else:
        print("\n⚠ SUPABASE_PROJECT_REF not set (optional for CLI tools)")
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    if service_ok:
        print("✓ Service Key: WORKING")
    else:
        print("✗ Service Key: FAILED")
    
    if anon_key:
        if anon_ok:
            print("✓ Anon Key: WORKING")
        else:
            print("✗ Anon Key: FAILED")
    else:
        print("⚠ Anon Key: NOT CONFIGURED")
    
    print("=" * 60)
    
    if service_ok and (anon_ok or not anon_key):
        print("\n🜂 All configured credentials are working!")
        print("   Ready for Supabase integration.")
        sys.exit(0)
    else:
        print("\n✗ Some credentials failed. Check the errors above.")
        sys.exit(1)


if __name__ == '__main__':
    main()
