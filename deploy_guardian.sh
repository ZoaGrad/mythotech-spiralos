#!/bin/bash

# Deploy Guardian Automation Kit to Supabase
# This script deploys the Guardian SQL function and Edge Function to Supabase

set -e

echo "🛡️ Guardian Automation Kit - Deployment Script"
echo "=============================================="

# Check if Supabase CLI is installed
if ! command -v supabase &> /dev/null; then
    echo "❌ Supabase CLI not found. Installing..."
    curl -fsSL https://github.com/supabase/cli/releases/latest/download/supabase_linux_amd64.tar.gz -o /tmp/supabase.tar.gz
    tar -xzf /tmp/supabase.tar.gz -C /tmp
    sudo mv /tmp/supabase /usr/local/bin/
    echo "✅ Supabase CLI installed"
fi

# Check for required environment variables
if [ -z "$SUPABASE_PROJECT_REF" ]; then
    echo "❌ SUPABASE_PROJECT_REF not set"
    echo "Please set it: export SUPABASE_PROJECT_REF=your_project_ref"
    exit 1
fi

if [ -z "$SUPABASE_SERVICE_ROLE_KEY" ]; then
    echo "❌ SUPABASE_SERVICE_ROLE_KEY not set"
    echo "Please set it: export SUPABASE_SERVICE_ROLE_KEY=your_service_role_key"
    exit 1
fi

echo "✅ Environment variables verified"

# Link to Supabase project
echo "🔗 Linking to Supabase project..."
supabase link --project-ref "$SUPABASE_PROJECT_REF"

# Deploy SQL migration
echo "📊 Deploying SQL migration..."
supabase db push

# Deploy Edge Function
echo "⚡ Deploying Guardian Edge Function..."
supabase functions deploy guardian_sync --no-verify-jwt

# Get the Edge Function URL
EDGE_URL="https://${SUPABASE_PROJECT_REF}.supabase.co/functions/v1/guardian_sync"
echo ""
echo "✅ Deployment Complete!"
echo "========================"
echo "Edge Function URL: $EDGE_URL"
echo ""
echo "Next steps:"
echo "1. Test the function: curl '$EDGE_URL?hours=24'"
echo "2. Add GUARDIAN_EDGE_URL secret to GitHub repository"
echo "3. Set up scheduled workflow to call the function"

# Optionally test the function
read -p "Would you like to test the function now? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "🧪 Testing Guardian Edge Function..."
    curl -s "$EDGE_URL?hours=24" | jq '.'
fi

# Save the Edge URL to .env for reference
if [ ! -f .env ]; then
    cp .env.example .env
fi

# Update or add GUARDIAN_EDGE_URL in .env
if grep -q "GUARDIAN_EDGE_URL=" .env; then
    sed -i "s|GUARDIAN_EDGE_URL=.*|GUARDIAN_EDGE_URL=$EDGE_URL|" .env
else
    echo "GUARDIAN_EDGE_URL=$EDGE_URL" >> .env
fi

echo "💾 Edge URL saved to .env file"
