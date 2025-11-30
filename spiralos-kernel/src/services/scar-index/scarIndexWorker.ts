import { env } from '../../shared/env.js';
import { logger } from '../../shared/logger.js';
import { withRetry } from '../../shared/retry.js';
import { supabase } from '../../shared/supabaseClient.js';
import { Event, ScarIndexState } from '../../shared/types.js';
import { computeScarIndex } from './scarIndexLogic.js';

const delay = (ms: number) => new Promise((resolve) => setTimeout(resolve, ms));

async function fetchRecentEvents(): Promise<Event[]> {
  const since = new Date(Date.now() - env.SCAR_INDEX_WINDOW_HOURS * 60 * 60 * 1000).toISOString();

  const response = await withRetry(() =>
    supabase
      .from('events')
      .select('*')
      .gte('occurred_at', since)
      .order('occurred_at', { ascending: true })
  );

  if (response.error) {
    throw response.error;
  }

  return response.data ?? [];
}

async function persistScarIndex(state: ScarIndexState) {
  const response = await withRetry(() =>
    supabase
      .from('scar_index_state')
      .upsert({
        id: 1,
        score: state.score,
        trend: state.trend,
        sample_size: state.sample_size,
        window_hours: state.window_hours,
        updated_at: state.updated_at
      })
  );

  if (response.error) {
    throw response.error;
  }
}

async function computeAndPersistScarIndex() {
  const events = await fetchRecentEvents();
  const scarIndex = computeScarIndex(events, env.SCAR_INDEX_WINDOW_HOURS);
  logger.info({ scarIndex, sample: events.length }, 'updated ScarIndex');
  await persistScarIndex(scarIndex);
}

export async function startScarIndexLoop(): Promise<never> {
  logger.info({ windowHours: env.SCAR_INDEX_WINDOW_HOURS, interval: env.SCAN_INTERVAL_MS }, 'starting ScarIndex loop');
  while (true) {
    try {
      await computeAndPersistScarIndex();
    } catch (error) {
      logger.error({ error }, 'failed to compute ScarIndex');
    }
    await delay(env.SCAN_INTERVAL_MS);
  }
}
