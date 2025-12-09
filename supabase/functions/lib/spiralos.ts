// Shared types and tiny helpers for SpiralOS Edge Functions

/**
 * Computes SHA-256 hash of input string and returns hex string
 */
export async function sha256(message: string): Promise<string> {
  const msgBuffer = new TextEncoder().encode(message);
  const hashBuffer = await crypto.subtle.digest("SHA-256", msgBuffer);
  const hashArray = Array.from(new Uint8Array(hashBuffer));
  const hashHex = hashArray.map((b) => b.toString(16).padStart(2, "0")).join("");
  return hashHex;
}

/**
 * Converts first 8 hex chars of hash to 0-1 float
 * Takes first 8 hex chars, converts to integer, divides by 0xffffffff
 */
export function floatFromHash(hexHash: string): number {
  const first8 = hexHash.substring(0, 8);
  const intValue = parseInt(first8, 16);
  return intValue / 0xffffffff;
}

/**
 * Common types for vault nodes
 */
export interface VaultNode {
  id?: string;
  content_type: string;
  content_ref: any;
  merkle_root: string;
  signature: string;
  created_at?: string;
  previous_node_hash?: string;
}

/**
 * Common types for witness events
 */
export interface WitnessEvent {
  id?: string;
  event_type: string;
  resonance?: number;
  payload?: any;
  created_at?: string;
}

/**
 * Common types for scar index snapshots
 */
export interface ScarIndexSnapshot {
  id?: string;
  coherence_score: number;
  timestamp: string;
  snapshot_hash: string;
  mean_resonance?: number;
  chain_integrity_ratio?: number;
}
