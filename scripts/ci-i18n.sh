#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR=$(cd "$(dirname "$0")/.." && pwd)
cd "$ROOT_DIR"

echo "🌐 i18n-lint (STRICT)"
STRICT=1 ./scripts/i18n-lint.sh

