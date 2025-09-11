#!/bin/bash
# Test de la gestion des secrets Traefik EcoleHub

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

# Couleurs
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "🔐 Test de la gestion des secrets Traefik"
echo "========================================"

# Test 1: Vérifier que les secrets existent
echo -n "✅ Test 1 - Secrets générés... "
if [[ -f "$PROJECT_DIR/secrets/traefik_users.txt" ]] && [[ -f "$PROJECT_DIR/secrets/traefik_admin_password.txt" ]]; then
    echo -e "${GREEN}OK${NC}"
else
    echo -e "${RED}ERREUR${NC} - Secrets Traefik manquants"
    exit 1
fi

# Test 2: Vérifier que les conteneurs sont UP
echo -n "✅ Test 2 - Conteneurs démarrés... "
if docker compose -f docker-compose.traefik-secrets.yml ps postgres | grep -q healthy && \
   docker compose -f docker-compose.traefik-secrets.yml ps redis | grep -q healthy; then
    echo -e "${GREEN}OK${NC}"
else
    echo -e "${RED}ERREUR${NC} - Conteneurs non healthy"
    exit 1
fi

# Test 3: Tester PostgreSQL avec secret
echo -n "✅ Test 3 - PostgreSQL avec secret... "
if docker compose -f docker-compose.traefik-secrets.yml exec -T postgres psql -U ecolehub -d ecolehub -c "SELECT 1;" > /dev/null 2>&1; then
    echo -e "${GREEN}OK${NC}"
else
    echo -e "${RED}ERREUR${NC} - PostgreSQL secret failed"
    exit 1
fi

# Test 4: Tester Redis avec secret
echo -n "✅ Test 4 - Redis avec secret... "
if docker compose -f docker-compose.traefik-secrets.yml exec -T redis redis-cli -a "$(cat $PROJECT_DIR/secrets/redis_password.txt)" ping > /dev/null 2>&1; then
    echo -e "${GREEN}OK${NC}"
else
    echo -e "${RED}ERREUR${NC} - Redis secret failed"
    exit 1
fi

# Test 5: Vérifier montage secrets dans Traefik
echo -n "✅ Test 5 - Secrets montés dans Traefik... "
if docker compose -f docker-compose.traefik-secrets.yml exec -T traefik cat /run/secrets/traefik_users.txt > /dev/null 2>&1; then
    echo -e "${GREEN}OK${NC}"
else
    echo -e "${RED}ERREUR${NC} - Secrets non montés dans Traefik"
    exit 1
fi

# Test 6: Valider format htpasswd
echo -n "✅ Test 6 - Format htpasswd valide... "
traefik_auth=$(docker compose -f docker-compose.traefik-secrets.yml exec -T traefik cat /run/secrets/traefik_users.txt | tr -d '\r\n')
if [[ "$traefik_auth" =~ ^admin:\$[a-z0-9]+\$ ]]; then
    echo -e "${GREEN}OK${NC}"
else
    echo -e "${RED}ERREUR${NC} - Format htpasswd invalide"
    exit 1
fi

echo ""
echo "🎉 Tous les tests secrets Traefik sont passés !"
echo ""
echo "📝 Informations de connexion :"
echo "   • Utilisateur Traefik: admin"
echo "   • Mot de passe: $(cat $PROJECT_DIR/secrets/traefik_admin_password.txt)"
echo "   • URL Dashboard: https://traefik.ecolehub.be/ (production)"
echo ""
echo "🔒 Sécurité :"
echo "   • Tous les secrets utilisent Docker secrets"
echo "   • Authentification htpasswd pour Traefik"
echo "   • PostgreSQL et Redis protégés par mots de passe"
echo ""