#!/bin/bash
# EcoleHub avec Traefik pour ngrok

echo "🚀 Lancement EcoleHub avec Traefik"
echo "=================================="

# Vérifications
if [ ! -f "docker-compose.traefik.yml" ]; then
    echo "❌ Configuration Traefik non trouvée"
    exit 1
fi

# Configuration
echo "⚙️ Configuration EcoleHub + Traefik..."
cp .env.stage4.example .env

# Arrêt des services existants
echo "🛑 Arrêt services existants..."
docker compose -f docker-compose.stage3.yml down 2>/dev/null || true
docker compose -f docker-compose.stage4.yml down 2>/dev/null || true

# Lancement avec Traefik
echo "🚀 Lancement EcoleHub avec Traefik..."
docker compose -f docker-compose.traefik.yml up -d --build

# Attendre démarrage
echo "⏳ Attente démarrage complet..."
sleep 20

# Vérifications
echo "🔍 Vérification services..."
HEALTH=$(curl -s http://localhost/health 2>/dev/null || echo "")

if echo "$HEALTH" | grep -q '"status":"healthy"'; then
    echo "✅ EcoleHub opérationnel via Traefik !"
    echo ""
    echo "🌐 URLs Traefik:"
    echo "• EcoleHub: http://localhost"
    echo "• API directe: http://api.localhost"
    echo "• Traefik Dashboard: http://localhost:8080"
    echo "• Prometheus: http://prometheus.localhost"
    echo "• Grafana: http://grafana.localhost"
    echo "• MinIO Console: http://minio-console.localhost"
    echo ""
    echo "🔗 POUR NGROK:"
    echo "ngrok http 80"
    echo "→ EcoleHub sera accessible via URL ngrok"
    echo ""
    echo "📊 Services actifs:"
    docker compose -f docker-compose.traefik.yml ps --format "table {{.Service}}\t{{.Status}}"
    
else
    echo "❌ Problème démarrage EcoleHub"
    echo "Logs Traefik:"
    docker compose -f docker-compose.traefik.yml logs traefik --tail=5
fi