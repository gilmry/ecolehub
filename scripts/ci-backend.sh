#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR=$(cd "$(dirname "$0")/.." && pwd)
cd "$ROOT_DIR"

export STAGE=${STAGE:-4}
export TESTING=${TESTING:-1}
export DATABASE_URL=${DATABASE_URL:-sqlite:///test.db}
export REDIS_URL=${REDIS_URL:-redis://localhost:6379/15}
export SECRET_KEY=${SECRET_KEY:-test-secret-key-for-ci-only}

PYBIN="python3"
if [ -x backend/venv/bin/python ]; then
  PYBIN="backend/venv/bin/python"
fi

echo "🔍 flake8 (strict then relaxed)"
$PYBIN -m pip install -q flake8 || true
(cd backend && $PYBIN -m flake8 app/ --count --select=E9,F63,F7,F82 --show-source --statistics) || echo "Linting issues found"
(cd backend && $PYBIN -m flake8 app/ --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics) || echo "Style issues found"

echo "🧪 Pytest: unit"
(cd backend && $PYBIN -m pytest tests/unit/ -v --tb=short -m unit)
echo "🧪 Pytest: integration"
(cd backend && $PYBIN -m pytest tests/integration/ -v --tb=short -m integration)
echo "🧪 Pytest: auth"
(cd backend && $PYBIN -m pytest tests/ -v --tb=short -m auth)
echo "🧪 Pytest: sel"
(cd backend && $PYBIN -m pytest tests/ -v --tb=short -m sel)
echo "📊 Coverage"
(cd backend && $PYBIN -m pytest tests/ --cov=app --cov-report=xml:coverage.xml --cov-report=term)

echo "✅ Backend CI script completed"

