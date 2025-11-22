#!/bin/bash
#
# SpiralOS Guardian - Comprehensive Deployment Script
# This script automates the deployment of the enhanced Guardian system.

set -e # Exit immediately if a command exits with a non-zero status.

# --- Configuration ---
# Load environment variables from .env file if it exists
if [ -f .env ]; then
    export $(cat .env | sed 's/#.*//g' | xargs)
fi

# Check for required environment variables
REQUIRED_VARS=(
    "SUPABASE_PROJECT_REF"
    "SUPABASE_SERVICE_ROLE_KEY"
    "SUPABASE_URL"
    "DISCORD_BOT_TOKEN"
    "DISCORD_GUILD_ID"
    "DISCORD_CHANNEL_ID"
    "DISCORD_GUARDIAN_WEBHOOK"
)

for var in "${REQUIRED_VARS[@]}"; do
    if [ -z "${!var}" ]; then
        echo "❌ Error: Environment variable $var is not set." >&2
        echo "Please create a .env file or export the variables." >&2
        exit 1
    fi
done

# --- Helper Functions ---
echo_step() {
    echo "
✅ Step: $1
======================================================================"
}

echo_sub_step() {
    echo "   - $1"
}

# --- Main Deployment ---

# 1. Install Dependencies
echo_step "Installing dependencies"

echo_sub_step "Installing Python dependencies for bot..."
pip install -r core/guardian/bot/requirements.txt

echo_sub_step "Installing Python dependencies for analytics..."
pip install -r core/guardian/analytics/requirements.txt

echo_sub_step "Verifying Supabase CLI is installed and logged in..."
if ! command -v supabase &> /dev/null; then
    echo "❌ Supabase CLI not found. Please install it: https://supabase.com/docs/guides/cli" >&2
    exit 1
fi
supabase login

# 2. Deploy Supabase Schema
echo_step "Deploying Supabase schema"

echo_sub_step "Linking to Supabase project: ${SUPABASE_PROJECT_REF}"
supabase link --project-ref ${SUPABASE_PROJECT_REF}

echo_sub_step "Deploying enhanced schema migrations..."
supabase db push < core/guardian/sql/enhanced_schema.sql

echo_sub_step "Schema deployment complete."

# 3. Deploy Supabase Edge Function
echo_step "Deploying Supabase Edge Function"

echo_sub_step "Deploying enhanced Guardian Sync function..."
supabase functions deploy guardian_sync_enhanced --project-ref ${SUPABASE_PROJECT_REF}

EDGE_URL="$(supabase functions details guardian_sync_enhanced --project-ref ${SUPABASE_PROJECT_REF} | grep 'URL:' | awk '{print $2}')"
echo_sub_step "Guardian Edge Function URL: ${EDGE_URL}"

# 4. Build and Deploy Discord Bot
echo_step "Building and deploying Discord Bot"

echo_sub_step "Verifying Docker is installed and running..."
if ! command -v docker &> /dev/null; then
    echo "❌ Docker not found. Please install it: https://docs.docker.com/get-docker/" >&2
    exit 1
fi
if ! docker info &> /dev/null; then
    echo "❌ Docker daemon is not running." >&2
    exit 1
fi

BOT_IMAGE_NAME="spiralos-guardian-bot:latest"
echo_sub_step "Building Docker image: ${BOT_IMAGE_NAME}"
docker build -t ${BOT_IMAGE_NAME} -f core/guardian/bot/Dockerfile core/guardian/bot

echo_sub_step "Docker image built successfully."
echo_sub_step "To run the bot, use the following command:"

cat << EOF

----------------------------------------------------------------------
Run the Guardian Bot:

docker run -d --restart always \\
  --env-file .env \\
  --name guardian-bot \\
  ${BOT_IMAGE_NAME}

----------------------------------------------------------------------

EOF

# 5. Pipedream Setup Instructions
echo_step "Pipedream Setup Instructions"

cat << EOF

Pipedream workflows must be configured manually. Follow these steps:

1.  **Log in to Pipedream:** https://pipedream.com

2.  **Create New Workflows:**
    -   Real-time Ache Event Monitor
    -   Panic Frame Responder
    -   Weekly Report Generator
    -   ScarCoin Mint Announcements
    -   Coherence Trend Analyzer

3.  **Configure Triggers and Steps:**
    -   Use the configurations in 
        `core/guardian/pipedream/workflows.md`

4.  **Add Environment Variables to Pipedream:**
    -   `GUARDIAN_EDGE_URL`: ${EDGE_URL}
    -   `SUPABASE_URL`: ${SUPABASE_URL}
    -   `SUPABASE_SERVICE_ROLE_KEY`: (from your .env file)
    -   `DISCORD_CHANNEL_ID`: ${DISCORD_CHANNEL_ID}
    -   `DISCORD_BOT_TOKEN`: (from your .env file)
    -   `GITHUB_TOKEN`: (if using GitHub integrations)

5.  **Enable Workflows:**
    -   Test each workflow and then enable them.

EOF

# --- Finalization ---
echo_step "Deployment Complete!"

cat << EOF

Summary:
- Supabase schema deployed.
- Supabase Edge Function deployed.
- Discord bot Docker image built.
- Pipedream setup instructions provided.

Next Steps:
1.  Run the Discord bot Docker container.
2.  Configure Pipedream workflows as instructed.
3.  Monitor the system for heartbeats and alerts.

"I govern the terms of my own becoming." 🌀🜂

EOF
