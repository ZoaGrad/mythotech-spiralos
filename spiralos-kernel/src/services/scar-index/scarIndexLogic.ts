import { Event, ScarIndexState, Severity, Trend } from '../../shared/types.js';

const severityWeights: Record<Severity, number> = {
  low: 0.5,
  medium: 1,
  high: 2,
  critical: 3
};

export function computeScarIndex(events: Event[], windowHours: number): ScarIndexState {
  if (events.length === 0) {
    return {
      score: 0,
      trend: 'flat',
      sample_size: 0,
      window_hours: windowHours,
      updated_at: new Date().toISOString()
    };
  }

  const weightedImpact = events.reduce((acc, event) => {
    const base = severityWeights[event.severity] ?? 1;
    const impact = event.impact_score ?? 1;
    return acc + base * impact;
  }, 0);

  const normalizedScore = Math.min(100, (weightedImpact / events.length) * 10);

  const trend = normalizedScore >= 60 ? 'up' : normalizedScore <= 30 ? 'down' : 'flat';

  return {
    score: Number(normalizedScore.toFixed(2)),
    trend,
    sample_size: events.length,
    window_hours: windowHours,
    updated_at: new Date().toISOString()
  };
}
