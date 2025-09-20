# 🛠️ EcoleHub Scripts & Tools

Cette collection d'outils facilite la gestion et l'administration d'EcoleHub.

## 🔧 Outils de Gestion

### `ecolehub-cli.py` - CLI Principal
Interface en ligne de commande pour la gestion des utilisateurs et comptes.

```bash
# Gestion des utilisateurs
python scripts/ecolehub-cli.py users list
python scripts/ecolehub-cli.py users create --email admin@school.com
python scripts/ecolehub-cli.py users reset-password --email user@school.com

# Gestion des enfants
python scripts/ecolehub-cli.py children list --parent-email parent@school.com
```

### `ecolehub-manager.sh` - Manager Shell
Script bash simplifié pour les opérations courantes via Docker.

```bash
# Gestion des services
./scripts/ecolehub-manager.sh start
./scripts/ecolehub-manager.sh stop
./scripts/ecolehub-manager.sh status

# Gestion des utilisateurs
./scripts/ecolehub-manager.sh users:list
./scripts/ecolehub-manager.sh users:create admin@school.com
```

## 🔐 Outils de Sécurité

### `generate-secrets.sh` - Génération de Secrets
Génère des mots de passe sécurisés pour tous les services.

```bash
# Génération complète
./scripts/generate-secrets.sh

# Génération pour production
./scripts/generate-secrets.sh --production
```

### `password_utils.py` - Utilitaires Mots de Passe
Outils Python pour la gestion des mots de passe.

```bash
# Hacher un mot de passe
python scripts/password_utils.py hash "motdepasse"

# Vérifier un mot de passe
python scripts/password_utils.py verify "motdepasse" "$hash"
```

## 🧪 Outils de Test

### `run-tests-local.sh` - Tests Locaux
Lance les tests dans l'environnement local.

```bash
# Tests complets
./scripts/run-tests-local.sh

# Tests spécifiques
./scripts/run-tests-local.sh unit
./scripts/run-tests-local.sh integration
```

### `test-secrets-deployment.sh` - Test Déploiement Secrets
Valide que tous les secrets sont correctement configurés.

```bash
./scripts/test-secrets-deployment.sh
```

### `test-traefik-secrets.sh` - Test Traefik
Valide la configuration Traefik avec secrets.

```bash
./scripts/test-traefik-secrets.sh
```

## 🗄️ Bases de Données

### Fichiers SQL d'Initialisation
- `init_stage1.sql` - Initialisation SEL (PostgreSQL)
- `init_stage2.sql` - Ajout Messages/Events (Redis)
- `init_stage3.sql` - Ajout Shop/Education (MinIO)
- `init_stage4.sql` - Version complète avec Analytics

```bash
# Initialisation base de données
docker compose exec postgres psql -U ecolehub ecolehub < scripts/init_stage4.sql
```

## 📋 Pré-requis

### Pour les scripts Python
```bash
pip install psycopg2-binary python-dotenv
```

### Pour les scripts bash
```bash
# Ubuntu/Debian
sudo apt-get install jq curl docker-compose

# Vérifier Docker
docker --version
docker compose version
```

## 🚀 Usage Rapide

### Nouveau déploiement
```bash
# 1. Générer les secrets
./scripts/generate-secrets.sh

# 2. Démarrer les services
./scripts/ecolehub-manager.sh start

# 3. Créer un admin
./scripts/ecolehub-manager.sh users:create admin@votre-ecole.com

# 4. Tester le déploiement
./scripts/test-secrets-deployment.sh
```

### Maintenance quotidienne
```bash
# Status des services
./scripts/ecolehub-manager.sh status

# Lister les utilisateurs
python scripts/ecolehub-cli.py users list

# Sauvegarder
./scripts/ecolehub-manager.sh backup
```

## 🔧 Configuration

Les scripts utilisent automatiquement la configuration de votre fichier `.env`.

Variables importantes :
- `DATABASE_URL` - Connexion PostgreSQL
- `DOMAIN` - Domaine de votre école
- `SECRET_KEY` - Clé de chiffrement

## 📚 Documentation

Voir aussi :
- [secrets-rotation.md](../docs/secrets-rotation.md) - Rotation des secrets
- [Configuration générale](../docs/CONFIGURATION-GUIDE.md)
- [Guide Traefik](../docs/README-TRAEFIK.md)