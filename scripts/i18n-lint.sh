#!/usr/bin/env bash
set -eo pipefail

# Simple i18n linter for frontend templates
# Finds visible hardcoded text that isn't using $t() or mustache bindings

FILE="frontend/index.html"

if ! command -v rg >/dev/null 2>&1; then
  echo "ripgrep (rg) is required for i18n-lint." >&2
  exit 2
fi

# Find text nodes with letters between > and <, exclude those containing $t( or {{
# Find matches with visible letters, then exclude known acceptable cases
MATCHES=$(rg -n "\>[^<\{\}]*[A-Za-zÀ-ÿ][^<\{\}]*\<" --pcre2 "$FILE" \
  | grep -vF -e '$t(' -e '{{' \
  | rg -v '<title' \
  | rg -v '×</button>' || true)

COUNT=$(printf "%s\n" "$MATCHES" | sed '/^$/d' | wc -l | tr -d ' ')

echo "i18n-lint: $COUNT potential hardcoded strings found in $FILE"
if [ "$COUNT" -gt 0 ]; then
  echo "--- Findings ---"
  printf "%s\n" "$MATCHES" | sed -n '1,200p'
fi

# Strict mode: fail CI if issues remain
if [ "${STRICT:-0}" != "0" ] && [ "$COUNT" -gt 0 ]; then
  echo "i18n-lint: FAIL (STRICT mode)." >&2
  exit 1
fi

echo "i18n-lint: OK"
