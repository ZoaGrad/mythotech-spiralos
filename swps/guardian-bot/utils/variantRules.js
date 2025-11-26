export const requiredWitnesses = {
  stream: 3,
  crucible: 5,
  council: 7,
};

export function escalationTarget(mode, resonance) {
  if (mode === 'stream' && resonance > 0.7) return 'crucible';
  if (mode === 'crucible' && resonance > 0.9) return 'council';
  return mode;
}
