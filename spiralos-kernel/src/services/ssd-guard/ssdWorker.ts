import { env } from '../../shared/env.js';
import { logger } from '../../shared/logger.js';
import { withRetry } from '../../shared/retry.js';
import { supabase } from '../../shared/supabaseClient.js';
import {
  Proposal,
  ProposalEvent,
  SsdAssessment,
  SsdErrorLog
} from '../../shared/types.js';
import { evaluateProposal } from './ssdLogic.js';

const delay = (ms: number) => new Promise((resolve) => setTimeout(resolve, ms));

async function fetchPendingProposals(): Promise<Proposal[]> {
  const response = await withRetry(() =>
    supabase
      .from('proposals')
      .select('*')
      .eq('status', 'pending')
      .order('created_at', { ascending: true })
      .limit(env.MAX_PROPOSALS_PER_SCAN)
  );

  if (response.error) {
    throw response.error;
  }

  return response.data ?? [];
}

async function recordProposalEvent(event: ProposalEvent) {
  const response = await withRetry(() => supabase.from('proposal_events').insert(event));
  if (response.error) {
    throw response.error;
  }
}

async function updateProposalWithAssessment(proposal: Proposal, assessment: SsdAssessment) {
  const status = assessment.decision === 'reject'
    ? 'rejected'
    : assessment.decision === 'needs_human_review'
      ? 'flagged'
      : 'approved';

  const updateResult = await withRetry(() =>
    supabase
      .from('proposals')
      .update({
        risk_score: assessment.riskScore,
        risk_level: assessment.riskLevel,
        ssd_decision: assessment.decision,
        findings: assessment.findings,
        status,
        reviewed_at: assessment.reviewedAt
      })
      .eq('id', proposal.id)
  );

  if (updateResult.error) {
    throw updateResult.error;
  }

  const event: ProposalEvent = {
    proposal_id: proposal.id,
    event_type: 'ssd_guard.assessed',
    payload: {
      decision: assessment.decision,
      risk_score: assessment.riskScore,
      risk_level: assessment.riskLevel,
      findings: assessment.findings,
      summary: assessment.summary
    }
  };

  await recordProposalEvent(event);
}

async function logSsdError(entry: SsdErrorLog) {
  const response = await withRetry(() => supabase.from('ssd_errors').insert(entry));
  if (response.error) {
    logger.error({ error: response.error, entry }, 'failed to record ssd error');
  }
}

async function processProposal(proposal: Proposal) {
  const assessment = evaluateProposal(proposal);
  logger.info({ proposal_id: proposal.id, assessment }, 'assessed proposal');
  await updateProposalWithAssessment(proposal, assessment);
}

async function scanOnce() {
  const proposals = await fetchPendingProposals();
  if (proposals.length === 0) {
    logger.debug('no pending proposals');
    return;
  }

  for (const proposal of proposals) {
    try {
      await processProposal(proposal);
    } catch (error) {
      logger.error({ proposal_id: proposal.id, error }, 'failed to process proposal');
      await logSsdError({
        proposal_id: proposal.id,
        error_message: error instanceof Error ? error.message : 'unknown error',
        stacktrace: error instanceof Error ? error.stack : undefined,
        context: { proposal_id: proposal.id }
      });
    }
  }
}

export async function startSsdGuardLoop(): Promise<never> {
  logger.info({ interval: env.SCAN_INTERVAL_MS, batch: env.MAX_PROPOSALS_PER_SCAN }, 'starting SSD Guard loop');
  while (true) {
    try {
      await scanOnce();
    } catch (error) {
      logger.error({ error }, 'scan iteration failed');
      await logSsdError({ error_message: error instanceof Error ? error.message : 'unknown error', stacktrace: error instanceof Error ? error.stack : undefined });
    }
    await delay(env.SCAN_INTERVAL_MS);
  }
}
