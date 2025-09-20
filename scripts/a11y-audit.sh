#!/usr/bin/env bash
set -euo pipefail

# Simple a11y audit runner.
# Requires the site to be running locally (e.g., make start or start-stage4/traefik).

BASE_URL=${BASE_URL:-http://localhost}
STRICT=${STRICT:-0}

echo "🔎 Running accessibility audit"

CONFIG_FILE=".pa11yci"
USE_CONFIG=0
if [ -f "$CONFIG_FILE" ]; then
  echo "📝 Using $CONFIG_FILE configuration"
  USE_CONFIG=1
fi

if command -v pa11y-ci >/dev/null 2>&1 && [ "$USE_CONFIG" = "1" ]; then
  if [ "$STRICT" = "1" ]; then
    pa11y-ci
  else
    pa11y-ci || true
  fi
  exit 0
fi

if command -v pa11y >/dev/null 2>&1 && [ "$USE_CONFIG" = "0" ]; then
  echo "🔎 Auditing BASE_URL: $BASE_URL"
  if [ "$STRICT" = "1" ]; then
    pa11y "$BASE_URL" --standard WCAG2AA
  else
    pa11y "$BASE_URL" --standard WCAG2AA || true
  fi
  exit 0
fi

if command -v npx >/dev/null 2>&1; then
  if [ "$USE_CONFIG" = "1" ]; then
    echo "ℹ️ Using npx pa11y-ci (network required)"
    if [ "$STRICT" = "1" ]; then
      npx --yes pa11y-ci
    else
      npx --yes pa11y-ci || true
    fi
    exit 0
  else
    echo "ℹ️ Using npx pa11y (network required)"
    echo "🔎 Auditing BASE_URL: $BASE_URL"
    if [ "$STRICT" = "1" ]; then
      npx --yes pa11y "$BASE_URL" --standard WCAG2AA
    else
      npx --yes pa11y "$BASE_URL" --standard WCAG2AA || true
    fi
    exit 0
  fi
fi

if command -v docker >/dev/null 2>&1; then
  if [ "$USE_CONFIG" = "1" ]; then
    echo "🐳 Using pa11y-ci Docker image (host network assumed)"
    # pa11y/ci image expects /ci/.pa11yci 
    if [ "$STRICT" = "1" ]; then
      docker run --rm --network host -v "$(pwd)/.pa11yci:/ci/.pa11yci:ro" pa11y/ci
    else
      docker run --rm --network host -v "$(pwd)/.pa11yci:/ci/.pa11yci:ro" pa11y/ci || true
    fi
  else
    echo "🐳 Using pa11y Docker image (host network assumed)"
    echo "🔎 Auditing BASE_URL: $BASE_URL"
    if [ "$STRICT" = "1" ]; then
      docker run --rm --network host pa11y/pa11y pa11y "$BASE_URL" --standard WCAG2AA
    else
      docker run --rm --network host pa11y/pa11y pa11y "$BASE_URL" --standard WCAG2AA || true
    fi
  fi
  exit 0
fi

echo "❌ No pa11y/npx/docker available."
echo "Install pa11y: npm i -g pa11y  (requires Node.js)"
exit 2
