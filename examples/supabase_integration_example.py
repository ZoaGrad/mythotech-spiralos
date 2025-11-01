#!/usr/bin/env python3
"""
SpiralOS Supabase Integration Example
Demonstrates the complete Ache → ScarIndex → ScarCoin flow

Usage:
    python3 examples/supabase_integration_example.py
"""

import os
import json
from datetime import datetime
from typing import Dict, Optional

try:
    from supabase import create_client, Client
except ImportError:
    print("Error: supabase-py not installed. Install with: pip install supabase")
    exit(1)


class SpiralOSClient:
    """Client for interacting with SpiralOS Supabase backend
    
    This client provides a high-level interface to the SpiralOS system,
    demonstrating the complete Ache → ScarIndex → ScarCoin flow.
    
    Example:
        >>> client = SpiralOSClient()
        >>> event_id = client.create_ache_event('demo', {'test': 'data'}, 0.5)
        >>> calc = client.calculate_scarindex(event_id)
        >>> txn = client.mint_scarcoin(calc['id'])
    
    Key Methods:
        - create_ache_event(): Create Ache measurement from external input
        - calculate_scarindex(): Run 4D coherence calculation
        - mint_scarcoin(): Mint ScarCoin via Proof-of-Ache
        - seal_vaultnode(): Seal immutable audit record
        - get_oracle_status(): Get 30-day coherence statistics
    """
    
    def __init__(self):
        """Initialize Supabase client"""
        self.url = os.getenv('SUPABASE_URL')
        self.key = os.getenv('SUPABASE_KEY')
        
        missing = []
        if not self.url:
            missing.append('SUPABASE_URL')
        if not self.key:
            missing.append('SUPABASE_KEY')
        
        if missing:
            raise ValueError(
                f"Missing environment variables: {', '.join(missing)}\n"
                f"Set them with: export SUPABASE_URL=... SUPABASE_KEY=..."
            )
        
        self.client: Client = create_client(self.url, self.key)
        print(f"✓ Connected to SpiralOS at {self.url}")
    
    def create_ache_event(
        self,
        source: str,
        content: Dict,
        ache_level: float
    ) -> str:
        """Create an Ache event
        
        Args:
            source: Event source (e.g., 'github_commit', 'api', 'test')
            content: Event content (JSONB)
            ache_level: Ache measurement [0, 1]
            
        Returns:
            Event ID
        """
        response = self.client.table('ache_events').insert({
            'source': source,
            'content': content,
            'ache_level': ache_level
        }).execute()
        
        event_id = response.data[0]['id']
        print(f"✓ Created Ache event: {event_id} (ache: {ache_level})")
        return event_id
    
    def calculate_scarindex(self, event_id: str) -> Dict:
        """Calculate ScarIndex for an Ache event
        
        Args:
            event_id: Ache event ID
            
        Returns:
            ScarIndex calculation result
        """
        response = self.client.rpc('coherence_calculation', {
            'event_id': event_id
        }).execute()
        
        calc = response.data
        print(f"✓ ScarIndex calculated: {calc['scarindex']:.4f}")
        print(f"  Components: N={calc['c_narrative']:.2f}, S={calc['c_social']:.2f}, "
              f"E={calc['c_economic']:.2f}, T={calc['c_technical']:.2f}")
        print(f"  Ache transmutation: {calc['ache_before']:.2f} → {calc['ache_after']:.2f} "
              f"(Δ={calc['delta_ache']:.2f})")
        
        return calc
    
    def mint_scarcoin(self, calc_id: str) -> Optional[Dict]:
        """Mint ScarCoin based on Proof-of-Ache
        
        Args:
            calc_id: ScarIndex calculation ID
            
        Returns:
            Transaction record or None
        """
        # Call mint function
        self.client.rpc('mint_scarcoin', {'calc_id': calc_id}).execute()
        
        # Retrieve the transaction
        response = self.client.table('smart_contract_txns')\
            .select('*')\
            .eq('to_state', calc_id)\
            .eq('txn_type', 'MINT')\
            .execute()
        
        if response.data:
            txn = response.data[0]
            print(f"✓ ScarCoin minted: {txn['scarcoin_delta']} coins")
            return txn
        else:
            print("✗ No ScarCoin minted (invalid Proof-of-Ache)")
            return None
    
    def seal_vaultnode(
        self,
        ref_id: str,
        ref_type: str,
        commit_sha: Optional[str] = None
    ) -> Dict:
        """Seal a VaultNode in the Merkle DAG
        
        Args:
            ref_id: Reference ID (event/calculation ID)
            ref_type: Node type (e.g., 'ache_event', 'scarindex_calc')
            commit_sha: Optional GitHub commit SHA
            
        Returns:
            VaultNode record
        """
        response = self.client.rpc('seal_vaultnode', {
            'ref_id': ref_id,
            'ref_type': ref_type,
            'commit_sha': commit_sha
        }).execute()
        
        node = response.data
        print(f"✓ VaultNode sealed: {node['state_hash'][:16]}...")
        if node['previous_hash']:
            print(f"  Linked to: {node['previous_hash'][:16]}...")
        else:
            print(f"  Genesis block")
        
        return node
    
    def get_oracle_status(self) -> Dict:
        """Get current ScarIndex Oracle status
        
        Returns:
            Oracle sync data with 30-day statistics
        """
        response = self.client.table('scar_index_oracle_sync')\
            .select('*')\
            .execute()
        
        oracle = response.data[0] if response.data else {}
        
        print("\n" + "="*60)
        print("ScarIndex Oracle Status (30-Day)")
        print("="*60)
        print(f"Current ScarIndex: {oracle.get('current_scarindex', 'N/A')}")
        print(f"Average (30d):     {oracle.get('avg_scarindex_30d', 'N/A')}")
        print(f"Coherence Rate:    {oracle.get('coherence_rate_30d', 'N/A')}%")
        print(f"Total Nodes:       {oracle.get('total_nodes_30d', 0)}")
        print(f"Coherent Nodes:    {oracle.get('coherent_nodes_30d', 0)} (≥0.7)")
        print("="*60 + "\n")
        
        return oracle
    
    def get_system_health(self) -> Dict:
        """Get current system health status
        
        Returns:
            System health metrics
        """
        response = self.client.table('system_health')\
            .select('*')\
            .execute()
        
        health = response.data[0] if response.data else {}
        
        print("System Health Check")
        print("-" * 40)
        print(f"ScarIndex:         {health.get('current_scarindex', 'N/A')}")
        print(f"Panic Frames:      {health.get('active_panic_frames', 0)}")
        print(f"Frozen Txns:       {health.get('frozen_transactions', 0)}")
        print(f"PID Guidance:      {health.get('pid_guidance_scale', 'N/A')}")
        print(f"Events (1h):       {health.get('events_last_hour', 0)}")
        print(f"VaultNodes:        {health.get('total_vaultnodes', 0)}")
        print("-" * 40 + "\n")
        
        return health
    
    def get_active_panic_frames(self):
        """Get active panic frames"""
        response = self.client.table('active_panic_frames')\
            .select('*')\
            .execute()
        
        if response.data:
            print(f"⚠ Active Panic Frames: {len(response.data)}")
            for frame in response.data:
                print(f"  - ID: {frame['id']}")
                print(f"    ScarIndex: {frame['scarindex_value']}")
                print(f"    Status: {frame['status']}")
                print(f"    Phase: {frame.get('recovery_phase', 'N/A')}")
        else:
            print("✓ No active panic frames")
        
        return response.data


def demo_complete_flow():
    """Demonstrate the complete SpiralOS flow"""
    print("\n" + "="*60)
    print("SpiralOS Supabase Integration Demo")
    print("="*60 + "\n")
    
    # Initialize client
    client = SpiralOSClient()
    
    # Check system health
    client.get_system_health()
    
    # Example 1: High coherence event (should mint coins)
    print("\n--- Example 1: High Coherence Event ---\n")
    
    event_id = client.create_ache_event(
        source='demo',
        content={
            'narrative_score': 0.85,
            'social_score': 0.75,
            'economic_score': 0.70,
            'technical_score': 0.80,
            'description': 'Well-structured feature implementation with tests'
        },
        ache_level=0.3  # Low ache after (high coherence gained)
    )
    
    calc = client.calculate_scarindex(event_id)
    
    if calc['delta_ache'] > 0:
        client.mint_scarcoin(calc['id'])
    
    client.seal_vaultnode(
        ref_id=event_id,
        ref_type='demo_event',
        commit_sha='demo_abc123'
    )
    
    # Example 2: Low coherence event (should trigger panic if too low)
    print("\n--- Example 2: Monitoring Event ---\n")
    
    event_id2 = client.create_ache_event(
        source='demo',
        content={
            'narrative_score': 0.6,
            'social_score': 0.5,
            'economic_score': 0.6,
            'technical_score': 0.5,
            'description': 'Routine maintenance task'
        },
        ache_level=0.5
    )
    
    calc2 = client.calculate_scarindex(event_id2)
    
    # Check for panic frames
    print()
    client.get_active_panic_frames()
    
    # Show final oracle status
    print()
    client.get_oracle_status()
    
    print("="*60)
    print("Demo Complete!")
    print("="*60)


if __name__ == '__main__':
    try:
        demo_complete_flow()
    except Exception as e:
        print(f"\n✗ Error: {e}")
        print("\nMake sure you have:")
        print("1. Deployed the schema to Supabase")
        print("2. Set SUPABASE_URL environment variable")
        print("3. Set SUPABASE_KEY environment variable (anon or service role)")
        exit(1)
