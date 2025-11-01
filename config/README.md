# SpiralOS Configuration

Configuration files for SpiralOS integration and deployment.

---

## Files

### `supabase_connection.json`

**Purpose:** Connection manifest for the Supabase ↔ GitHub ↔ Reddit trinity loop

**Contents:**
- Supabase credential templates and descriptions
- GitHub Actions secret requirements
- Reddit integration configuration
- Database table documentation
- Environment setup instructions
- Security notes and best practices
- Trinity loop architecture overview

**Usage:**

This file serves as:
1. **Documentation** - Reference for all required secrets and their purposes
2. **Configuration template** - Shows structure for integration setup
3. **Deployment guide** - Lists all components of the trinity loop

**Key Sections:**

- **`supabase`** - Supabase credentials and their use cases
- **`github_actions`** - Required secrets for workflows
- **`reddit_integration`** - Reddit bot configuration
- **`database_tables`** - Schema documentation
- **`environment_setup`** - Local dev and CI/CD setup
- **`trinity_loop`** - Architecture and autonomous operations

**Security:**

All values in this file use `${VARIABLE_NAME}` placeholders.
**NEVER** replace these with actual credentials.

Actual credentials should be stored in:
- **Local dev:** `.env` file (not committed)
- **GitHub Actions:** Repository Secrets
- **Production:** Environment variables

---

## Related Documentation

- **Integration Guide:** `docs/SUPABASE_INTEGRATION.md`
- **CI Setup:** `CI_SETUP_GUIDE.md`
- **Scripts:** `scripts/README.md`

---

## Environment Variables Reference

### Required

| Variable | Description | Example |
|----------|-------------|---------|
| `SUPABASE_URL` | Supabase project URL | `https://xxxxx.supabase.co` |
| `SUPABASE_SERVICE_KEY` | Server-side API key | `eyJhbGc...` |

### Optional

| Variable | Description | Default |
|----------|-------------|---------|
| `SUPABASE_ANON_KEY` | Client-side API key | None |
| `SUPABASE_PROJECT_REF` | Project reference | None |
| `REDDIT_CLIENT_ID` | Reddit app ID | None |
| `REDDIT_CLIENT_SECRET` | Reddit app secret | None |
| `REDDIT_USERNAME` | Reddit bot username | None |
| `REDDIT_PASSWORD` | Reddit bot password | None |

---

## Quick Start

### 1. View Configuration

```bash
cat config/supabase_connection.json | jq
```

### 2. Set Up Environment

```bash
# Copy template
cp config/supabase_connection.json .env.template

# Edit with your values (create .env, don't commit)
# See docs/SUPABASE_INTEGRATION.md for details
```

### 3. Test Connection

```bash
export SUPABASE_URL="..."
export SUPABASE_SERVICE_KEY="..."

python3 scripts/test_supabase_connection.py
```

---

🜂 **Configuration Complete** 🜂

*Where coherence → currency → community*
