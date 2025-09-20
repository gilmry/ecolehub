#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR=$(cd "$(dirname "$0")/.." && pwd)
cd "$ROOT_DIR"

export STAGE=${STAGE:-4}
export TESTING=${TESTING:-1}
export DATABASE_URL=${DATABASE_URL:-sqlite:///test.db}
export REDIS_URL=${REDIS_URL:-redis://localhost:6379/15}
export SECRET_KEY=${SECRET_KEY:-test-secret-key-for-ci-only}

PYBIN_ABS="python3"
if [ -x backend/venv/bin/python ]; then
  # Verify venv python works; otherwise fallback
  if backend/venv/bin/python -V >/dev/null 2>&1; then
    PYBIN_ABS="$ROOT_DIR/backend/venv/bin/python"
  fi
fi

echo "🔍 flake8 (strict then relaxed)"
if $PYBIN_ABS - <<<'import flake8' >/dev/null 2>&1; then
  (cd backend && $PYBIN_ABS -m flake8 app/ --count --select=E9,F63,F7,F82 --show-source --statistics) || echo "Linting issues found"
  (cd backend && $PYBIN_ABS -m flake8 app/ --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics) || echo "Style issues found"
else
  echo "ℹ️ flake8 not available; skipping"
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
