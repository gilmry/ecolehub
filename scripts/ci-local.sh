#!/usr/bin/env bash
set -euo pipefail

# CI-like local runner to mirror .github/workflows/ci.yml
# - i18n lint (STRICT)
# - backend flake8
# - backend pytest (unit/integration/auth/sel + coverage)
# - security scans (bandit/safety) if available
# - docs checks

ROOT_DIR=$(cd "$(dirname "$0")/.." && pwd)
cd "$ROOT_DIR"

echo "🌐 i18n-lint (STRICT)"
if command -v rg >/dev/null 2>&1; then
  STRICT=1 ./scripts/i18n-lint.sh
else
  echo "⚠️ ripgrep (rg) not found; skipping i18n-lint" >&2
fi

echo "🐍 Backend: environment"
export STAGE=4 TESTING=1 DATABASE_URL=sqlite:///test.db REDIS_URL=redis://localhost:6379/15 SECRET_KEY=test-secret-key-for-ci-only

PYBIN="python3"
if [ -x backend/venv/bin/python ]; then
  PYBIN="backend/venv/bin/python"
fi

echo "📦 Ensure test dependencies (best effort)"
if [ -f backend/requirements.test.txt ]; then
  $PYBIN -m pip install -q -r backend/requirements.test.txt || true
fi

echo "🔍 flake8 (non-blocking strict then relaxed)"
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

echo "🛡️ Security scans (optional)"
if $PYBIN -m pip show bandit >/dev/null 2>&1 || $PYBIN -m pip install -q bandit; then
  (cd backend && bandit -r app/ -ll) || true
else
  echo "ℹ️ bandit not installed; skipping"
fi
if $PYBIN -m pip show safety >/dev/null 2>&1 || $PYBIN -m pip install -q safety; then
  if [ -f backend/requirements.test.txt ]; then
    (cd backend && safety check -r requirements.test.txt) || true
  fi
else
  echo "ℹ️ safety not installed; skipping"
fi

echo "📖 Docs checks"
[ -f README.md ] || { echo "❌ README.md missing"; exit 1; }
[ -f CHANGELOG.md ] || { echo "❌ CHANGELOG.md missing"; exit 1; }
[ -f docker-compose.traefik.yml ] || echo "⚠️ docker-compose.traefik.yml missing"
[ -f backend/pytest.ini ] || echo "⚠️ backend/pytest.ini missing"

echo "✅ CI-local checks completed"

