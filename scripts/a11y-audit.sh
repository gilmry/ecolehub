#!/usr/bin/env bash
set -euo pipefail

# Simple a11y audit runner.
# Requires the site to be running locally (e.g., make start or start-stage4/traefik).

BASE_URL=${BASE_URL:-http://localhost}
STRICT=${STRICT:-0}

# Reports directory
REPORT_DIR="reports/a11y"
mkdir -p "$REPORT_DIR"

run_pa11y_ci() {
  local out_json="$REPORT_DIR/pa11y-ci.json"
  echo "🧾 Writing Pa11y CI JSON report to: $out_json"
  if [ "$STRICT" = "1" ]; then
    # Note: Chrome launch args for pa11y-ci must be set via .pa11yci chromeLaunchConfig
    pa11y-ci --reporter json | tee "$out_json"
  else
    pa11y-ci --reporter json | tee "$out_json" || true
  fi
}

run_pa11y() {
  local out_json="$REPORT_DIR/pa11y.json"
  echo "🧾 Writing Pa11y JSON report to: $out_json"
  if [ "$STRICT" = "1" ]; then
    pa11y "$BASE_URL" --standard WCAG2AA --reporter json \
      --chrome-arg="--no-sandbox" \
      --chrome-arg="--disable-setuid-sandbox" \
      --chrome-arg="--disable-dev-shm-usage" \
      | tee "$out_json"
  else
    pa11y "$BASE_URL" --standard WCAG2AA --reporter json \
      --chrome-arg="--no-sandbox" \
      --chrome-arg="--disable-setuid-sandbox" \
      --chrome-arg="--disable-dev-shm-usage" \
      | tee "$out_json" || true
  fi
}

echo "🔎 Running accessibility audit"

CONFIG_FILE=".pa11yci"
USE_CONFIG=0
if [ -f "$CONFIG_FILE" ]; then
  echo "📝 Using $CONFIG_FILE configuration"
  USE_CONFIG=1
fi

if command -v pa11y-ci >/dev/null 2>&1 && [ "$USE_CONFIG" = "1" ]; then
  run_pa11y_ci
  exit 0
fi

if command -v pa11y >/dev/null 2>&1 && [ "$USE_CONFIG" = "0" ]; then
  echo "🔎 Auditing BASE_URL: $BASE_URL"
  run_pa11y
  exit 0
fi

if command -v npx >/dev/null 2>&1; then
  if [ "$USE_CONFIG" = "1" ]; then
    echo "ℹ️ Using npx pa11y-ci (network required)"
    if [ "$STRICT" = "1" ]; then
      # Note: Chrome launch args are provided via .pa11yci chromeLaunchConfig
      npx --yes pa11y-ci --reporter json | tee "$REPORT_DIR/pa11y-ci.json"
    else
      npx --yes pa11y-ci --reporter json | tee "$REPORT_DIR/pa11y-ci.json" || true
    fi
    exit 0
  else
    echo "ℹ️ Using npx pa11y (network required)"
    echo "🔎 Auditing BASE_URL: $BASE_URL"
    if [ "$STRICT" = "1" ]; then
      npx --yes pa11y "$BASE_URL" --standard WCAG2AA --reporter json \
        --chrome-arg="--no-sandbox" \
        --chrome-arg="--disable-setuid-sandbox" \
        --chrome-arg="--disable-dev-shm-usage" \
        | tee "$REPORT_DIR/pa11y.json"
    else
      npx --yes pa11y "$BASE_URL" --standard WCAG2AA --reporter json \
        --chrome-arg="--no-sandbox" \
        --chrome-arg="--disable-setuid-sandbox" \
        --chrome-arg="--disable-dev-shm-usage" \
        | tee "$REPORT_DIR/pa11y.json" || true
    fi
    exit 0
  fi
fi

if command -v docker >/dev/null 2>&1; then
  if [ "$USE_CONFIG" = "1" ]; then
    echo "🐳 Using pa11y-ci Docker image (host network assumed)"
    # pa11y/ci image expects /ci/.pa11yci 
    # Docker image does not support direct JSON file output mapping; capture stdout to file
    if [ "$STRICT" = "1" ]; then
      docker run --rm --network host -v "$(pwd)/.pa11yci:/ci/.pa11yci:ro" pa11y/ci --reporter json | tee "$REPORT_DIR/pa11y-ci.json"
    else
      docker run --rm --network host -v "$(pwd)/.pa11yci:/ci/.pa11yci:ro" pa11y/ci --reporter json | tee "$REPORT_DIR/pa11y-ci.json" || true
    fi
  else
    echo "🐳 Using pa11y Docker image (host network assumed)"
    echo "🔎 Auditing BASE_URL: $BASE_URL"
    if [ "$STRICT" = "1" ]; then
      docker run --rm --network host pa11y/pa11y pa11y "$BASE_URL" --standard WCAG2AA --reporter json | tee "$REPORT_DIR/pa11y.json"
    else
      docker run --rm --network host pa11y/pa11y pa11y "$BASE_URL" --standard WCAG2AA --reporter json | tee "$REPORT_DIR/pa11y.json" || true
    fi
  fi
  exit 0
fi

echo "❌ No pa11y/npx/docker available."
echo "Install pa11y: npm i -g pa11y  (requires Node.js)"
exit 2

# Summarize reports if jq is available
summarize_json() {
  local file="$1"
  if ! command -v jq >/dev/null 2>&1; then
    echo "ℹ️ Install jq to see a summarized a11y report (sudo apt-get install -y jq)"
    return 0
  fi
  if [ ! -f "$file" ]; then
    return 0
  fi
  echo "\n📊 Accessibility Summary for $file"
  # Count issues heuristically: objects that look like pa11y issues (have code, selector, type)
  local total
  total=$(jq '[.. | objects | select(has("code") and has("selector") and has("type"))] | length' "$file" 2>/dev/null || echo 0)
  # Count distinct URLs if present
  local urls
  urls=$(jq '[.. | objects | .url?] | unique | length' "$file" 2>/dev/null || echo 0)
  echo "Total issues: ${total} across ${urls} URL(s)"
  # Top codes
  echo "Top issue codes:"
  jq -r '[.. | objects | select(has("code") and has("message")) | .code]
         | group_by(.)
         | map({code: .[0], count: length})
         | sort_by(-.count)
         | .[:5]
         | ("  " + (map("\(.code): \(.count)") | join("\n  ")))
        ' "$file" 2>/dev/null || true
}

# Attempt to summarize any generated reports
summarize_json "$REPORT_DIR/pa11y-ci.json"
summarize_json "$REPORT_DIR/pa11y.json"
