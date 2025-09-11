# 🔐 Guide de Rotation des Secrets EcoleHub

Ce guide décrit les procédures de rotation sécurisée des secrets pour maintenir la sécurité d'EcoleHub sans interruption de service.

## 🎯 Vue d'Ensemble

### Fréquence de Rotation Recommandée

| Secret | Fréquence | Criticité | Notes |
|--------|-----------|-----------|-------|
| `secret_key` | 6 mois | 🔴 Critique | JWT signing - rotation complexe |
| `db_password` | 3 mois | 🔴 Critique | PostgreSQL - rotation délicate |
| `redis_password` | 3 mois | 🟡 Important | Cache - rotation rapide |
| `grafana_password` | 1 mois | 🟢 Normal | Dashboard admin |
| `minio_secret_key` | 3 mois | 🟡 Important | Stockage fichiers |
| `mollie_api_key` | À la demande | 🔴 Critique | Clé fournie par Mollie |
| `printful_api_key` | À la demande | 🟢 Normal | Clé fournie par Printful |

### Principe Zero-Downtime

Toutes les rotations suivent le principe **Blue-Green** :
1. Générer nouveau secret 
2. Configurer les services pour accepter ancien ET nouveau
3. Déployer progressivement le nouveau
4. Supprimer l'ancien après validation

## 🔄 Procédures de Rotation

### 1. Rotation Secrets Non-Critiques (Redis, Grafana, MinIO)

**Durée estimée : 5-10 minutes**

```bash
# 1. Sauvegarder les secrets actuels
cp -r secrets/ secrets.backup.$(date +%Y%m%d-%H%M%S)/

# 2. Générer nouveaux secrets
./scripts/generate-secrets.sh --force --stage 4

# 3. Redémarrer les services concernés
docker compose -f docker-compose.stage4-secrets.yml restart redis grafana minio

# 4. Vérifier que tout fonctionne
curl -f http://localhost:8000/health
curl -f http://localhost:3001/api/health  # Grafana
curl -f http://localhost:9000/minio/health/live  # MinIO

# 5. Valider les nouvelles connexions
docker compose -f docker-compose.stage4-secrets.yml exec backend python -c "
from app.secrets_manager import secrets_manager
print('Validation:', secrets_manager.validate_secrets(stage=4))
"
```

### 2. Rotation Base de Données (PostgreSQL) 

**Durée estimée : 15-30 minutes** ⚠️ **Opération critique**

```bash
# Phase 1: Préparation (sans interruption)
echo "Phase 1: Préparation du nouveau mot de passe"

# Sauvegarder
cp secrets/db_password.txt secrets/db_password.old.txt

# Générer nouveau mot de passe
openssl rand -base64 32 | tr -d "=+/" | cut -c1-32 > secrets/db_password.new.txt

# Phase 2: Double authentification PostgreSQL
echo "Phase 2: Configuration double auth"

# Se connecter à PostgreSQL avec l'ancien mot de passe
docker compose -f docker-compose.stage4-secrets.yml exec postgres psql -U ecolehub -d ecolehub -c "
-- Créer utilisateur temporaire avec nouveau mot de passe
CREATE USER ecolehub_new WITH PASSWORD '$(cat secrets/db_password.new.txt)';
GRANT ALL PRIVILEGES ON DATABASE ecolehub TO ecolehub_new;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO ecolehub_new;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO ecolehub_new;
"

# Phase 3: Test de connexion
echo "Phase 3: Test nouveau mot de passe"
docker run --rm --network schoolhub_ecolehub postgres:15-alpine \
  psql -h postgres -U ecolehub_new -d ecolehub -c "SELECT 1;" || {
  echo "❌ Échec test connexion - ARRÊT de la rotation"
  exit 1
}

# Phase 4: Rotation finale
echo "Phase 4: Rotation finale"

# Remplacer le secret
mv secrets/db_password.new.txt secrets/db_password.txt

# Redémarrer les services backend
docker compose -f docker-compose.stage4-secrets.yml restart backend celery

# Attendre que les services redémarrent
sleep 30

# Phase 5: Nettoyage 
echo "Phase 5: Nettoyage"

# Supprimer l'ancien utilisateur
docker compose -f docker-compose.stage4-secrets.yml exec postgres psql -U ecolehub -d ecolehub -c "
DROP USER IF EXISTS ecolehub_old;  -- Au cas où
"

# Vérification finale
curl -f http://localhost:8000/health || {
  echo "❌ Service backend ne répond pas - RESTAURATION nécessaire!"
  mv secrets/db_password.txt secrets/db_password.failed.txt  
  mv secrets/db_password.old.txt secrets/db_password.txt
  docker compose -f docker-compose.stage4-secrets.yml restart backend
  exit 1
}

echo "✅ Rotation PostgreSQL terminée avec succès"
rm secrets/db_password.old.txt
```

### 3. Rotation JWT Secret Key 

**Durée estimée : 30-60 minutes** ⚠️ **Rotation la plus complexe**

Cette rotation nécessite une stratégie spéciale car elle invalide tous les tokens JWT existants.

```bash
# Phase 1: Notification utilisateurs
echo "Phase 1: Notification utilisateurs (24h avant)"
# Envoyer email aux utilisateurs : "Maintenance planifiée - reconnexion requise"

# Phase 2: Génération du nouveau secret
echo "Phase 2: Préparation (jour J)"
cp secrets/secret_key.txt secrets/secret_key.old.txt
openssl rand -base64 64 | tr -d "=+/" | cut -c1-64 > secrets/secret_key.new.txt

# Phase 3: Configuration Double JWT (modification backend temporaire)
# OPTION A: Maintenance programmée (recommandé)
echo "🚨 DÉBUT MAINTENANCE - Service temporairement indisponible"

# Arrêt propre
docker compose -f docker-compose.stage4-secrets.yml stop backend celery

# Rotation du secret
mv secrets/secret_key.new.txt secrets/secret_key.txt

# Redémarrage
docker compose -f docker-compose.stage4-secrets.yml start backend celery

# Attendre démarrage
sleep 60

# Vérification
curl -f http://localhost:8000/health || {
  echo "❌ ÉCHEC - Restauration de l'ancien secret"
  docker compose -f docker-compose.stage4-secrets.yml stop backend
  mv secrets/secret_key.txt secrets/secret_key.failed.txt
  mv secrets/secret_key.old.txt secrets/secret_key.txt  
  docker compose -f docker-compose.stage4-secrets.yml start backend
  exit 1
}

echo "✅ Rotation JWT terminée - Tous les utilisateurs doivent se reconnecter"

# OPTION B: Double validation (avancé - nécessite modification code)
# Modifier temporairement secrets_manager.py pour accepter ancien ET nouveau secret
# Puis migration progressive sur 24-48h
```

### 4. Rotation Clés API Externes

#### Mollie API Key

```bash
# 1. Obtenir nouvelle clé depuis dashboard Mollie
echo "Récupérez la nouvelle clé API depuis https://my.mollie.com/"
read -p "Nouvelle clé Mollie: " NEW_MOLLIE_KEY

# 2. Tester la nouvelle clé
curl -H "Authorization: Bearer $NEW_MOLLIE_KEY" \
  "https://api.mollie.com/v2/methods" || {
  echo "❌ Clé Mollie invalide"
  exit 1
}

# 3. Rotation
echo "$NEW_MOLLIE_KEY" > secrets/mollie_api_key.txt
chmod 600 secrets/mollie_api_key.txt

# 4. Redémarrer
docker compose -f docker-compose.stage4-secrets.yml restart backend celery

# 5. Test paiement (staging)
curl -f http://localhost:8000/shop/test-payment || echo "⚠️ Vérifiez les paiements"
```

#### Printful API Key

```bash
# Similaire à Mollie
echo "Récupérez la nouvelle clé depuis dashboard Printful"
read -p "Nouvelle clé Printful: " NEW_PRINTFUL_KEY

echo "$NEW_PRINTFUL_KEY" > secrets/printful_api_key.txt
chmod 600 secrets/printful_api_key.txt

docker compose -f docker-compose.stage4-secrets.yml restart backend celery
```

## 🚨 Procédures d'Urgence

### Rotation d'Urgence (Compromission Détectée)

```bash
#!/bin/bash
# scripts/emergency-rotation.sh

echo "🚨 ROTATION D'URGENCE - SECRETS COMPROMIS 🚨"

# 1. Générer tous les secrets immédiatement
./scripts/generate-secrets.sh --force --stage 4

# 2. Redémarrer TOUS les services
docker compose -f docker-compose.stage4-secrets.yml restart

# 3. Forcer déconnexion de tous les utilisateurs (JWT invalidé)
echo "⚠️ Tous les utilisateurs seront déconnectés"

# 4. Notification
echo "📧 Envoyer notification incident sécurité aux administrateurs"

# 5. Logs d'audit
echo "$(date): Rotation d'urgence effectuée" >> logs/security-audit.log

# 6. Vérification
sleep 30
curl -f http://localhost:8000/health || {
  echo "❌ SYSTÈME DOWN - Intervention manuelle requise"
  exit 1
}

echo "✅ Rotation d'urgence terminée"
```

### Rollback en Cas d'Échec

```bash
#!/bin/bash
# scripts/rollback-secrets.sh SECRET_NAME

SECRET_NAME=$1

if [[ -f "secrets/${SECRET_NAME}.old.txt" ]]; then
  echo "🔄 Rollback de $SECRET_NAME"
  
  cp "secrets/${SECRET_NAME}.txt" "secrets/${SECRET_NAME}.failed.txt"
  mv "secrets/${SECRET_NAME}.old.txt" "secrets/${SECRET_NAME}.txt"
  
  # Redémarrer services affectés
  case $SECRET_NAME in
    "secret_key"|"db_password")
      docker compose -f docker-compose.stage4-secrets.yml restart backend celery
      ;;
    "redis_password")  
      docker compose -f docker-compose.stage4-secrets.yml restart redis backend
      ;;
    "grafana_password")
      docker compose -f docker-compose.stage4-secrets.yml restart grafana
      ;;
  esac
  
  echo "✅ Rollback terminé pour $SECRET_NAME"
else
  echo "❌ Pas de backup trouvé pour $SECRET_NAME"
  exit 1
fi
```

## 📋 Checklist Post-Rotation

### Vérifications Obligatoires

- [ ] **Services opérationnels**
  ```bash
  curl -f http://localhost:8000/health
  curl -f http://localhost:3001/api/health
  curl -f http://localhost:9000/minio/health/live
  ```

- [ ] **Authentification fonctionnelle**
  ```bash
  # Test login API
  curl -X POST http://localhost:8000/login \
    -H "Content-Type: application/json" \
    -d '{"email":"test@ecolehub.be","password":"test123"}'
  ```

- [ ] **Base de données accessible**
  ```bash
  docker compose -f docker-compose.stage4-secrets.yml exec postgres \
    psql -U ecolehub -d ecolehub -c "SELECT COUNT(*) FROM users;"
  ```

- [ ] **Cache Redis fonctionnel**
  ```bash
  docker compose -f docker-compose.stage4-secrets.yml exec redis \
    redis-cli -a $(cat secrets/redis_password.txt) ping
  ```

- [ ] **Stockage MinIO accessible**
  ```bash
  curl -f http://localhost:9000/minio/health/live
  ```

- [ ] **API externes (si rotation)**
  - Test Mollie: `curl -H "Authorization: Bearer $(cat secrets/mollie_api_key.txt)" https://api.mollie.com/v2/methods`
  - Test Printful: Vérifier dashboard

### Documentation de Rotation

```bash
# Créer rapport de rotation
cat > "logs/rotation-report-$(date +%Y%m%d).md" << EOF
# Rapport de Rotation Secrets - $(date)

## Secrets Rotés
- [x] secret_key: $(date)
- [x] db_password: $(date) 
- [x] redis_password: $(date)

## Durée Opération
- Début: $(date -d '30 minutes ago')  
- Fin: $(date)
- Interruption service: 2 minutes

## Vérifications Post-Rotation
- [x] API Health Check: OK
- [x] Authentification: OK  
- [x] Base de données: OK
- [x] Paiements: OK

## Prochaine Rotation Programmée
$(date -d '+3 months')
EOF
```

## 🔐 Sécurité des Backups

### Chiffrement des Sauvegardes

```bash
# Backup chiffré des secrets
tar czf secrets-backup-$(date +%Y%m%d).tar.gz secrets/
gpg --symmetric --cipher-algo AES256 secrets-backup-$(date +%Y%m%d).tar.gz
rm secrets-backup-$(date +%Y%m%d).tar.gz

# Stockage sécurisé (à adapter selon infrastructure)
# scp secrets-backup-*.tar.gz.gpg admin@backup-server:/secure-backups/
```

### Audit des Accès

```bash
# Log des accès aux secrets
sudo auditctl -w /home/user/schoolhub/secrets/ -p rwxa -k ecolehub-secrets

# Vérification des permissions
find secrets/ -type f ! -perm 600 -exec chmod 600 {} \;
find secrets/ -type d ! -perm 700 -exec chmod 700 {} \;
```

---

## ⚡ Quick Reference

### Commandes Essentielles

```bash
# Rotation complète (non-critique)
./scripts/generate-secrets.sh --force && docker compose -f docker-compose.stage4-secrets.yml restart

# Test santé système  
curl -f http://localhost:8000/health

# Validation secrets
docker compose exec backend python -c "from app.secrets_manager import secrets_manager; print(secrets_manager.validate_secrets(4))"

# Rotation d'urgence
./scripts/emergency-rotation.sh

# Rollback
./scripts/rollback-secrets.sh secret_name
```

### Contacts d'Urgence

- **Technique**: Admin système EcoleHub
- **Mollie**: Support via dashboard  
- **Printful**: Support API documentation

---

> ⚠️ **Important**: Testez toujours les procédures en environnement de développement avant la production !