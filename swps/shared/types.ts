export type WitnessMode = 'stream' | 'crucible' | 'council';

export interface ReputationVector {
  velocity: number; // Stream throughput
  density: number; // Crucible reliability
  gravity: number; // Council wisdom
}

export interface WitnessEvent {
  id: string;
  initiator: string | null;
  target: string | null;
  mode: WitnessMode;
  payload: Record<string, unknown>;
  emp_stake: number;
  reputation_cost: number;
  resonance: number;
  status: 'pending' | 'assigned' | 'assessing' | 'finalized' | 'escalated' | 'rejected';
  required_witnesses: number;
  created_at: string;
  updated_at: string;
}

export interface Assessment {
  id: string;
  event_id: string;
  witness_id: string;
  verdict: string;
  notes?: string;
  score: number;
  created_at: string;
}

export interface AncestryEdge {
  id: string;
  parent_event: string;
  child_event: string;
  weight: number;
  permanence: boolean;
  decay_rate?: number | null;
  created_at: string;
}
