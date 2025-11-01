#!/usr/bin/env python3
"""
ScarIndex Logging Hook for Supabase

Provides a logging mechanism to append ScarIndex calculation deltas
to the scarindex_calculations table in Supabase after each cycle.
"""

import os
from typing import Dict, Optional
from datetime import datetime, timezone

try:
    from supabase import create_client, Client
    SUPABASE_AVAILABLE = True
except ImportError:
    SUPABASE_AVAILABLE = False
    print("WARNING: supabase-py not installed, ScarIndex logging will be disabled")


class ScarIndexLogger:
    """
    Logger for ScarIndex calculations to Supabase
    
    This hook appends coherence delta information after each ScarIndex
    calculation cycle to the scarindex_calculations table.
    """
    
    def __init__(self, supabase_url: Optional[str] = None, supabase_key: Optional[str] = None):
        """
        Initialize the ScarIndex logger
        
        Args:
            supabase_url: Supabase project URL (defaults to SUPABASE_URL env var)
            supabase_key: Supabase anon key (defaults to SUPABASE_ANON_KEY env var)
        """
        self.enabled = SUPABASE_AVAILABLE
        self.client: Optional[Client] = None
        
        if not self.enabled:
            return
        
        # Get credentials from environment or parameters
        self.url = supabase_url or os.getenv('SUPABASE_URL')
        self.key = supabase_key or os.getenv('SUPABASE_ANON_KEY')
        
        if not self.url or not self.key:
            print("WARNING: Supabase credentials not configured, logging disabled")
            self.enabled = False
            return
        
        try:
            self.client = create_client(self.url, self.key)
        except Exception as e:
            print(f"ERROR: Failed to initialize Supabase client: {e}")
            self.enabled = False
    
    def log_calculation(
        self,
        scarindex: float,
        coherence_delta: float,
        ache_before: float,
        ache_after: float,
        components: Optional[Dict[str, float]] = None,
        metadata: Optional[Dict] = None,
        timestamp: Optional[str] = None
    ) -> bool:
        """
        Log a ScarIndex calculation to Supabase
        
        Args:
            scarindex: Calculated ScarIndex value
            coherence_delta: Change in coherence (ache_before - ache_after)
            ache_before: Ache level before transmutation
            ache_after: Ache level after transmutation
            components: Optional coherence component scores
            metadata: Optional additional metadata
            timestamp: Optional timestamp (ISO format), defaults to current time
            
        Returns:
            True if successfully logged, False otherwise
        """
        if not self.enabled or not self.client:
            return False
        
        try:
            # Prepare record
            record = {
                'scarindex': scarindex,
                'coherence_delta': coherence_delta,
                'ache_before': ache_before,
                'ache_after': ache_after,
                'is_valid': ache_after < ache_before,  # Valid if Ache decreased (coherence increased)
                'timestamp': timestamp or datetime.now(timezone.utc).isoformat(),
                'components': components or {},
                'metadata': metadata or {}
            }
            
            # Insert into scarindex_calculations table
            result = self.client.table('scarindex_calculations').insert(record).execute()
            
            print(f"✓ Logged ScarIndex calculation: delta={coherence_delta:.4f}, scarindex={scarindex:.4f}")
            return True
            
        except Exception as e:
            print(f"ERROR: Failed to log ScarIndex calculation: {e}")
            return False
    
    def log_from_result(self, result) -> bool:
        """
        Log a ScarIndex calculation from a ScarIndexResult object
        
        Args:
            result: ScarIndexResult object from ScarIndexOracle.calculate()
            
        Returns:
            True if successfully logged, False otherwise
        """
        if not self.enabled:
            return False
        
        try:
            # Extract component values
            components = {
                'operational': result.components.operational,
                'audit': result.components.audit,
                'constitutional': result.components.constitutional,
                'symbolic': result.components.symbolic
            }
            
            # Calculate coherence delta
            coherence_delta = result.ache.coherence_gain
            
            # Log the calculation with original timestamp
            return self.log_calculation(
                scarindex=result.scarindex,
                coherence_delta=coherence_delta,
                ache_before=result.ache.before,
                ache_after=result.ache.after,
                components=components,
                metadata=result.metadata,
                timestamp=result.timestamp.isoformat()
            )
            
        except Exception as e:
            print(f"ERROR: Failed to log from ScarIndexResult: {e}")
            return False


# Global logger instance (lazy-initialized)
_global_logger: Optional[ScarIndexLogger] = None


def get_logger() -> ScarIndexLogger:
    """
    Get the global ScarIndex logger instance
    
    Returns:
        ScarIndexLogger instance
    """
    global _global_logger
    
    if _global_logger is None:
        _global_logger = ScarIndexLogger()
    
    return _global_logger


def log_scarindex_calculation(
    scarindex: float,
    coherence_delta: float,
    ache_before: float,
    ache_after: float,
    components: Optional[Dict[str, float]] = None,
    metadata: Optional[Dict] = None
) -> bool:
    """
    Convenience function to log a ScarIndex calculation
    
    This is the main hook function to be called after each calculation.
    
    Args:
        scarindex: Calculated ScarIndex value
        coherence_delta: Change in coherence (ache_before - ache_after)
        ache_before: Ache level before transmutation
        ache_after: Ache level after transmutation
        components: Optional coherence component scores
        metadata: Optional additional metadata
        
    Returns:
        True if successfully logged, False otherwise
    """
    logger = get_logger()
    return logger.log_calculation(
        scarindex=scarindex,
        coherence_delta=coherence_delta,
        ache_before=ache_before,
        ache_after=ache_after,
        components=components,
        metadata=metadata
    )


def log_scarindex_result(result) -> bool:
    """
    Convenience function to log from a ScarIndexResult object
    
    Args:
        result: ScarIndexResult object
        
    Returns:
        True if successfully logged, False otherwise
    """
    logger = get_logger()
    return logger.log_from_result(result)


if __name__ == '__main__':
    # Example usage
    print("ScarIndex Logger Example")
    print("=" * 70)
    
    logger = ScarIndexLogger()
    
    if logger.enabled:
        # Example log
        success = logger.log_calculation(
            scarindex=0.75,
            coherence_delta=0.25,
            ache_before=0.6,
            ache_after=0.35,
            components={
                'operational': 0.8,
                'audit': 0.7,
                'constitutional': 0.75,
                'symbolic': 0.65
            },
            metadata={'source': 'example', 'cycle': 1}
        )
        
        print(f"\nLogging {'successful' if success else 'failed'}")
    else:
        print("\nScarIndex logging is disabled (Supabase not configured)")
