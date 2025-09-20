#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR=$(cd "$(dirname "$0")/.." && pwd)
cd "$ROOT_DIR"

export STAGE=${STAGE:-4}
export TESTING=${TESTING:-1}
export DATABASE_URL=${DATABASE_URL:-sqlite:///test.db}
export REDIS_URL=${REDIS_URL:-redis://localhost:6379/15}
export SECRET_KEY=${SECRET_KEY:-test-secret-key-for-ci-only}

# CI path shim: some external tests expect repo to be at /home/runner/work/<repo>
# but Actions checks out at /home/runner/work/<repo>/<repo>. Expose symlinks for Makefile and backend.
PARENT_DIR=$(dirname "$ROOT_DIR")
if [ -d "$PARENT_DIR" ] && [ "$PARENT_DIR" != "$ROOT_DIR" ]; then
  # Symlink Makefile
  if [ ! -e "$PARENT_DIR/Makefile" ]; then
    ln -s "$ROOT_DIR/Makefile" "$PARENT_DIR/Makefile" || true
  fi
  # Symlink backend directory
  if [ ! -e "$PARENT_DIR/backend" ]; then
    ln -s "$ROOT_DIR/backend" "$PARENT_DIR/backend" || true
  fi
fi

PYBIN_ABS="python3"
if [ -x backend/venv/bin/python ]; then
  # Verify venv python works; otherwise fallback
  if backend/venv/bin/python -V >/dev/null 2>&1; then
    PYBIN_ABS="$ROOT_DIR/backend/venv/bin/python"
  fi
fi

echo "🎨 Auto-formatting Python code"
# Use centralized formatting script as source of truth
FORMAT_SCRIPT="$ROOT_DIR/scripts/format-python.sh"
if [ -x "$FORMAT_SCRIPT" ]; then
  "$FORMAT_SCRIPT"
else
  echo "⚠️ format-python.sh not found at $FORMAT_SCRIPT, using fallback formatting"
  # Fallback if script not available
  if $PYBIN_ABS - <<<'import black' >/dev/null 2>&1; then
    echo "  ⚫ black: basic formatting"
    (cd backend && $PYBIN_ABS -m black app tests --line-length 88 --safe) || true
  fi
fi

echo "🔍 flake8 (strict then relaxed)"
if $PYBIN_ABS - <<<'import flake8' >/dev/null 2>&1; then
  (cd backend && $PYBIN_ABS -m flake8 app/ --count --select=E9,F63,F7,F82 --show-source --statistics) || echo "Linting issues found"
  (cd backend && $PYBIN_ABS -m flake8 app/ --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics) || echo "Style issues found"
else
  echo "ℹ️ flake8 not available; skipping"
fi

# Ensure runtime and test dependencies (CI environment)
echo "📦 Installing backend dependencies (runtime + test)"
if [ -f backend/requirements.txt ]; then
  (cd backend && $PYBIN_ABS -m pip install -q -r requirements.txt) || true
fi
if [ -f backend/requirements.test.txt ]; then
  (cd backend && $PYBIN_ABS -m pip install -q -r requirements.test.txt) || true
fi

echo "🔎 Checking requirements alignment"
if [ -x scripts/check-requirements-sync.sh ]; then
  ./scripts/check-requirements-sync.sh
else
  echo "ℹ️ requirements sync script missing; skipping"
fi

if $PYBIN_ABS - <<<'import pytest' >/dev/null 2>&1; then
  echo "🧪 Pytest: unit"
  (cd backend && $PYBIN_ABS -m pytest tests/unit/ -v --tb=short -m unit)
  echo "🧪 Pytest: integration"
  (cd backend && $PYBIN_ABS -m pytest tests/integration/ -v --tb=short -m integration)
  echo "🧪 Pytest: auth"
  (cd backend && $PYBIN_ABS -m pytest tests/ -v --tb=short -m auth)
  echo "🧪 Pytest: sel"
  (cd backend && $PYBIN_ABS -m pytest tests/ -v --tb=short -m sel)
  echo "📊 Coverage"
  (cd backend && $PYBIN_ABS -m pytest tests/ --cov=app --cov-report=xml:coverage.xml --cov-report=term)
else
  echo "⚠️ pytest not available; please run 'scripts/run-tests-local.sh' locally with internet or ensure venv dependencies installed."
  exit 2
fi

echo "✅ Backend CI script completed"
