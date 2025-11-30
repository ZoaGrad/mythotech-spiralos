import { Proposal, RiskLevel, SsdAssessment, SsdFinding, SsdDecision } from '../../shared/types.js';

const KEYWORD_FLAGS: Record<string, number> = {
  emergency: 20,
  bypass: 15,
  override: 15,
  unauthorized: 25,
  exploit: 25,
  breach: 25,
  backdoor: 25,
  expedite: 10
};

const CATEGORY_WEIGHTS: Record<string, number> = {
  treasury: 20,
  protocol_upgrade: 15,
  validator_policy: 10,
  governance_rule: 5
};

const IMPACT_RADIUS_WEIGHT = 0.75;
const AMOUNT_WEIGHT = 0.0001;

function addFinding(findings: SsdFinding[], tag: string, message: string, weight: number) {
  findings.push({ tag, message, weight });
}

function clampRisk(score: number): RiskLevel {
  if (score >= 70) return 'high';
  if (score >= 40) return 'medium';
  return 'low';
}

function classifyDecision(level: RiskLevel, findings: SsdFinding[]): SsdDecision {
  if (level === 'high') return 'reject';
  if (findings.some((f) => f.tag === 'integrity_gap')) return 'needs_human_review';
  if (findings.some((f) => f.tag === 'missing_context')) return 'needs_human_review';
  return 'approve';
}

export function evaluateProposal(proposal: Proposal): SsdAssessment {
  const findings: SsdFinding[] = [];
  let riskScore = 0;

  const description = `${proposal.title} ${proposal.body}`.toLowerCase();
  Object.entries(KEYWORD_FLAGS).forEach(([keyword, weight]) => {
    if (description.includes(keyword)) {
      riskScore += weight;
      addFinding(findings, 'keyword', `Detected sensitive keyword: ${keyword}`, weight);
    }
  });

  if (proposal.category && CATEGORY_WEIGHTS[proposal.category]) {
    const weight = CATEGORY_WEIGHTS[proposal.category];
    riskScore += weight;
    addFinding(findings, 'category', `High-impact category: ${proposal.category}`, weight);
  }

  if (proposal.amount && proposal.amount > 0) {
    const weight = Math.min(30, proposal.amount * AMOUNT_WEIGHT);
    riskScore += weight;
    if (weight >= 20) {
      addFinding(findings, 'treasury_drain', 'Large fund movement detected', weight);
    }
  }

  if (proposal.impact_radius && proposal.impact_radius > 0) {
    const weight = Math.min(25, proposal.impact_radius * IMPACT_RADIUS_WEIGHT);
    riskScore += weight;
    addFinding(findings, 'blast_radius', `Impact radius reported as ${proposal.impact_radius}`, weight);
  }

  if (!proposal.proposer) {
    riskScore += 10;
    addFinding(findings, 'integrity_gap', 'Missing proposer identity', 10);
  }

  if (!proposal.body || proposal.body.length < 50) {
    riskScore += 10;
    addFinding(findings, 'missing_context', 'Proposal description is too short for automated validation', 10);
  }

  const level = clampRisk(riskScore);
  const decision = classifyDecision(level, findings);

  return {
    riskScore,
    riskLevel: level,
    decision,
    findings,
    summary: `${decision} | risk=${riskScore.toFixed(1)} | findings=${findings.length}`,
    reviewedAt: new Date().toISOString()
  };
}
