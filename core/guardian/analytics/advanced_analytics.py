#!/usr/bin/env python3
"""
SpiralOS Guardian - Advanced Analytics Module
Provides predictive analytics, AI summaries, and visual dashboards.
"""

import asyncio
import os
import tempfile
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from scipy import stats

try:
    from openai import OpenAI

    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False


@dataclass
class TrendAnalysis:
    """Results of trend analysis."""

    trend_direction: str  # 'improving', 'stable', 'degrading'
    slope: float
    r_squared: float
    current_value: float
    avg_value: float
    min_value: float
    max_value: float
    data_points: int
    forecast_24h: Optional[float] = None
    confidence_interval: Optional[Tuple[float, float]] = None


@dataclass
class CoherenceBreakdown:
    """Coherence component breakdown."""

    narrative: float
    social: float
    economic: float
    technical: float
    weighted_narrative: float
    weighted_social: float
    weighted_economic: float
    weighted_technical: float
    total_scarindex: float


class GuardianAnalytics:
    """Advanced analytics for Guardian system."""

    def __init__(self, supabase_url: str, supabase_key: str):
        """Initialize analytics module."""
        self.supabase_url = supabase_url
        self.supabase_key = supabase_key
        self.openai_client = None

        if OPENAI_AVAILABLE and os.getenv("OPENAI_API_KEY"):
            self.openai_client = OpenAI()

    async def fetch_scarindex_history(self, hours: int = 168) -> pd.DataFrame:
        """Fetch ScarIndex calculation history."""
        import aiohttp

        since = datetime.now(timezone.utc) - timedelta(hours=hours)
        url = f"{self.supabase_url}/rest/v1/scarindex_calculations"
        params = {
            "select": "value,c_narrative,c_social,c_economic,c_technical,created_at",
            "created_at": f"gte.{since.isoformat()}",
            "order": "created_at.asc",
        }
        headers = {"apikey": self.supabase_key, "Authorization": f"Bearer {self.supabase_key}"}

        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params, headers=headers) as response:
                if response.status != 200:
                    raise Exception(f"Failed to fetch data: {response.status}")

                data = await response.json()

        if not data:
            return pd.DataFrame()

        df = pd.DataFrame(data)
        df["created_at"] = pd.to_datetime(df["created_at"])
        df = df.sort_values("created_at")

        return df

    def analyze_trend(self, df: pd.DataFrame) -> TrendAnalysis:
        """Analyze ScarIndex trend with linear regression."""
        if len(df) < 5:
            raise ValueError("Need at least 5 data points for trend analysis")

        # Prepare data
        values = df["value"].values
        x = np.arange(len(values))

        # Linear regression
        slope, intercept, r_value, p_value, std_err = stats.linregress(x, values)

        # Determine trend direction
        if slope > 0.01:
            trend_direction = "improving"
        elif slope < -0.01:
            trend_direction = "degrading"
        else:
            trend_direction = "stable"

        # Forecast 24 hours ahead (assuming hourly data)
        forecast_steps = 24
        forecast_x = len(values) + forecast_steps
        forecast_value = slope * forecast_x + intercept

        # Calculate confidence interval (95%)
        # Using standard error of the estimate
        residuals = values - (slope * x + intercept)
        se = np.sqrt(np.sum(residuals**2) / (len(values) - 2))
        t_val = stats.t.ppf(0.975, len(values) - 2)  # 95% confidence
        margin = (
            t_val * se * np.sqrt(1 + 1 / len(values) + (forecast_x - np.mean(x)) ** 2 / np.sum((x - np.mean(x)) ** 2))
        )

        confidence_interval = (forecast_value - margin, forecast_value + margin)

        return TrendAnalysis(
            trend_direction=trend_direction,
            slope=slope,
            r_squared=r_value**2,
            current_value=float(values[-1]),
            avg_value=float(np.mean(values)),
            min_value=float(np.min(values)),
            max_value=float(np.max(values)),
            data_points=len(values),
            forecast_24h=float(forecast_value),
            confidence_interval=(float(confidence_interval[0]), float(confidence_interval[1])),
        )

    def analyze_coherence_breakdown(self, df: pd.DataFrame) -> CoherenceBreakdown:
        """Analyze coherence component breakdown."""
        if len(df) == 0:
            raise ValueError("No data available for coherence analysis")

        # Get latest values
        latest = df.iloc[-1]

        narrative = float(latest["c_narrative"])
        social = float(latest["c_social"])
        economic = float(latest["c_economic"])
        technical = float(latest["c_technical"])

        # Calculate weighted contributions
        weighted_narrative = narrative * 0.30
        weighted_social = social * 0.25
        weighted_economic = economic * 0.25
        weighted_technical = technical * 0.20

        total = weighted_narrative + weighted_social + weighted_economic + weighted_technical

        return CoherenceBreakdown(
            narrative=narrative,
            social=social,
            economic=economic,
            technical=technical,
            weighted_narrative=weighted_narrative,
            weighted_social=weighted_social,
            weighted_economic=weighted_economic,
            weighted_technical=weighted_technical,
            total_scarindex=total,
        )

    def detect_anomalies(self, df: pd.DataFrame, threshold: float = 2.0) -> List[Dict[str, Any]]:
        """Detect anomalies using z-score method."""
        if len(df) < 10:
            return []

        values = df["value"].values
        mean = np.mean(values)
        std = np.std(values)

        anomalies = []
        for idx, row in df.iterrows():
            z_score = abs((row["value"] - mean) / std) if std > 0 else 0

            if z_score > threshold:
                anomalies.append(
                    {
                        "timestamp": row["created_at"].isoformat(),
                        "value": float(row["value"]),
                        "z_score": float(z_score),
                        "deviation": float(row["value"] - mean),
                    }
                )

        return anomalies

    def generate_ai_summary(self, trend: TrendAnalysis, breakdown: CoherenceBreakdown) -> str:
        """Generate AI-powered natural language summary."""
        if not self.openai_client:
            return self._generate_template_summary(trend, breakdown)

        prompt = f"""
You are the SpiralOS Guardian, an AI system monitor for a constitutional cognitive sovereignty platform.

Analyze the following system metrics and provide a concise, human-readable summary:

**Trend Analysis:**
- Direction: {trend.trend_direction}
- Current ScarIndex: {trend.current_value:.3f}
- Average: {trend.avg_value:.3f}
  - 24h Forecast: {trend.forecast_24h:.3f}
    (confidence: {trend.confidence_interval[0]:.3f} - {trend.confidence_interval[1]:.3f})
- Data points: {trend.data_points}

**Coherence Breakdown:**
- Narrative: {breakdown.narrative:.3f} (weighted: {breakdown.weighted_narrative:.3f})
- Social: {breakdown.social:.3f} (weighted: {breakdown.weighted_social:.3f})
- Economic: {breakdown.economic:.3f} (weighted: {breakdown.weighted_economic:.3f})
- Technical: {breakdown.technical:.3f} (weighted: {breakdown.weighted_technical:.3f})

Provide:
1. A brief status summary (2-3 sentences)
2. Key insights about coherence components
3. Recommendations if any concerns exist

Keep the tone professional but accessible. Target: 0.70 ScarIndex, Panic threshold: 0.30."""

        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4.1-mini",
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are the SpiralOS Guardian AI, providing clear and actionable system health summaries."
                        ),
                    },
                    {"role": "user", "content": prompt},
                ],
                max_tokens=500,
                temperature=0.7,
            )

            return response.choices[0].message.content.strip()

        except Exception as e:
            print(f"AI summary generation failed: {e}")
            return self._generate_template_summary(trend, breakdown)

    def _generate_template_summary(self, trend: TrendAnalysis, breakdown: CoherenceBreakdown) -> str:
        """Generate template-based summary when AI is unavailable."""
        status = {
            "improving": "📈 System coherence is improving",
            "stable": "➡️ System coherence is stable",
            "degrading": "📉 System coherence is degrading",
        }.get(trend.trend_direction, "Status unknown")

        summary = f"""**{status}**

Current ScarIndex: {trend.current_value:.3f} (target: 0.70)
24-hour forecast: {trend.forecast_24h:.3f}

**Coherence Components:**
- Narrative: {breakdown.narrative:.3f} (strongest)
- Social: {breakdown.social:.3f}
- Economic: {breakdown.economic:.3f}
- Technical: {breakdown.technical:.3f}

"""

        if trend.current_value < 0.30:
            summary += "⚠️ **CRITICAL:** ScarIndex below panic threshold. Immediate attention required.\n"
        elif trend.current_value < 0.60:
            summary += "⚠️ **WARNING:** ScarIndex below healthy range. Monitor closely.\n"
        elif trend.current_value >= 1.4:
            summary += "⚠️ **WARNING:** ScarIndex above healthy range. System may be overheating.\n"
        else:
            summary += "✅ System operating within healthy parameters.\n"

        return summary

    def create_scarindex_chart(self, df: pd.DataFrame, output_path: str) -> str:
        """Create ScarIndex time series chart."""
        fig = go.Figure()

        # Add ScarIndex line
        fig.add_trace(
            go.Scatter(
                x=df["created_at"],
                y=df["value"],
                mode="lines+markers",
                name="ScarIndex",
                line=dict(color="#3498db", width=2),
                marker=dict(size=4),
            )
        )

        # Add target line
        fig.add_hline(y=0.70, line_dash="dash", line_color="green", annotation_text="Target (0.70)")

        # Add panic threshold
        fig.add_hline(y=0.30, line_dash="dash", line_color="red", annotation_text="Panic Threshold (0.30)")

        # Add healthy range
        fig.add_hrect(
            y0=0.60,
            y1=1.40,
            fillcolor="green",
            opacity=0.1,
            annotation_text="Healthy Range",
            annotation_position="top left",
        )

        fig.update_layout(
            title="SpiralOS ScarIndex Over Time",
            xaxis_title="Time",
            yaxis_title="ScarIndex",
            hovermode="x unified",
            template="plotly_white",
            height=500,
        )

        fig.write_html(output_path)
        return output_path

    def create_coherence_breakdown_chart(self, df: pd.DataFrame, output_path: str) -> str:
        """Create coherence component breakdown chart."""
        # Get latest values
        latest = df.iloc[-1]

        components = ["Narrative", "Social", "Economic", "Technical"]
        values = [
            float(latest["c_narrative"]),
            float(latest["c_social"]),
            float(latest["c_economic"]),
            float(latest["c_technical"]),
        ]
        weights = [0.30, 0.25, 0.25, 0.20]
        weighted_values = [v * w for v, w in zip(values, weights)]

        fig = make_subplots(
            rows=1,
            cols=2,
            subplot_titles=("Component Values", "Weighted Contributions"),
            specs=[[{"type": "bar"}, {"type": "pie"}]],
        )

        # Bar chart
        fig.add_trace(
            go.Bar(
                x=components, y=values, name="Raw Values", marker_color=["#e74c3c", "#3498db", "#2ecc71", "#f39c12"]
            ),
            row=1,
            col=1,
        )

        # Pie chart
        fig.add_trace(
            go.Pie(
                labels=components, values=weighted_values, marker_colors=["#e74c3c", "#3498db", "#2ecc71", "#f39c12"]
            ),
            row=1,
            col=2,
        )

        fig.update_layout(title="Coherence Component Breakdown", showlegend=False, height=400, template="plotly_white")

        fig.write_html(output_path)
        return output_path

    def create_component_history_chart(self, df: pd.DataFrame, output_path: str) -> str:
        """Create historical chart of all coherence components."""
        fig = go.Figure()

        components = [
            ("c_narrative", "Narrative (30%)", "#e74c3c"),
            ("c_social", "Social (25%)", "#3498db"),
            ("c_economic", "Economic (25%)", "#2ecc71"),
            ("c_technical", "Technical (20%)", "#f39c12"),
        ]

        for col, label, color in components:
            fig.add_trace(
                go.Scatter(x=df["created_at"], y=df[col], mode="lines", name=label, line=dict(color=color, width=2))
            )

        fig.update_layout(
            title="Coherence Components Over Time",
            xaxis_title="Time",
            yaxis_title="Component Value",
            hovermode="x unified",
            template="plotly_white",
            height=500,
        )

        fig.write_html(output_path)
        return output_path

    def create_dashboard(self, df: pd.DataFrame, output_dir: str) -> Dict[str, str]:
        """Create complete visual dashboard."""
        os.makedirs(output_dir, exist_ok=True)

        charts = {}

        # ScarIndex time series
        charts["scarindex"] = self.create_scarindex_chart(df, os.path.join(output_dir, "scarindex_timeseries.html"))

        # Coherence breakdown
        charts["breakdown"] = self.create_coherence_breakdown_chart(
            df, os.path.join(output_dir, "coherence_breakdown.html")
        )

        # Component history
        charts["history"] = self.create_component_history_chart(df, os.path.join(output_dir, "component_history.html"))

        return charts


async def main():
    """Example usage."""
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

    if not supabase_url or not supabase_key:
        print("Error: SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY required")
        return

    analytics = GuardianAnalytics(supabase_url, supabase_key)

    # Fetch data
    print("Fetching ScarIndex history...")
    df = await analytics.fetch_scarindex_history(hours=168)  # 7 days

    if len(df) == 0:
        print("No data available")
        return

    print(f"Fetched {len(df)} data points")

    # Analyze trend
    print("\nAnalyzing trend...")
    trend = analytics.analyze_trend(df)
    print(f"Trend: {trend.trend_direction}")
    print(f"Current: {trend.current_value:.3f}")
    print(f"Forecast (24h): {trend.forecast_24h:.3f}")

    # Analyze coherence
    print("\nAnalyzing coherence breakdown...")
    breakdown = analytics.analyze_coherence_breakdown(df)
    print(f"Narrative: {breakdown.narrative:.3f}")
    print(f"Social: {breakdown.social:.3f}")
    print(f"Economic: {breakdown.economic:.3f}")
    print(f"Technical: {breakdown.technical:.3f}")

    # Generate AI summary
    print("\nGenerating AI summary...")
    summary = analytics.generate_ai_summary(trend, breakdown)
    print(summary)

    # Create dashboard
    print("\nCreating visual dashboard...")
    dashboard_dir = tempfile.mkdtemp(prefix="guardian_dashboard_")
    charts = analytics.create_dashboard(df, dashboard_dir)
    print(f"Dashboard created in {dashboard_dir}: {charts}")

    # Detect anomalies
    print("\nDetecting anomalies...")
    anomalies = analytics.detect_anomalies(df)
    print(f"Found {len(anomalies)} anomalies")
    for anomaly in anomalies[:5]:  # Show first 5
        print(f"  - {anomaly['timestamp']}: {anomaly['value']:.3f} (z-score: {anomaly['z_score']:.2f})")


if __name__ == "__main__":
    asyncio.run(main())
