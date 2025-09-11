# 🔐 Gestion Sécurisée des Secrets EcoleHub

Cette documentation décrit l'implémentation complète de la gestion des secrets pour EcoleHub, permettant une sécurité renforcée tout en maintenant la simplicité d'utilisation.

## 🎯 Vue d'Ensemble

### Architecture Secrets par Stage

| Stage | Méthode | Secrets Gérés | Usage |
|-------|---------|---------------|-------|
| **0-1** | Variables d'env + fichiers locaux | `secret_key`, `db_password` | Développement |
| **2+** | Docker Compose secrets | Tous secrets | Production recommandée |
| **4** | Docker Swarm secrets | Rotation automatisée | Production scale |

### Secrets Gérés

- 🔴 **Critiques** : `secret_key`, `db_password`
- 🟡 **Importants** : `redis_password`, `minio_secret_key`  
- 🟢 **Normaux** : `grafana_password`, APIs externes

## 🚀 Installation Rapide

### 1. Génération des Secrets

```bash
# Génération automatique tous secrets Stage 4
./scripts/generate-secrets.sh --stage 4

# Forcer régénération
./scripts/generate-secrets.sh --force

# Aide complète
./scripts/generate-secrets.sh --help
```

### 2. Déploiement Développement

```bash
# Export pour variables d'environnement
./scripts/generate-secrets.sh --export-env

# Test de fonctionnement
python3 -c "
import os
exec(open('.env.secrets').read())
import sys; sys.path.append('backend/app')
from secrets_manager import secrets_manager
print('✅ Secrets OK' if all(secrets_manager.validate_secrets(4).values()) else '❌ Erreur')
"
```

### 3. Déploiement Production (Docker Secrets)

```bash
# Utiliser Docker Compose avec secrets
docker compose -f docker-compose.stage4-secrets.yml up -d

# Vérifier santé
curl http://localhost:8000/health

# Test complet
./scripts/test-secrets-deployment.sh
```

## 🔧 Utilisation Développement

### SecretsManager dans le Code

```python
from app.secrets_manager import get_jwt_secret, get_database_url, get_redis_url

# Configuration automatique avec fallback
try:
    SECRET_KEY = get_jwt_secret()           # Docker secrets ou env
    DATABASE_URL = get_database_url()       # URL avec mot de passe sécurisé
    REDIS_URL = get_redis_url()             # URL avec mot de passe sécurisé
except RuntimeError:
    # Fallback développement
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-fallback")
    DATABASE_URL = os.getenv("DATABASE_URL", "...")
```

### Validation des Secrets

```python
from app.secrets_manager import secrets_manager

# Validation complète
validation = secrets_manager.validate_secrets(stage=4)
print(f"Secrets valides: {all(validation.values())}")

# Secrets individuels
mollie_key = secrets_manager.read_secret('mollie_api_key')
```

## 🐳 Docker Compose Secrets

### Fichiers Disponibles

- `docker-compose.stage4-secrets.yml` - **Recommandé production**
- `docker-compose.stage2-secrets.yml` - Pour Stage 2
- `docker-compose.yml` - Original avec variables d'env

### Configuration Secrets

```yaml
services:
  postgres:
    environment:
      POSTGRES_PASSWORD_FILE: /run/secrets/db_password
    secrets:
      - db_password

secrets:
  db_password:
    file: ./secrets/db_password.txt
```

### Services Adaptés

- ✅ **PostgreSQL** : `POSTGRES_PASSWORD_FILE`
- ✅ **Redis** : Commande avec `$(cat /run/secrets/redis_password)`
- ✅ **MinIO** : Variables d'environnement dynamiques
- ✅ **Backend** : SecretsManager avec montage `/run/secrets/`
- ✅ **Grafana** : `GF_SECURITY_ADMIN_PASSWORD__FILE`

## 🔄 Rotation des Secrets

### Procédure Standard (3 mois)

```bash
# 1. Sauvegarde
cp -r secrets/ secrets.backup.$(date +%Y%m%d)/

# 2. Génération nouveaux secrets
./scripts/generate-secrets.sh --force

# 3. Redémarrage services (selon secret)
docker compose -f docker-compose.stage4-secrets.yml restart redis grafana

# 4. Validation
curl -f http://localhost:8000/health
```

### Rotation Critique (PostgreSQL)

```bash
# Procédure double-auth pour zero-downtime
# Voir docs/secrets-rotation.md pour procédure complète

# Test préalable
docker compose -f docker-compose.stage4-secrets.yml exec postgres \
  psql -U ecolehub -c "SELECT 1;"
```

### Rotation d'Urgence

```bash
# En cas de compromission
./scripts/emergency-rotation.sh

# Ou génération + restart immédiat  
./scripts/generate-secrets.sh --force
docker compose -f docker-compose.stage4-secrets.yml restart
```

## 🔒 Sécurité

### Permissions Fichiers

```bash
# Validation permissions
find secrets/ -type f ! -perm 600 -ls  # Doit être vide
find secrets/ -type d ! -perm 700 -ls  # Doit être vide

# Correction si nécessaire
chmod 700 secrets/
chmod 600 secrets/*.txt
```

### .gitignore Protection

```gitignore
# Secrets - NEVER COMMIT THESE!
secrets/
*.key
*.pem
.env.secrets
secrets-backup-*
*secret*.txt
*password*.txt
*api_key*.txt
```

### Audit des Accès

```bash
# Monitoring accès aux secrets (optionnel)
sudo auditctl -w /path/to/secrets/ -p rwxa -k ecolehub-secrets

# Vérifier les logs
sudo ausearch -k ecolehub-secrets
```

## ⚙️ Configuration par Stage

### Stage 0 : Minimal

```bash
# Seul secret_key requis
./scripts/generate-secrets.sh --stage 0

# Variables d'environnement suffit
export SECRET_KEY=$(cat secrets/secret_key.txt)
```

### Stage 2 : Messagerie

```bash  
# Secrets: secret_key, db_password, redis_password
./scripts/generate-secrets.sh --stage 2
docker compose -f docker-compose.stage2-secrets.yml up -d
```

### Stage 4 : Production Complète

```bash
# Tous les secrets + monitoring
./scripts/generate-secrets.sh --stage 4
docker compose -f docker-compose.stage4-secrets.yml up -d

# Vérification complète
curl http://localhost:8000/health     # Backend
curl http://localhost:3001/api/health # Grafana  
curl http://localhost:9000/minio/health/live # MinIO
```

## 🛠️ Dépannage

### Erreur "Secret manquant"

```bash
# Vérifier présence fichiers
ls -la secrets/

# Régénérer si nécessaire
./scripts/generate-secrets.sh --force

# Tester accès Docker
docker run --rm -v $(pwd)/secrets:/run/secrets alpine cat /run/secrets/secret_key.txt
```

### Service ne démarre pas

```bash
# Logs détaillés
docker compose -f docker-compose.stage4-secrets.yml logs [service]

# Test connexion manuelle
docker compose -f docker-compose.stage4-secrets.yml exec postgres \
  psql -U ecolehub -d ecolehub -c "SELECT version();"
```

### Problème permissions

```bash
# Reset permissions
sudo chown -R $USER:$USER secrets/
chmod 700 secrets/  
chmod 600 secrets/*.txt

# Vérification
ls -la secrets/
```

## 📚 Documentation Avancée

### Fichiers de Référence

- [`docs/secrets-rotation.md`](docs/secrets-rotation.md) - Procédures rotation complètes
- [`scripts/generate-secrets.sh`](scripts/generate-secrets.sh) - Script génération
- [`backend/app/secrets_manager.py`](backend/app/secrets_manager.py) - Gestionnaire Python
- [`scripts/test-secrets-deployment.sh`](scripts/test-secrets-deployment.sh) - Tests déploiement

### APIs Externes

- **Mollie** : Récupérer vraie clé depuis dashboard production
- **Printful** : Configurer webhook + clé API réelle
- **Monitoring** : Alertes sur échec rotation

### Migration Environnements

```bash
# Dev vers staging
scp -r secrets/ staging-server:/opt/ecolehub/
ssh staging-server "cd /opt/ecolehub && ./scripts/test-secrets-deployment.sh"

# Staging vers production  
# Utiliser procédures rotation pour migration zero-downtime
```

---

## ✅ Validation Finale

```bash
# Test complet de la solution
./scripts/test-secrets-deployment.sh

# Doit afficher:
# ✅ Script génération secrets: OK
# ✅ SecretsManager Python: OK  
# ✅ Docker Compose secrets: OK
# ✅ PostgreSQL avec secrets: OK
# ✅ Redis avec secrets: OK
# ✅ Documentation rotation: Créée
# ✅ .gitignore sécurisé: OK
# 🚀 La gestion des secrets EcoleHub est prête pour la production!
```

---

> 🔐 **Note Sécurité** : Cette implémentation suit les meilleures pratiques Docker secrets avec fallback sécurisé pour le développement. Tous les secrets sont générés cryptographiquement et jamais exposés dans les logs ou git.