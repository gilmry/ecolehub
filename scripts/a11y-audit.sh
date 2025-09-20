#!/usr/bin/env bash
set -euo pipefail

# Simple a11y audit runner.
# Requires the site to be running locally (e.g., make start or start-stage4/traefik).

BASE_URL=${BASE_URL:-http://localhost}
STRICT=${STRICT:-0}

echo "🔎 Running accessibility audit against: $BASE_URL"

if command -v pa11y >/dev/null 2>&1; then
  if [ "$STRICT" = "1" ]; then
    pa11y "$BASE_URL" --standard WCAG2AA
  else
    pa11y "$BASE_URL" --standard WCAG2AA || true
  fi
  exit 0
fi

if command -v npx >/dev/null 2>&1; then
  echo "ℹ️ Using npx pa11y (network required)"
  if [ "$STRICT" = "1" ]; then
    npx --yes pa11y "$BASE_URL" --standard WCAG2AA
  else
    npx --yes pa11y "$BASE_URL" --standard WCAG2AA || true
  fi
  exit 0
fi

if command -v docker >/dev/null 2>&1; then
  echo "🐳 Using pa11y Docker image (host network assumed)"
  if [ "$STRICT" = "1" ]; then
    docker run --rm --network host pa11y/pa11y pa11y "$BASE_URL" --standard WCAG2AA
  else
    docker run --rm --network host pa11y/pa11y pa11y "$BASE_URL" --standard WCAG2AA || true
  fi
  exit 0
fi

echo "❌ No pa11y/npx/docker available."
echo "Install pa11y: npm i -g pa11y  (requires Node.js)"
exit 2
