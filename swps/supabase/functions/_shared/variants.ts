import type { WitnessMode } from '../../../shared/types.ts';

export const variantWitnessTargets: Record<WitnessMode, number> = {
  stream: 3,
  crucible: 5,
  council: 7,
};

export function validateStake(mode: WitnessMode, empStake: number): void {
  if (mode === 'crucible' && empStake <= 0) {
    throw new Error('Crucible witnesses require positive EMP stake');
  }
}
