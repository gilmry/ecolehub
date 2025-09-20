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
  ./scripts/ci-i18n.sh
else
  echo "⚠️ ripgrep (rg) not found; skipping i18n-lint" >&2
fi

echo "🐍 Backend: environment"
export STAGE=4 TESTING=1 DATABASE_URL=sqlite:///test.db REDIS_URL=redis://localhost:6379/15 SECRET_KEY=test-secret-key-for-ci-only

PYBIN="python3"
if [ -x "$ROOT_DIR/backend/venv/bin/python" ]; then
  PYBIN="$ROOT_DIR/backend/venv/bin/python"
elif [ -x "$ROOT_DIR/venv/bin/python" ]; then
  PYBIN="$ROOT_DIR/venv/bin/python"
fi

echo "📦 Ensure test dependencies (best effort)"
if [ -f backend/requirements.test.txt ]; then
  $PYBIN -m pip install -q -r backend/requirements.test.txt || true
fi

echo "🔧 Install formatting tools"
$PYBIN -m pip install -q black isort autopep8 autoflake || echo "⚠️ Some formatting tools failed to install"

./scripts/ci-backend.sh

echo "🛡️ Security scans (optional)"
# Prefer venv-provided tools; fall back gracefully if unavailable
if $PYBIN -c 'import bandit' >/dev/null 2>&1; then
  $PYBIN -m bandit -r backend/app/ -ll || true
else
  echo "ℹ️ bandit not installed; skipping"
fi
if $PYBIN -c 'import safety' >/dev/null 2>&1; then
  # Verbose mode: show safety output if SAFETY_VERBOSE=1
  if [ "${SAFETY_VERBOSE:-0}" = "1" ]; then
    # Scan runtime dependencies
    if [ -f backend/requirements.txt ]; then
      $PYBIN -m safety scan -r backend/requirements.txt \
        || $PYBIN -m safety check -r backend/requirements.txt \
        || echo "ℹ️ safety (runtime) scan/check skipped"
    fi
    # Scan test/dev dependencies
    if [ -f backend/requirements.test.txt ]; then
      $PYBIN -m safety scan -r backend/requirements.test.txt \
        || $PYBIN -m safety check -r backend/requirements.test.txt \
        || echo "ℹ️ safety (test) scan/check skipped"
    fi
  else
    # Silent mode: suppress noisy output (default for CI scripts)
    if [ -f backend/requirements.txt ]; then
      ($PYBIN -m safety scan -r backend/requirements.txt >/dev/null 2>&1) \
        || ($PYBIN -m safety check -r backend/requirements.txt >/dev/null 2>&1) \
        || echo "ℹ️ safety (runtime) scan/check skipped"
    fi
    if [ -f backend/requirements.test.txt ]; then
      ($PYBIN -m safety scan -r backend/requirements.test.txt >/dev/null 2>&1) \
        || ($PYBIN -m safety check -r backend/requirements.test.txt >/dev/null 2>&1) \
        || echo "ℹ️ safety (test) scan/check skipped"
    fi
  fi
else
  echo "ℹ️ safety not installed; skipping"
fi

echo "♿ Accessibility (frontend)"
# Serve frontend with Python and run pa11y audit (non-strict by default)
bash -c 'set -euo pipefail; \
  PORT=${A11Y_FRONTEND_PORT:-8089}; \
  (cd frontend && python3 -m http.server $PORT >/dev/null 2>&1 &) ; \
  PID=$!; trap "kill $PID >/dev/null 2>&1 || true" EXIT; \
  sleep 2; \
  BASE_URL=http://localhost:$PORT STRICT=${A11Y_STRICT:-0} ./scripts/a11y-audit.sh'

echo "📖 Docs checks"
[ -f README.md ] || { echo "❌ README.md missing"; exit 1; }
[ -f CHANGELOG.md ] || { echo "❌ CHANGELOG.md missing"; exit 1; }
[ -f docker-compose.traefik.yml ] || echo "⚠️ docker-compose.traefik.yml missing"
[ -f backend/pytest.ini ] || echo "⚠️ backend/pytest.ini missing"

echo "✅ CI-local checks completed"
