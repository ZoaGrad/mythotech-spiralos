#!/bin/bash

# Add GUARDIAN_EDGE_URL to GitHub repository secrets
# Requires: gh CLI or GITHUB_TOKEN environment variable

set -e

REPO="ZoaGrad/mythotech-spiralos"

if [ -z "$1" ]; then
    read -p "Enter EDGE_FUNCTION_URL: " EDGE_URL
else
    EDGE_URL="$1"
fi

if [ -z "$EDGE_URL" ]; then
    echo "Error: EDGE_FUNCTION_URL cannot be empty."
    exit 1
fi

EDGE_URL="$1"

echo "🔐 Adding GUARDIAN_EDGE_URL to GitHub secrets..."

# Method 1: Using gh CLI (preferred)
if command -v gh &> /dev/null; then
    echo "Using gh CLI..."
    echo "$EDGE_URL" | gh secret set GUARDIAN_EDGE_URL --repo "$REPO"
    echo "✅ Secret added successfully via gh CLI"
    exit 0
fi

# Method 2: Using GitHub API with curl
if [ -n "$GITHUB_TOKEN" ]; then
    echo "Using GitHub API..."
    
    # Get public key for encryption
    PUBLIC_KEY_RESPONSE=$(curl -s -H "Authorization: token $GITHUB_TOKEN" \
        "https://api.github.com/repos/$REPO/actions/secrets/public-key")
    
    PUBLIC_KEY=$(echo "$PUBLIC_KEY_RESPONSE" | jq -r '.key')
    KEY_ID=$(echo "$PUBLIC_KEY_RESPONSE" | jq -r '.key_id')
    
    # Encrypt the secret using libsodium
    # Note: This requires libsodium-wrappers or similar for proper encryption
    # For simplicity, we'll show the command but note it needs proper encryption
    
    echo "⚠️  Manual encryption required"
    echo "Public Key: $PUBLIC_KEY"
    echo "Key ID: $KEY_ID"
    echo "Secret Value: $EDGE_URL"
    echo ""
    echo "To add the secret manually:"
    echo "1. Go to https://github.com/$REPO/settings/secrets/actions"
    echo "2. Click 'New repository secret'"
    echo "3. Name: GUARDIAN_EDGE_URL"
    echo "4. Value: $EDGE_URL"
    
    exit 0
fi

# Method 3: Manual instructions
echo "❌ Neither gh CLI nor GITHUB_TOKEN found"
echo ""
echo "Please add the secret manually:"
echo "1. Install gh CLI: curl -sS https://webi.sh/gh | sh"
echo "   Or set GITHUB_TOKEN environment variable"
echo "2. Run: echo '$EDGE_URL' | gh secret set GUARDIAN_EDGE_URL --repo $REPO"
echo ""
echo "Or via GitHub UI:"
echo "1. Go to https://github.com/$REPO/settings/secrets/actions"
echo "2. Click 'New repository secret'"
echo "3. Name: GUARDIAN_EDGE_URL"
echo "4. Value: $EDGE_URL"

exit 1
