export type Severity = 'low' | 'medium' | 'high' | 'critical';
export type RiskLevel = 'low' | 'medium' | 'high';
export type Trend = 'up' | 'down' | 'flat';
export type ProposalStatus = 'pending' | 'approved' | 'flagged' | 'rejected' | 'in_review';
export type SsdDecision = 'approve' | 'reject' | 'needs_human_review';

export interface Witness {
  id: string;
  name: string;
  public_key: string;
  reputation_score?: number;
  created_at: string;
}

export interface Event {
  id: string;
  type: string;
  severity: Severity;
  description?: string;
  metadata?: Record<string, unknown>;
  impact_score?: number;
  occurred_at?: string;
  created_at: string;
  witnessed_by?: string | null;
}

export interface Proposal {
  id: string;
  title: string;
  body: string;
  proposer?: string | null;
  category?: string | null;
  impact_radius?: number | null;
  amount?: number | null;
  status: ProposalStatus;
  risk_score?: number | null;
  risk_level?: RiskLevel | null;
  ssd_decision?: SsdDecision | null;
  findings?: SsdFinding[] | null;
  created_at: string;
  reviewed_at?: string | null;
}

export interface ProposalEvent {
  id?: number;
  proposal_id: string;
  event_type: string;
  payload: Record<string, unknown>;
  created_at?: string;
}

export interface ScarIndexState {
  id?: number;
  score: number;
  trend: Trend;
  sample_size: number;
  window_hours: number;
  updated_at?: string;
}

export interface SsdFinding {
  tag: string;
  message: string;
  weight: number;
}

export interface SsdAssessment {
  riskScore: number;
  riskLevel: RiskLevel;
  decision: SsdDecision;
  findings: SsdFinding[];
  summary: string;
  reviewedAt: string;
}

export interface SsdErrorLog {
  id?: number;
  proposal_id?: string | null;
  error_message: string;
  stacktrace?: string | null;
  context?: Record<string, unknown>;
  created_at?: string;
}
