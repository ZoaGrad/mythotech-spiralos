"""
Financial Risk Mirror - Constitutional Stability Telemetry

Tracks ScarCoin volatility relative to underlying ScarIndex composite score,
transforming market risk signals into direct constitutional compliance telemetry.

This implements Strategic Directive #2 from Recursive Economist v1.3 Addendum:
"Deploy the ScarCoin Derivative Engine to create a Financial Risk Mirror that
provides real-time transparency."
"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from decimal import Decimal
from enum import Enum
import uuid
import statistics


class StabilityLevel(Enum):
    """Constitutional stability level"""
    CRITICAL = "critical"      # < 0.3
    UNSTABLE = "unstable"      # 0.3 - 0.5
    MODERATE = "moderate"      # 0.5 - 0.7
    STABLE = "stable"          # 0.7 - 0.9
    OPTIMAL = "optimal"        # > 0.9


class RiskLevel(Enum):
    """Market risk level"""
    EXTREME = "extreme"        # > 50% volatility
    HIGH = "high"              # 20-50% volatility
    MEDIUM = "medium"          # 10-20% volatility
    LOW = "low"                # 5-10% volatility
    MINIMAL = "minimal"        # < 5% volatility


@dataclass
class PriceDataPoint:
    """ScarCoin price data point"""
    timestamp: datetime = field(default_factory=datetime.utcnow)
    price: Decimal = Decimal('0')
    scarindex: Decimal = Decimal('0')
    volume: Decimal = Decimal('0')
    
    def to_dict(self) -> Dict:
        return {
            'timestamp': self.timestamp.isoformat(),
            'price': str(self.price),
            'scarindex': str(self.scarindex),
            'volume': str(self.volume)
        }


@dataclass
class VolatilityMetrics:
    """Volatility calculation metrics"""
    timestamp: datetime = field(default_factory=datetime.utcnow)
    
    # Price volatility
    price_volatility: Decimal = Decimal('0')  # Standard deviation / mean
    price_range: Decimal = Decimal('0')       # (max - min) / mean
    
    # ScarIndex volatility
    scarindex_volatility: Decimal = Decimal('0')
    scarindex_range: Decimal = Decimal('0')
    
    # Correlation
    price_scarindex_correlation: Decimal = Decimal('0')
    
    # Risk assessment
    risk_level: RiskLevel = RiskLevel.MINIMAL
    
    def to_dict(self) -> Dict:
        return {
            'timestamp': self.timestamp.isoformat(),
            'price_volatility': str(self.price_volatility),
            'price_range': str(self.price_range),
            'scarindex_volatility': str(self.scarindex_volatility),
            'scarindex_range': str(self.scarindex_range),
            'price_scarindex_correlation': str(self.price_scarindex_correlation),
            'risk_level': self.risk_level.value
        }


@dataclass
class ConstitutionalStabilityIndex:
    """
    Constitutional Stability Index (CSI)
    
    Combines ScarIndex, price volatility, and market sentiment to
    provide real-time constitutional compliance telemetry.
    """
    timestamp: datetime = field(default_factory=datetime.utcnow)
    
    # Core metrics
    scarindex: Decimal = Decimal('0')
    scarcoin_price: Decimal = Decimal('0')
    volatility: Decimal = Decimal('0')
    market_sentiment: Decimal = Decimal('0')  # -1 to 1
    
    # Composite score
    stability_score: Decimal = Decimal('0')  # 0 to 1
    stability_level: StabilityLevel = StabilityLevel.MODERATE
    
    # Prediction
    prediction_horizon_hours: int = 24
    predicted_scarindex: Decimal = Decimal('0')
    confidence: Decimal = Decimal('0')
    
    def calculate_stability_score(self) -> Decimal:
        """
        Calculate Constitutional Stability Score
        
        Formula:
        CSI = (0.4 * ScarIndex) + (0.3 * (1 - Volatility)) + 
              (0.2 * (1 + Sentiment)/2) + (0.1 * Price_Stability)
        """
        # Normalize components
        scarindex_component = self.scarindex * Decimal('0.4')
        
        volatility_component = (Decimal('1') - min(self.volatility, Decimal('1'))) * Decimal('0.3')
        
        sentiment_component = ((Decimal('1') + self.market_sentiment) / Decimal('2')) * Decimal('0.2')
        
        # Price stability (inverse of price volatility)
        price_stability = Decimal('1') - min(self.volatility, Decimal('1'))
        price_component = price_stability * Decimal('0.1')
        
        # Calculate composite
        score = scarindex_component + volatility_component + sentiment_component + price_component
        
        return max(Decimal('0'), min(Decimal('1'), score))
    
    def determine_stability_level(self, score: Decimal) -> StabilityLevel:
        """Determine stability level from score"""
        if score < Decimal('0.3'):
            return StabilityLevel.CRITICAL
        elif score < Decimal('0.5'):
            return StabilityLevel.UNSTABLE
        elif score < Decimal('0.7'):
            return StabilityLevel.MODERATE
        elif score < Decimal('0.9'):
            return StabilityLevel.STABLE
        else:
            return StabilityLevel.OPTIMAL
    
    def to_dict(self) -> Dict:
        return {
            'timestamp': self.timestamp.isoformat(),
            'scarindex': str(self.scarindex),
            'scarcoin_price': str(self.scarcoin_price),
            'volatility': str(self.volatility),
            'market_sentiment': str(self.market_sentiment),
            'stability_score': str(self.stability_score),
            'stability_level': self.stability_level.value,
            'prediction_horizon_hours': self.prediction_horizon_hours,
            'predicted_scarindex': str(self.predicted_scarindex),
            'confidence': str(self.confidence)
        }


class FinancialRiskMirror:
    """
    Financial Risk Mirror - Constitutional Stability Telemetry
    
    Tracks ScarCoin market dynamics and provides real-time signals
    about constitutional stability and compliance.
    """
    
    def __init__(
        self,
        window_size: int = 24,  # Hours of data to track
        update_interval: int = 1  # Hours between updates
    ):
        """Initialize Financial Risk Mirror"""
        self.window_size = window_size
        self.update_interval = update_interval
        
        # Price history
        self.price_history: List[PriceDataPoint] = []
        
        # Volatility tracking
        self.volatility_history: List[VolatilityMetrics] = []
        
        # Stability index
        self.stability_history: List[ConstitutionalStabilityIndex] = []
        
        # Current state
        self.current_price: Optional[Decimal] = None
        self.current_scarindex: Optional[Decimal] = None
        self.current_volatility: Optional[VolatilityMetrics] = None
        self.current_stability: Optional[ConstitutionalStabilityIndex] = None
    
    def record_price_data(
        self,
        price: Decimal,
        scarindex: Decimal,
        volume: Decimal = Decimal('0')
    ):
        """Record new price data point"""
        data_point = PriceDataPoint(
            price=price,
            scarindex=scarindex,
            volume=volume
        )
        
        self.price_history.append(data_point)
        self.current_price = price
        self.current_scarindex = scarindex
        
        # Trim history to window size
        cutoff_time = datetime.utcnow() - timedelta(hours=self.window_size)
        self.price_history = [
            dp for dp in self.price_history
            if dp.timestamp > cutoff_time
        ]
    
    def calculate_volatility(self) -> Optional[VolatilityMetrics]:
        """Calculate current volatility metrics"""
        if len(self.price_history) < 2:
            return None
        
        # Extract price and scarindex series
        prices = [float(dp.price) for dp in self.price_history]
        scarindices = [float(dp.scarindex) for dp in self.price_history]
        
        # Calculate price volatility
        price_mean = statistics.mean(prices)
        price_stdev = statistics.stdev(prices) if len(prices) > 1 else 0
        price_volatility = Decimal(str(price_stdev / price_mean if price_mean > 0 else 0))
        
        price_min, price_max = min(prices), max(prices)
        price_range = Decimal(str((price_max - price_min) / price_mean if price_mean > 0 else 0))
        
        # Calculate ScarIndex volatility
        scarindex_mean = statistics.mean(scarindices)
        scarindex_stdev = statistics.stdev(scarindices) if len(scarindices) > 1 else 0
        scarindex_volatility = Decimal(str(scarindex_stdev / scarindex_mean if scarindex_mean > 0 else 0))
        
        scarindex_min, scarindex_max = min(scarindices), max(scarindices)
        scarindex_range = Decimal(str((scarindex_max - scarindex_min) / scarindex_mean if scarindex_mean > 0 else 0))
        
        # Calculate correlation (simplified)
        correlation = Decimal('0.8')  # Simplified - production would use actual correlation
        
        # Determine risk level
        volatility_pct = price_volatility * Decimal('100')
        if volatility_pct > Decimal('50'):
            risk_level = RiskLevel.EXTREME
        elif volatility_pct > Decimal('20'):
            risk_level = RiskLevel.HIGH
        elif volatility_pct > Decimal('10'):
            risk_level = RiskLevel.MEDIUM
        elif volatility_pct > Decimal('5'):
            risk_level = RiskLevel.LOW
        else:
            risk_level = RiskLevel.MINIMAL
        
        metrics = VolatilityMetrics(
            price_volatility=price_volatility,
            price_range=price_range,
            scarindex_volatility=scarindex_volatility,
            scarindex_range=scarindex_range,
            price_scarindex_correlation=correlation,
            risk_level=risk_level
        )
        
        self.volatility_history.append(metrics)
        self.current_volatility = metrics
        
        return metrics
    
    def calculate_stability_index(
        self,
        market_sentiment: Decimal = Decimal('0')
    ) -> Optional[ConstitutionalStabilityIndex]:
        """Calculate Constitutional Stability Index"""
        if not self.current_price or not self.current_scarindex or not self.current_volatility:
            return None
        
        # Create stability index
        csi = ConstitutionalStabilityIndex(
            scarindex=self.current_scarindex,
            scarcoin_price=self.current_price,
            volatility=self.current_volatility.price_volatility,
            market_sentiment=market_sentiment
        )
        
        # Calculate stability score
        csi.stability_score = csi.calculate_stability_score()
        csi.stability_level = csi.determine_stability_level(csi.stability_score)
        
        # Simple prediction (production would use ML/statistical models)
        csi.predicted_scarindex = self.current_scarindex * Decimal('1.02')  # Assume 2% growth
        csi.confidence = Decimal('0.75')
        
        self.stability_history.append(csi)
        self.current_stability = csi
        
        return csi
    
    def get_risk_assessment(self) -> Dict:
        """Get current risk assessment"""
        if not self.current_volatility or not self.current_stability:
            return {
                'status': 'insufficient_data',
                'message': 'Need more price data to assess risk'
            }
        
        return {
            'status': 'active',
            'risk_level': self.current_volatility.risk_level.value,
            'stability_level': self.current_stability.stability_level.value,
            'stability_score': str(self.current_stability.stability_score),
            'price_volatility': str(self.current_volatility.price_volatility),
            'scarindex': str(self.current_scarindex),
            'recommendation': self._get_recommendation()
        }
    
    def _get_recommendation(self) -> str:
        """Get operational recommendation based on current state"""
        if not self.current_stability:
            return "Insufficient data"
        
        level = self.current_stability.stability_level
        
        if level == StabilityLevel.CRITICAL:
            return "CRITICAL: Activate F4 Panic Frames. System coherence at risk."
        elif level == StabilityLevel.UNSTABLE:
            return "WARNING: Increase F2 Judicial oversight. Monitor closely."
        elif level == StabilityLevel.MODERATE:
            return "CAUTION: Normal operations. Continue monitoring."
        elif level == StabilityLevel.STABLE:
            return "STABLE: System operating within constitutional parameters."
        else:  # OPTIMAL
            return "OPTIMAL: Excellent constitutional compliance. Consider growth initiatives."
    
    def get_mirror_stats(self) -> Dict:
        """Get Financial Risk Mirror statistics"""
        return {
            'window_size_hours': self.window_size,
            'data_points': len(self.price_history),
            'volatility_calculations': len(self.volatility_history),
            'stability_calculations': len(self.stability_history),
            'current_price': str(self.current_price) if self.current_price else None,
            'current_scarindex': str(self.current_scarindex) if self.current_scarindex else None,
            'current_risk_level': self.current_volatility.risk_level.value if self.current_volatility else None,
            'current_stability_level': self.current_stability.stability_level.value if self.current_stability else None
        }


# Example usage
def example_financial_risk_mirror():
    """Example of Financial Risk Mirror"""
    print("=" * 70)
    print("Financial Risk Mirror - Constitutional Stability Telemetry")
    print("=" * 70)
    print()
    
    # Initialize mirror
    mirror = FinancialRiskMirror(window_size=24)
    
    print("Initializing Financial Risk Mirror...")
    print(f"Window Size: {mirror.window_size} hours")
    print()
    
    # Simulate price data over time
    print("Recording price data (simulating 24 hours)...")
    print("-" * 70)
    
    import random
    base_price = Decimal('100')
    base_scarindex = Decimal('0.7')
    
    for hour in range(24):
        # Add some volatility
        price_change = Decimal(str(random.uniform(-0.05, 0.05)))
        scarindex_change = Decimal(str(random.uniform(-0.02, 0.02)))
        
        price = base_price * (Decimal('1') + price_change)
        scarindex = max(Decimal('0'), min(Decimal('1'), base_scarindex + scarindex_change))
        volume = Decimal(str(random.uniform(100, 1000)))
        
        mirror.record_price_data(price, scarindex, volume)
        
        base_price = price
        base_scarindex = scarindex
    
    print(f"✅ Recorded {len(mirror.price_history)} data points")
    print()
    
    # Calculate volatility
    print("Calculating volatility metrics...")
    print("-" * 70)
    
    volatility = mirror.calculate_volatility()
    if volatility:
        print(f"✅ Volatility calculated:")
        print(f"  Price Volatility: {volatility.price_volatility:.4f} ({volatility.price_volatility * 100:.2f}%)")
        print(f"  ScarIndex Volatility: {volatility.scarindex_volatility:.4f}")
        print(f"  Price/ScarIndex Correlation: {volatility.price_scarindex_correlation:.2f}")
        print(f"  Risk Level: {volatility.risk_level.value}")
        print()
    
    # Calculate stability index
    print("Calculating Constitutional Stability Index...")
    print("-" * 70)
    
    market_sentiment = Decimal('0.2')  # Slightly positive
    csi = mirror.calculate_stability_index(market_sentiment)
    
    if csi:
        print(f"✅ Constitutional Stability Index:")
        print(f"  ScarIndex: {csi.scarindex:.4f}")
        print(f"  ScarCoin Price: {csi.scarcoin_price:.2f}")
        print(f"  Volatility: {csi.volatility:.4f}")
        print(f"  Market Sentiment: {csi.market_sentiment:+.2f}")
        print(f"  Stability Score: {csi.stability_score:.4f}")
        print(f"  Stability Level: {csi.stability_level.value}")
        print(f"  Predicted ScarIndex (24h): {csi.predicted_scarindex:.4f}")
        print(f"  Confidence: {csi.confidence:.2f}")
        print()
    
    # Risk assessment
    print("=" * 70)
    print("Risk Assessment")
    print("=" * 70)
    
    assessment = mirror.get_risk_assessment()
    print(f"\nStatus: {assessment['status']}")
    print(f"Risk Level: {assessment['risk_level']}")
    print(f"Stability Level: {assessment['stability_level']}")
    print(f"Stability Score: {assessment['stability_score']}")
    print(f"\nRecommendation:")
    print(f"  {assessment['recommendation']}")
    
    # Mirror statistics
    print("\n" + "=" * 70)
    print("Mirror Statistics")
    print("=" * 70)
    
    stats = mirror.get_mirror_stats()
    print(f"\nData Points: {stats['data_points']}")
    print(f"Volatility Calculations: {stats['volatility_calculations']}")
    print(f"Stability Calculations: {stats['stability_calculations']}")
    print(f"Current Price: {stats['current_price']}")
    print(f"Current ScarIndex: {stats['current_scarindex']}")


if __name__ == '__main__':
    example_financial_risk_mirror()
