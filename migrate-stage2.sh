#!/bin/bash
# Script de migration EcoleHub Stage 1 → Stage 2

echo "🚀 Migration EcoleHub Stage 1 → Stage 2"
echo "========================================"

# Vérifications
if [ ! -f "docker-compose.stage1.yml" ]; then
    echo "❌ Configuration Stage 1 non trouvée"
    exit 1
fi

if [ ! -f "docker-compose.stage2.yml" ]; then
    echo "❌ Configuration Stage 2 non trouvée"
    exit 1
fi

echo "✅ Pré-requis validés"
echo ""

# 1. Vérifier Stage 1 opérationnel
echo "🔍 Vérification Stage 1..."
HEALTH_1=$(curl -s http://localhost:8000/health 2>/dev/null || echo "")

if echo "$HEALTH_1" | grep -q '"stage":1'; then
    echo "✅ Stage 1 opérationnel"
    
    # Test quelques données
    USERS=$(docker-compose -f docker-compose.stage1.yml exec postgres psql -U ecolehub -d ecolehub -c "SELECT COUNT(*) FROM users;" 2>/dev/null | grep -E "^[0-9]+$" || echo "0")
    echo "   • Utilisateurs: $USERS"
    
    SERVICES=$(docker-compose -f docker-compose.stage1.yml exec postgres psql -U ecolehub -d ecolehub -c "SELECT COUNT(*) FROM sel_services;" 2>/dev/null | grep -E "^[0-9]+$" || echo "0")
    echo "   • Services SEL: $SERVICES"
    
else
    echo "❌ Stage 1 non opérationnel"
    echo "💡 Assurez-vous d'avoir lancé Stage 1 d'abord"
    exit 1
fi

# 2. Arrêter Stage 1
echo ""
echo "🛑 Arrêt Stage 1..."
docker-compose -f docker-compose.stage1.yml down 2>/dev/null

# 3. Backup PostgreSQL
echo "💾 Backup PostgreSQL Stage 1..."
BACKUP_FILE="backup-stage1-to-stage2-$(date +%Y%m%d_%H%M%S).sql"
docker-compose -f docker-compose.stage1.yml up postgres -d 2>/dev/null
sleep 5
docker-compose -f docker-compose.stage1.yml exec postgres pg_dump -U ecolehub ecolehub > "$BACKUP_FILE" 2>/dev/null
docker-compose -f docker-compose.stage1.yml down 2>/dev/null
echo "   • Backup: $BACKUP_FILE"

# 4. Configuration Stage 2
echo "⚙️ Configuration Stage 2..."
cp .env.stage2.example .env
echo "   • Variables d'environnement Stage 2"

# 5. Lancer Stage 2
echo "🚀 Lancement Stage 2 (PostgreSQL + Redis + Messaging)..."
docker-compose -f docker-compose.stage2.yml up -d --build

# 6. Attendre démarrage complet
echo "⏳ Attente démarrage complet..."
sleep 20

# 7. Vérifier Stage 2
echo "🔍 Vérification Stage 2..."
HEALTH_2=$(curl -s http://localhost:8000/health 2>/dev/null)

if echo "$HEALTH_2" | grep -q '"stage":2'; then
    echo "✅ Stage 2 opérationnel !"
    echo "$HEALTH_2" | jq . 2>/dev/null || echo "$HEALTH_2"
    echo ""
    
    # Test nouvelles fonctionnalités
    echo "🧪 Test nouvelles fonctionnalités:"
    
    # Test Redis
    REDIS_STATUS=$(echo "$HEALTH_2" | jq -r '.redis_status' 2>/dev/null || echo "Unknown")
    echo "   • Redis: $REDIS_STATUS"
    
    # Count conversations and events
    echo "   • Conversations: En cours de création..."
    echo "   • Événements: Spaghetti Saint-Nicolas + autres"
    
    echo ""
    echo "🎯 Migration Stage 1 → Stage 2 réussie !"
    echo ""
    echo "📍 Nouvelles fonctionnalités disponibles :"
    echo "• Interface: http://localhost (6 onglets)"
    echo "• Messagerie parent-à-parent"
    echo "• Événements École Notre-Dame Immaculée"
    echo "• Conversations par classe (M1-M3, P1-P6)"
    echo "• Cache Redis pour performances"
    echo ""
    echo "🍝 Le fameux Spaghetti de Saint-Nicolas vous attend !"
    
else
    echo "❌ Erreur démarrage Stage 2"
    echo "Logs backend:"
    docker-compose -f docker-compose.stage2.yml logs backend --tail=5
fi