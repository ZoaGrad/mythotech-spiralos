# Secret Management Strategy

## Overview
SpiralOS employs a strict "Zero Trust" approach to secret management. Secrets are never hardcoded in source code or committed to version control.

## Production Secrets
For production environments (Supabase, Cloud), secrets are managed via:
1.  **Supabase Vault**: For storing sensitive API keys and credentials within the database, accessible only via secure functions.
2.  **Environment Variables**: Injected at runtime for Edge Functions and Python services.
    - `SUPABASE_URL`
    - `SUPABASE_SERVICE_ROLE_KEY`
    - `GITHUB_WEBHOOK_SECRET`
    - `GATEWAY_API_KEY`

## CI/CD Secrets
GitHub Actions secrets are used for CI/CD pipelines.
- **Repository Secrets**: Managed via GitHub Settings > Secrets and Variables > Actions.
- **Local Development**: Use `.env` files (gitignored) for local testing.

## Hardening Guidelines
1.  **Rotation**: Rotate `SUPABASE_SERVICE_ROLE_KEY` and other critical keys every 90 days.
2.  **Least Privilege**: Use scoped API keys where possible instead of the service role key.
3.  **Audit**: Regularly audit `guardian_logs` for unauthorized access attempts.

## Scripts
- `add_github_secret.sh`: Helper script to add secrets to GitHub. Ensure this is run in a secure environment and history is cleared.
