import { config } from 'dotenv';
import { z } from 'zod';
import path from 'path';

// Load local .env
config();
// Load root .env (fallback)
config({ path: path.resolve(process.cwd(), '../.env') });

const envSchema = z.object({
  SUPABASE_URL: z.string().url(),
  SUPABASE_SERVICE_ROLE_KEY: z.string().min(1),
  SCAN_INTERVAL_MS: z.coerce.number().int().positive().default(15_000),
  MAX_PROPOSALS_PER_SCAN: z.coerce.number().int().positive().default(20),
  SCAR_INDEX_WINDOW_HOURS: z.coerce.number().int().positive().default(168),
  LOG_LEVEL: z.string().optional()
});

export type Env = z.infer<typeof envSchema>;

export const env = envSchema.parse(process.env);
