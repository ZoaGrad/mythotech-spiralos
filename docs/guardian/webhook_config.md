
# Discord Webhook Setup

1. In Discord → channel settings → **Integrations** → **Webhooks** → **New Webhook**.
2. Name it `Guardian` and select the target channel (e.g., `#spiralbot` or `#guardian-feed`).
3. Copy the webhook URL and store it as:
   - GitHub secret `DISCORD_GUARDIAN_WEBHOOK`
   - local `.env` as `DISCORD_GUARDIAN_WEBHOOK=...` (if you run scripts locally)
