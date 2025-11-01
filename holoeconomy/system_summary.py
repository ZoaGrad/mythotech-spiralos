"""
System Summary Module

Provides comprehensive system-wide status aggregation across all SpiralOS components:
- Core SpiralOS (ScarIndex, Panic Frames, PID Controller)
- Holo-Economy (ScarCoin supply, minting operations)
- Empathy Market (EMP tokens, resonance events)
- VaultNode (blockchain health, consensus status)

This module serves as a unified dashboard for system health monitoring and telemetry.
"""

from typing import Dict, Optional
from datetime import datetime
from decimal import Decimal


class SystemSummary:
    """
    Aggregates system-wide status from all SpiralOS components
    
    Provides a unified view of:
    - Economic health (ScarCoin + EMP metrics)
    - Blockchain integrity (VaultNode status)
    - System coherence (ScarIndex metrics)
    - Operational status (transmutations, activations)
    """
    
    def __init__(
        self,
        minting_engine=None,
        empathy_market=None,
        vaultnode=None,
        spiralos_core=None
    ):
        """
        Initialize SystemSummary with component references
        
        Args:
            minting_engine: ScarCoinMintingEngine instance (optional)
            empathy_market: EmpathyMarket instance (optional)
            vaultnode: VaultNode instance (optional)
            spiralos_core: SpiralOS core system instance (optional)
        """
        self.minting_engine = minting_engine
        self.empathy_market = empathy_market
        self.vaultnode = vaultnode
        self.spiralos_core = spiralos_core
    
    def get_summary(self) -> Dict:
        """
        Get comprehensive system summary
        
        Returns:
            Dictionary containing aggregated system status from all components
        """
        summary = {
            'system': {
                'name': 'SpiralOS',
                'version': '1.3.0-alpha',
                'vault_id': self.vaultnode.vault_id if self.vaultnode else 'N/A',
                'timestamp': datetime.utcnow().isoformat(),
                'status': self._determine_overall_status()
            },
            'components': {
                'core': self._get_core_summary(),
                'scarcoin': self._get_scarcoin_summary(),
                'empathy_market': self._get_empathy_summary(),
                'vaultnode': self._get_vaultnode_summary()
            },
            'health': self._calculate_health_metrics(),
            'motto': "Where coherence becomes currency 🜂"
        }
        
        return summary
    
    def _get_core_summary(self) -> Dict:
        """Get core SpiralOS component summary"""
        if not self.spiralos_core:
            return {'available': False}
        
        status = self.spiralos_core.get_system_status()
        
        return {
            'available': True,
            'coherence': {
                'current_scarindex': status['coherence']['current_scarindex'],
                'target_scarindex': status['coherence']['target_scarindex'],
                'status': status['coherence']['status']
            },
            'transmutations': {
                'total': status['transmutations']['total'],
                'successful': status['transmutations']['successful'],
                'success_rate': f"{status['transmutations']['success_rate']:.2%}"
            },
            'panic_frames': {
                'active_count': status['panic_frames']['active_count'],
                'total_activations': status['panic_frames']['total_activations']
            },
            'pid_controller': {
                'guidance_scale': status['pid_controller']['guidance_scale']
            }
        }
    
    def _get_scarcoin_summary(self) -> Dict:
        """Get ScarCoin economy summary"""
        if not self.minting_engine:
            return {'available': False}
        
        stats = self.minting_engine.get_supply_stats()
        
        return {
            'available': True,
            'supply': {
                'total_supply': stats['total_supply'],
                'total_minted': stats['total_minted'],
                'total_burned': stats['total_burned'],
                'circulating': str(
                    Decimal(stats['total_minted']) - Decimal(stats['total_burned'])
                )
            },
            'activity': {
                'minting_count': stats['minting_count'],
                'burning_count': stats['burning_count'],
                'active_wallets': stats['active_wallets'],
                'total_coins': stats['total_coins']
            }
        }
    
    def _get_empathy_summary(self) -> Dict:
        """Get Empathy Market summary"""
        if not self.empathy_market:
            return {'available': False}
        
        stats = self.empathy_market.get_market_stats()
        
        return {
            'available': True,
            'tokens': {
                'total_emp_minted': stats['total_emp_minted'],
                'total_resonance_events': stats['total_resonance_events'],
                'average_emp_per_event': stats['average_emp_per_event']
            },
            'participation': {
                'total_participants': stats['total_participants']
            },
            'thresholds': {
                'consensus_threshold': stats['consensus_threshold'],
                'min_resonance_surplus': stats['min_resonance_surplus']
            }
        }
    
    def _get_vaultnode_summary(self) -> Dict:
        """Get VaultNode blockchain summary"""
        if not self.vaultnode:
            return {'available': False}
        
        stats = self.vaultnode.get_chain_stats()
        
        return {
            'available': True,
            'blockchain': {
                'vault_id': stats['vault_id'],
                'total_blocks': stats['total_blocks'],
                'total_events': stats['total_events'],
                'latest_block_number': stats['latest_block_number'],
                'chain_valid': stats['chain_valid']
            },
            'pending': {
                'pending_events': stats['pending_events']
            }
        }
    
    def _determine_overall_status(self) -> str:
        """
        Determine overall system status based on component health
        
        Returns:
            Status string: OPTIMAL, OPERATIONAL, DEGRADED, or CRITICAL
        """
        # Check if core components are available
        components_available = sum([
            self.spiralos_core is not None,
            self.minting_engine is not None,
            self.vaultnode is not None
        ])
        
        # Check for critical conditions
        if self.spiralos_core:
            status = self.spiralos_core.get_system_status()
            if status['system']['status'] == 'PANIC_MODE':
                return 'CRITICAL'
            if status['panic_frames']['active_count'] > 0:
                return 'DEGRADED'
        
        if self.vaultnode:
            if not self.vaultnode.verify_chain():
                return 'CRITICAL'
        
        # Determine status based on component availability
        if components_available == 0:
            return 'UNAVAILABLE'
        elif components_available < 2:
            return 'DEGRADED'
        else:
            return 'OPERATIONAL'
    
    def _calculate_health_metrics(self) -> Dict:
        """
        Calculate aggregate health metrics across all components
        
        Returns:
            Dictionary of health scores and indicators
        """
        health = {
            'blockchain_integrity': False,
            'economic_activity': 'unknown',
            'coherence_status': 'unknown',
            'overall_score': 0.0
        }
        
        score_components = []
        
        # Blockchain health (25% weight)
        if self.vaultnode:
            blockchain_valid = self.vaultnode.verify_chain()
            health['blockchain_integrity'] = blockchain_valid
            score_components.append(1.0 if blockchain_valid else 0.0)
        
        # Economic activity (25% weight)
        if self.minting_engine:
            stats = self.minting_engine.get_supply_stats()
            total_activity = stats['minting_count'] + stats['burning_count']
            if total_activity > 100:
                health['economic_activity'] = 'high'
                score_components.append(1.0)
            elif total_activity > 10:
                health['economic_activity'] = 'moderate'
                score_components.append(0.7)
            else:
                health['economic_activity'] = 'low'
                score_components.append(0.4)
        
        # Coherence status (25% weight)
        if self.spiralos_core:
            status = self.spiralos_core.get_system_status()
            coherence_status = status['coherence']['status']
            health['coherence_status'] = coherence_status
            
            # Map coherence status to score
            coherence_score = {
                'OPTIMAL': 1.0,
                'STRONG': 0.8,
                'MODERATE': 0.6,
                'WEAK': 0.4,
                'CRITICAL': 0.2
            }.get(coherence_status, 0.5)
            score_components.append(coherence_score)
        
        # System availability (25% weight)
        components_count = sum([
            self.spiralos_core is not None,
            self.minting_engine is not None,
            self.empathy_market is not None,
            self.vaultnode is not None
        ])
        availability_score = components_count / 4.0
        score_components.append(availability_score)
        
        # Calculate overall score (0-1 scale)
        if score_components:
            health['overall_score'] = sum(score_components) / len(score_components)
        
        return health
    
    def get_quick_status(self) -> str:
        """
        Get a quick one-line status summary
        
        Returns:
            Human-readable status string
        """
        summary = self.get_summary()
        status = summary['system']['status']
        health_score = summary['health']['overall_score']
        
        scarcoin_supply = "N/A"
        emp_minted = "N/A"
        blocks = "N/A"
        
        if summary['components']['scarcoin']['available']:
            scarcoin_supply = summary['components']['scarcoin']['supply']['circulating']
        
        if summary['components']['empathy_market']['available']:
            emp_minted = summary['components']['empathy_market']['tokens']['total_emp_minted']
        
        if summary['components']['vaultnode']['available']:
            blocks = summary['components']['vaultnode']['blockchain']['total_blocks']
        
        return (
            f"SpiralOS v1.3-alpha | Status: {status} | "
            f"Health: {health_score:.0%} | "
            f"SCAR: {scarcoin_supply} | EMP: {emp_minted} | "
            f"Blocks: {blocks}"
        )


def create_summary_from_engines(
    minting_engine=None,
    empathy_market=None,
    vaultnode=None,
    spiralos_core=None
) -> Dict:
    """
    Convenience function to create summary from engine instances
    
    Args:
        minting_engine: ScarCoinMintingEngine instance
        empathy_market: EmpathyMarket instance
        vaultnode: VaultNode instance
        spiralos_core: SpiralOS core instance
    
    Returns:
        System summary dictionary
    """
    summarizer = SystemSummary(
        minting_engine=minting_engine,
        empathy_market=empathy_market,
        vaultnode=vaultnode,
        spiralos_core=spiralos_core
    )
    
    return summarizer.get_summary()


# Example usage
def example_system_summary():
    """Example of system summary generation"""
    from scarcoin import ScarCoinMintingEngine
    from empathy_market import EmpathyMarket
    from vaultnode import VaultNode
    
    print("=" * 70)
    print("System Summary - Comprehensive System Overview")
    print("=" * 70)
    print()
    
    # Initialize components
    minting_engine = ScarCoinMintingEngine()
    empathy_market = EmpathyMarket()
    vaultnode = VaultNode(vault_id="ΔΩ.123.0")
    
    # Create summary
    summarizer = SystemSummary(
        minting_engine=minting_engine,
        empathy_market=empathy_market,
        vaultnode=vaultnode
    )
    
    # Get quick status
    print("Quick Status:")
    print("-" * 70)
    print(summarizer.get_quick_status())
    print()
    
    # Get full summary
    print("Full Summary:")
    print("-" * 70)
    summary = summarizer.get_summary()
    
    import json
    print(json.dumps(summary, indent=2))
    print()
    
    print("=" * 70)
    print("Summary generated successfully 🜂")
    print("=" * 70)


if __name__ == "__main__":
    example_system_summary()
