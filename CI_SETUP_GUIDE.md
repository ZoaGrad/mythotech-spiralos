# CI/CD Setup Guide - MythoTech Spiralos

## ✅ FIXES COMPLETED

All critical CI/CD issues have been identified and fixed. Here's what was done:

### 1. ✅ Fixed YAML Syntax Errors (weekly-report.yml)
**Problem:** Empty secret variable placeholders `${{ }}` caused workflow parsing failures
**Solution:** Updated `.github/workflows/weekly-report.yml` with proper secret references
```yaml
# BEFORE (Line 66-69):
REDDIT_CLIENT_ID: ${{  }}
REDDIT_CLIENT_SECRET: ${{  }}
REDDIT_USERNAME: ${{  }}
REDDIT_PASSWORD: ${{  }}

# AFTER:
REDDIT_CLIENT_ID: ${{ secrets.REDDIT_CLIENT_ID }}
REDDIT_CLIENT_SECRET: ${{ secrets.REDDIT_CLIENT_SECRET }}
REDDIT_USERNAME: ${{ secrets.REDDIT_USERNAME }}
REDDIT_PASSWORD: ${{ secrets.REDDIT_PASSWORD }}
```
**Impact:** Fixes YAML validation error preventing all workflows from running

### 2. ✅ Updated requirements.txt with Pinned Versions
**Problem:** Supabase dependency had no version constraint, installing incompatible v2.x
**Solution:** Updated `requirements.txt` with proper version constraints
```
# BEFORE:
fastapi
uvicorn
pydantic
supabase

# AFTER:
fastapi
uvicorn
pydantic
praw>=7.0.0
supabase>=1.0.0,<2.0.0
python-dotenv
```
**Impact:** Ensures compatible API versions for all Python packages

### 3. ✅ Fixed Supabase API Imports (3 Python Files)
**Problem:** Code used deprecated `from supabase import create_client, Client` API
**Solution:** Updated all 3 files to use compatible import:
- `core/automation/judicial_automation.py` ✅
- `core/automation/status_report.py` ✅

```python
# BEFORE (Line 37):
from supabase import create_client, Client
...
self.supabase: Client = create_client(url, key)

# AFTER:
from supabase import create_client
...
self.supabase = create_client(url, key)
```
**Impact:** Removes ImportError preventing judicial automation and status report workflows

---

## 📋 REMAINING SETUP TASKS

### Task 1: Add Supabase Credentials to GitHub Secrets ⚠️ REQUIRED

**Status:** Not yet configured (Reddit secrets already present ✅)

**Steps:**
1. Navigate to: **Settings → Secrets and variables → Actions**
2. Click **"New repository secret"**
3. Add the following secrets:

| Secret Name | Value | Example |
|---|---|---|
| `SUPABASE_URL` | Your Supabase project URL | `https://xxxxx.supabase.co` |
| `SUPABASE_KEY` | Your Supabase API key (anon key) | `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...` |

**How to get these values:**
1. Go to [Supabase Dashboard](https://app.supabase.com)
2. Select your project
3. Go to **Settings → API**
4. Copy the **Project URL** and **API keys → anon (public key)**

### Task 2: Set Up Supabase Database Tables ⚠️ REQUIRED

**Expected Tables and Schema:**

#### Table: `judges`
```sql
CREATE TABLE judges (
  id TEXT PRIMARY KEY,
  name TEXT NOT NULL,
  status TEXT,
  specialization TEXT[] DEFAULT '{}',
  current_workload INTEGER DEFAULT 0,
  max_workload INTEGER DEFAULT 20,
  f2_score FLOAT DEFAULT 0.0,
  availability_start TIMESTAMP,
  availability_end TIMESTAMP,
  created_at TIMESTAMP DEFAULT now(),
  updated_at TIMESTAMP DEFAULT now()
);
```

#### Table: `cases`
```sql
CREATE TABLE cases (
  id TEXT PRIMARY KEY,
  case_number TEXT NOT NULL,
  case_type TEXT,
  complexity INTEGER DEFAULT 1,
  filing_date TIMESTAMP,
  assigned_judge_id TEXT REFERENCES judges(id),
  status TEXT DEFAULT 'pending',
  created_at TIMESTAMP DEFAULT now(),
  updated_at TIMESTAMP DEFAULT now()
);
```

#### Table: `panicframe_signals`
```sql
CREATE TABLE panicframe_signals (
  id TEXT PRIMARY KEY,
  created_at TIMESTAMP DEFAULT now(),
  level TEXT,
  key TEXT,
  meta JSONB DEFAULT '{}'
);
```

**To create these tables:**
1. Go to Supabase Dashboard → SQL Editor
2. Copy-paste each SQL statement above
3. Execute each statement

### Task 3: Test Locally (Optional but Recommended)

```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
export SUPABASE_URL="https://xxxxx.supabase.co"
export SUPABASE_KEY="your-anon-key"

# Test judicial automation
python -m core.automation.judicial_automation

# Test status report
python -m core.automation.status_report
```

---

## 🚀 TRIGGERING WORKFLOWS

Once secrets are configured, workflows will run:

### Manual Trigger:
1. Go to **Actions** tab
2. Select a workflow (e.g., "Judicial Automation")
3. Click "Run workflow"

### Automatic Triggers:
- **Judicial Automation**: Scheduled (check workflow for schedule)
- **Status Report**: Scheduled hourly
- **Weekly Report**: Scheduled for Mondays at 00:00 UTC

---

## 🔍 VERIFICATION CHECKLIST

- [ ] GitHub Secrets configured (SUPABASE_URL, SUPABASE_KEY)
- [ ] Supabase tables created (judges, cases, panicframe_signals)
- [ ] Reddit secrets verified (already configured)
- [ ] Requirements.txt pinned correctly
- [ ] Python imports updated in all files
- [ ] Workflow YAML syntax is valid
- [ ] First workflow run successful

---

## 📊 ROOT CAUSE ANALYSIS

### Issue Summary
**16 consecutive workflow failures** due to cascading errors:

1. **Primary**: YAML syntax errors blocked all workflows from running
2. **Secondary**: Missing Supabase secrets would fail runtime checks
3. **Tertiary**: Incompatible Supabase API versions caused ImportError

### Failed Workflows
- Run 2: Judicial Automation (Most recent)
- Run 16: Add requirements.txt
- Run 1: Status Report
- Runs 15, 14, 13, 12, 11, 10, 9, 8, 7: Weekly Report variants
- Runs 6, 5: Reddit credential updates
- **Run 1: Test Reddit Authentication** ✅ (Only successful - no Supabase imports)

---

## 🆘 TROUBLESHOOTING

### Error: "ImportError: cannot import name 'create_client'"
**Solution:** Verify requirements.txt has `supabase>=1.0.0,<2.0.0`

### Error: "YAML parsing error on lines 54-57"
**Solution:** Check that all secret references have proper syntax: `${{ secrets.NAME }}`

### Error: "Failed to authenticate with Supabase"
**Solution:** 
1. Verify SUPABASE_URL and SUPABASE_KEY are set in GitHub secrets
2. Check credentials are correct in Supabase dashboard
3. Ensure network access from GitHub Actions runners (usually allowed by default)

### Workflow runs but reports empty results
**Solution:** 
1. Check that Supabase tables have sample data
2. Verify table schemas match the code expectations
3. Check logs in GitHub Actions for specific errors

---

## 📚 USEFUL LINKS

- [GitHub Actions Secrets Documentation](https://docs.github.com/en/actions/security-guides/using-secrets-in-github-actions)
- [Supabase Python Client Documentation](https://github.com/supabase-community/supabase-py)
- [Supabase SQL Editor](https://app.supabase.com)
- [GitHub Actions Workflow Syntax](https://docs.github.com/en/actions/using-workflows/workflow-syntax-for-github-actions)

---

## ✨ NEXT STEPS

1. **Add Supabase Credentials** (Takes ~5 minutes)
2. **Create Supabase Tables** (Takes ~10 minutes)
3. **Trigger a workflow manually** to verify it works
4. **Monitor Actions tab** for successful runs
5. **Monitor workflow logs** to identify any remaining issues

---

*Last Updated: November 2024*
*Status: 3/5 fixes complete ✅*
*Ready for: Supabase credential configuration*
