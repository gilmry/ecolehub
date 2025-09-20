#!/usr/bin/env bash
set -euo pipefail

# Verify that key dependency pins are aligned across backend requirement files
# Checks: fastapi, python-jose, python-multipart, pydantic (incl. extras)

ROOT_DIR=$(cd "$(dirname "$0")/.." && pwd)
cd "$ROOT_DIR"

BASE="backend/requirements.txt"
STAGES=(
  "backend/requirements.stage1.txt"
  "backend/requirements.stage2.txt"
  "backend/requirements.stage3.txt"
  "backend/requirements.stage4.txt"
)

PKGS=("fastapi" "python-jose" "python-multipart" "pydantic")

err() { echo "❌ $*" >&2; }

extract_spec() {
  local file="$1" pkg="$2"
  # Match with optional extras block, strip comments and whitespace
  local line
  line=$(grep -E "^${pkg}(\\[.*\\])?==|^${pkg}(\\[.*\\])?>=|^${pkg}(\\[.*\\])?<" "$file" | head -n1 || true)
  # Fallback: allow unpinned (not recommended)
  if [[ -z "$line" ]]; then
    line=$(grep -E "^${pkg}(\\[.*\\])?" "$file" | head -n1 || true)
  fi
  # Clean comments and spaces
  line=${line%%#*}
  line=${line// /}
  echo "$line"
}

missing=()
mismatch=()

for pkg in "${PKGS[@]}"; do
  base_spec=$(extract_spec "$BASE" "$pkg")
  if [[ -z "$base_spec" ]]; then
    missing+=("$pkg in $BASE")
    continue
  fi
  for stage in "${STAGES[@]}"; do
    if [[ ! -f "$stage" ]]; then
      missing+=("$stage (file missing)")
      continue
    fi
    stage_spec=$(extract_spec "$stage" "$pkg")
    if [[ -z "$stage_spec" ]]; then
      missing+=("$pkg in $stage")
      continue
    fi
    if [[ "$stage_spec" != "$base_spec" ]]; then
      mismatch+=("$pkg: $stage has '$stage_spec' but base has '$base_spec'")
    fi
  done
done

if (( ${#missing[@]} > 0 )); then
  err "Missing pins:"
  for m in "${missing[@]}"; do err "  - $m"; done
  exit 1
fi

if (( ${#mismatch[@]} > 0 )); then
  err "Version mismatches detected (align stage files with backend/requirements.txt):"
  for m in "${mismatch[@]}"; do err "  - $m"; done
  exit 1
fi

echo "✅ Requirements sync OK (fastapi, python-jose, python-multipart, pydantic)"

