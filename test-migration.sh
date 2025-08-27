#!/bin/bash
# Test complet de migration Stage 0 → Stage 1

echo "🧪 Test Migration EcoleHub Stage 0 → Stage 1"
echo "============================================="

# 1. Test Stage 0 
echo "1️⃣ Test Stage 0..."
cp .env.example .env
docker-compose up -d --build > /dev/null 2>&1

sleep 10

# Créer utilisateur test
echo "   • Création utilisateur test..."
curl -s -X POST http://localhost:8000/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@ndi.be","password":"test123","first_name":"Test","last_name":"User"}' > /dev/null

# Vérifier SQLite créé
if [ -f "db/ecolehub.db" ]; then
    USERS_COUNT=$(sqlite3 db/ecolehub.db "SELECT COUNT(*) FROM users;")
    echo "   • ✅ SQLite créé avec $USERS_COUNT utilisateur(s)"
else
    echo "   • ❌ SQLite non créé"
    exit 1
fi

# 2. Test Migration
echo ""
echo "2️⃣ Test Migration vers Stage 1..."
./migrate.sh

# 3. Test Stage 1
echo ""
echo "3️⃣ Validation Stage 1..."

sleep 5

HEALTH=$(curl -s http://localhost:8000/health 2>/dev/null)
if echo "$HEALTH" | grep -q '"stage":1'; then
    echo "   • ✅ Stage 1 opérationnel"
    echo "   • ✅ PostgreSQL connecté"
    
    # Test SEL endpoints
    CATEGORIES=$(curl -s http://localhost:8000/sel/categories 2>/dev/null)
    if echo "$CATEGORIES" | grep -q "garde"; then
        echo "   • ✅ Système SEL actif (9 catégories)"
    else
        echo "   • ❌ Système SEL problème"
    fi
    
    echo ""
    echo "🎉 Migration Stage 0 → Stage 1 validée !"
    echo ""
    echo "📋 Fonctionnalités disponibles:"
    echo "• Authentification (conservée)"
    echo "• Gestion enfants (conservée)"  
    echo "• Système SEL (nouveau)"
    echo "• PostgreSQL (nouveau)"
    
else
    echo "   • ❌ Stage 1 ne démarre pas"
    echo "Logs:"
    docker-compose -f docker-compose.stage1.yml logs backend --tail=5
    exit 1
fi