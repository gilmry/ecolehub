#!/usr/bin/env bash
set -euo pipefail

# Script de formatage automatique du code Python
# Utilise autoflake, isort, autopep8 et black dans l'ordre

ROOT_DIR=$(cd "$(dirname "$0")/.." && pwd)
cd "$ROOT_DIR/backend"

PYBIN="python3"
if [ -x venv/bin/python ]; then
    PYBIN="venv/bin/python"
fi

echo "🎨 Formatage automatique du code Python"

# 1. autoflake: supprime les imports et variables inutilisés
echo "  🧹 autoflake: suppression des imports/variables inutilisés"
if $PYBIN -c "import autoflake" 2>/dev/null; then
    find app tests -name "*.py" -exec $PYBIN -m autoflake \
        --in-place \
        --remove-all-unused-imports \
        --remove-unused-variables \
        --remove-duplicate-keys \
        --expand-star-imports \
        {} \; || echo "⚠️ autoflake: quelques erreurs ignorées"
else
    echo "  ⚠️ autoflake non disponible"
fi

# 2. isort: tri des imports
echo "  📚 isort: tri des imports"
if $PYBIN -c "import isort" 2>/dev/null; then
    $PYBIN -m isort app tests --profile black || echo "⚠️ isort: quelques erreurs ignorées"
else
    echo "  ⚠️ isort non disponible"
fi

# 3. autopep8: corrections PEP8 (conservative pour éviter de casser les f-strings)
echo "  🔧 autopep8: corrections PEP8 conservatrices"
if $PYBIN -c "import autopep8" 2>/dev/null; then
    find app tests -name "*.py" -exec $PYBIN -m autopep8 \
        --in-place \
        --max-line-length 88 \
        --select=E1,E2,E3,W1,W2,W3 \
        {} \; || echo "⚠️ autopep8: quelques erreurs ignorées"
else
    echo "  ⚠️ autopep8 non disponible"
fi

# 4. black: formatage final (safe pour les f-strings)
echo "  ⚫ black: formatage final"
if $PYBIN -c "import black" 2>/dev/null; then
    $PYBIN -m black app tests --line-length 88 --safe || echo "⚠️ black: quelques erreurs ignorées"
else
    echo "  ⚠️ black non disponible"
fi

echo "✅ Formatage terminé"