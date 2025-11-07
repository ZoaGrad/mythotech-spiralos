#!/usr/bin/env python3
"""
Oracle Bridge Synchronization Script
Synchronizes on-chain Oracle data with Supabase for SpiralOS governance.
"""

import os
import sys
import json
import logging
from argparse import ArgumentParser
from datetime import datetime

import requests
from web3 import Web3
from supabase import create_client, Client

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class OracleBridge:
    def __init__(self):
        self.supabase_url = os.getenv('SUPABASE_URL')
        self.supabase_key = os.getenv('SUPABASE_SERVICE_KEY')
        self.polygon_rpc = os.getenv('POLYGON_RPC')
        self.alchemy_key = os.getenv('ALCHEMY_API_KEY')
        
        self.supabase: Client = create_client(self.supabase_url, self.supabase_key)
        self.w3 = Web3(Web3.HTTPProvider(self.polygon_rpc))
        
        if not self.w3.is_connected():
            raise Exception('Failed to connect to Polygon Mumbai RPC')
        
        logger.info('Oracle Bridge initialized')
    
    def fetch_oracle_data(self):
        """Fetch current Oracle data from Alchemy."""
        try:
            headers = {'Authorization': f'Bearer {self.alchemy_key}'}
            response = requests.get(
                'https://polygon-mumbai.g.alchemy.com/v2/oracle/latest',
                headers=headers,
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f'Failed to fetch Oracle data: {e}')
            return None
    
    def sync_to_supabase(self, oracle_data):
        """Synchronize Oracle data to Supabase."""
        try:
            sync_record = {
                'oracle_data': oracle_data,
                'synced_at': datetime.utcnow().isoformat(),
                'chain': 'polygon-mumbai'
            }
            
            response = self.supabase.table('oracle_sync_log').insert(sync_record).execute()
            logger.info(f'Oracle data synchronized: {response.data}')
            return True
        except Exception as e:
            logger.error(f'Failed to sync to Supabase: {e}')
            return False
    
    def run_sync(self):
        """Execute full synchronization cycle."""
        logger.info('Starting Oracle Bridge sync...')
        
        oracle_data = self.fetch_oracle_data()
        if oracle_data:
            success = self.sync_to_supabase(oracle_data)
            if success:
                logger.info('✅ Oracle Bridge sync complete')
                return 0
        
        logger.error('❌ Oracle Bridge sync failed')
        return 1

def main():
    parser = ArgumentParser(description='Oracle Bridge Synchronization')
    parser.add_argument('--sync', action='store_true', help='Run synchronization')
    parser.add_argument('--test', action='store_true', help='Test connection')
    args = parser.parse_args()
    
    try:
        bridge = OracleBridge()
        
        if args.test:
            logger.info('Connection test passed')
            return 0
        elif args.sync:
            return bridge.run_sync()
        else:
            logger.info('Use --sync or --test flag')
            return 1
    
    except Exception as e:
        logger.error(f'Fatal error: {e}')
        return 1

if __name__ == '__main__':
    sys.exit(main())
