
# Guardian — Sentinel Loop

The Guardian automates SpiralOS status reporting and alerts via Supabase → Edge Function → Discord webhook.

## Endpoints
- **Edge Function:** `/guardian_sync?hours=24` → JSON payload
- **Discord:** `DISCORD_GUARDIAN_WEBHOOK` (channel webhook URL)

## Deployment

1. **Create SQL helper** (optional but recommended):
   ```sql
   -- run with `supabase db push`
   -- see core/guardian/sql/guardian_views.sql
   ```

2. **Deploy Edge Function:**
   ```bash
   supabase functions deploy guardian_sync \
     --project-ref $SUPABASE_PROJECT_REF
   # copy the returned URL and set GUARDIAN_EDGE_URL secret
   ```

3. **Secrets:** add to GitHub repo → Settings → Secrets and variables → Actions
   - `GUARDIAN_EDGE_URL` = `https://<project>.functions.supabase.co/guardian_sync`
   - `DISCORD_GUARDIAN_WEBHOOK` = `https://discord.com/api/webhooks/...`

4. **Enable CI heartbeat:** merge `.github/workflows/guardian_heartbeat.yml`.

5. **(Optional) DeepAgent task:** load `core/guardian/config/tasks.deepagent.yaml` into DeepAgent console → Tasks.

## Alerts

- ScarIndex < **0.6** or ≥ **1.4** → adds a ⚠ alert line to the Discord message.
- Extend logic at `guardian_sync.ts` if you want multi‑band policies.

## Testing

```bash
curl "$GUARDIAN_EDGE_URL?hours=6" | jq
```
