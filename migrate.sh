#!/bin/bash
# Script de migration EcoleHub Stage 0 → Stage 1

echo "🚀 Migration EcoleHub Stage 0 → Stage 1"
echo "========================================"

# Vérifications
if [ ! -f "db/ecolehub.db" ]; then
    echo "❌ Base SQLite non trouvée dans db/ecolehub.db"
    echo "💡 Assurez-vous d'avoir lancé Stage 0 d'abord"
    exit 1
fi

if [ ! -f "docker-compose.stage1.yml" ]; then
    echo "❌ Configuration Stage 1 non trouvée"
    exit 1
fi

echo "✅ Pré-requis validés"
echo ""

# 1. Arrêter Stage 0
echo "🛑 Arrêt Stage 0..."
docker-compose down 2>/dev/null

# 2. Backup SQLite
BACKUP_FILE="db/ecolehub-stage0-backup-$(date +%Y%m%d_%H%M%S).db"
cp db/ecolehub.db "$BACKUP_FILE"
echo "💾 Backup SQLite: $BACKUP_FILE"

# 3. Configuration Stage 1
echo "⚙️ Configuration Stage 1..."
cp .env.stage1.example .env
echo "   • Variables d'environnement mises à jour"

# 4. Basculer frontend Stage 1
echo "🎨 Basculement frontend Stage 1..."
cp frontend/index.html frontend/index-stage0.html.bak
cp frontend/index-stage1.html frontend/index.html

# 5. Lancer Stage 1
echo "🚀 Lancement Stage 1 (PostgreSQL + SEL)..."
docker-compose -f docker-compose.stage1.yml up -d --build

# 6. Attendre que PostgreSQL soit prêt
echo "⏳ Attente PostgreSQL..."
sleep 15

# 7. Vérifier que tout fonctionne
echo "🔍 Vérification Stage 1..."
HEALTH=$(curl -s http://localhost:8000/health 2>/dev/null)

if echo "$HEALTH" | grep -q '"stage":1'; then
    echo "✅ Stage 1 opérationnel !"
    echo "$HEALTH"
    echo ""
    echo "🎯 Migration terminée avec succès !"
    echo ""
    echo "📍 Prochaines étapes :"
    echo "• Interface: http://localhost"
    echo "• API: http://localhost:8000"
    echo "• Créer un compte pour tester le système SEL"
    echo ""
    echo "💡 Note: Les anciens comptes Stage 0 ne sont pas encore migrés"
    echo "   Créez de nouveaux comptes ou utilisez le script de migration des données"
else
    echo "❌ Erreur démarrage Stage 1"
    echo "Logs backend:"
    docker-compose -f docker-compose.stage1.yml logs backend --tail=5
fi