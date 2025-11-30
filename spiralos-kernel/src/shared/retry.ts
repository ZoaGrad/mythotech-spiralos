import { logger } from './logger.js';

export interface RetryOptions {
  attempts?: number;
  initialDelayMs?: number;
  factor?: number;
}

const wait = (ms: number) => new Promise((resolve) => setTimeout(resolve, ms));

export async function withRetry<T>(operation: () => PromiseLike<T>, options: RetryOptions = {}): Promise<T> {
  const attempts = options.attempts ?? 3;
  const factor = options.factor ?? 2;
  const initialDelayMs = options.initialDelayMs ?? 250;

  let lastError: unknown;
  for (let attempt = 1; attempt <= attempts; attempt += 1) {
    try {
      return await operation();
    } catch (error) {
      lastError = error;
      const delay = initialDelayMs * factor ** (attempt - 1);
      logger.warn({ attempt, delay, error }, 'retryable operation failed, scheduling retry');
      if (attempt < attempts) {
        await wait(delay);
      }
    }
  }

  logger.error({ error: lastError }, 'exhausted retries');
  throw lastError;
}
