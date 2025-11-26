export function computeScore(verdict, notes = '') {
  const normalized = verdict.toLowerCase();
  if (normalized === 'affirm') return 1;
  if (normalized === 'challenge') return -1;
  if (normalized === 'abstain') return 0;
  return notes.length > 10 ? 0.2 : 0;
}

export function reputationDelta(mode, score) {
  if (mode === 'stream') return { velocity: score };
  if (mode === 'crucible') return { density: score };
  return { gravity: score };
}
