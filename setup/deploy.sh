#!/bin/bash
set -e

REPO_NAME="${1:-SiriBot}"
GITHUB_TOKEN="${GITHUB_TOKEN:-}"
GITHUB_USER="${GITHUB_USER:-$(git config --get user.username 2>/dev/null || git config --get user.name 2>/dev/null || echo "")}"

if [ -z "$GITHUB_TOKEN" ]; then
    echo "Error: GITHUB_TOKEN not set"
    echo "Usage: GITHUB_TOKEN=xxx ./setup/deploy.sh [repo-name]"
    exit 1
fi

if [ -z "$GITHUB_USER" ]; then
    echo "Error: GitHub username not configured"
    echo "Run: git config --global user.name 'Your Name'"
    exit 1
fi

echo "🚀 Deploying SiriBot to GitHub..."

REPO_RESPONSE=$(curl -s -X POST \
    -H "Authorization: Bearer $GITHUB_TOKEN" \
    -H "Content-Type: application/json" \
    -H "Accept: application/vnd.github+json" \
    https://api.github.com/user/repos \
    -d "{\"name\":\"$REPO_NAME\",\"description\":\"SiriBot - Open-source AI assistant for macOS\",\"private\":false,\"auto_init\":false,\"gitignore_template\":\"macOS\"}")

if echo "$REPO_RESPONSE" | grep -q '"html_url"'; then
    REPO_URL=$(echo "$REPO_RESPONSE" | python3 -c "import sys,json; print(json.load(sys.stdin)['html_url'])")
    echo "Repository created: $REPO_URL"
else
    if echo "$REPO_RESPONSE" | grep -q '"message".*already exists'; then
        echo "Repository already exists, using existing repo"
        REPO_URL="https://github.com/$GITHUB_USER/$REPO_NAME"
    else
        echo "Error creating repository: $REPO_RESPONSE"
        exit 1
    fi
fi

if [ ! -d .git ]; then
    git init
    git add .
    git commit -m "Initial SiriBot commit"
fi

git remote remove origin 2>/dev/null || true
git remote add origin "https://github.com/$GITHUB_USER/$REPO_NAME.git"
git branch -M main
git push -u origin main --force

echo ""
echo "✅ Deployment complete!"
echo "Repository: $REPO_URL"
