# SpiralOS v2 Kernel Workers

This package contains TypeScript workers for the SpiralOS v2 kernel:

- **SSD Guard** – classifies proposals using deterministic heuristics and records results.
- **ScarIndex Oracle** – computes a rolling ScarIndex over recent events.

## Folder structure

```
spiralos-kernel/
  migrations/        # Supabase-compatible SQL migrations
  src/
    services/
      scar-index/    # ScarIndex Oracle worker
      ssd-guard/     # SSD Guard worker
    shared/          # Cross-service helpers (logging, env parsing, Supabase client)
  package.json
  tsconfig.json
```

## Running locally

1. Install dependencies:

```bash
npm install
```

2. Provide environment variables in `.env`:

- `SUPABASE_URL`
- `SUPABASE_SERVICE_ROLE_KEY`
- `SCAN_INTERVAL_MS` (optional, defaults to 15000)
- `MAX_PROPOSALS_PER_SCAN` (optional, defaults to 20)
- `SCAR_INDEX_WINDOW_HOURS` (optional, defaults to 168)

3. Start a worker:

```bash
npm run start:ssd
npm run start:scar-index
```

Both workers log structured output to stdout and will retry transient Supabase failures with backoff.
