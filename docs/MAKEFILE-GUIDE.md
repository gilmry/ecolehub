# 🏫 EcoleHub Makefile Guide

Le Makefile centralise toutes les commandes de gestion du projet EcoleHub Stage 4.

## 🚀 Démarrage rapide

```bash
# Afficher l'aide
make help

# Démarrer l'application
make start

# Voir le statut des services
make status

# Arrêter l'application
make stop
```

## 📋 Commandes principales

### Gestion des services
```bash
make start          # Démarrer tous les services
make stop           # Arrêter tous les services  
make restart        # Redémarrer tous les services
make status         # Afficher le statut des services
```

### Informations utiles
```bash
make urls           # Afficher toutes les URLs des services
make accounts       # Afficher les comptes de test
make version        # Informations de version
make health         # Vérifier la santé du backend
```

## 👥 Gestion des utilisateurs

```bash
make users-list     # Lister tous les utilisateurs
make users-create   # Créer un utilisateur (interactif)
make users-reset    # Réinitialiser un mot de passe (interactif)
```

## 🔐 Gestion des credentials

```bash
make creds-show     # Afficher tous les credentials
make creds-generate # Générer de nouveaux credentials sécurisés
```

## 📋 Logs et monitoring

```bash
make logs           # Voir tous les logs
make logs-backend   # Logs du backend uniquement
make logs-frontend  # Logs du frontend uniquement
make logs-traefik   # Logs de Traefik uniquement
```

## 🛠️ Développement

```bash
make dev            # Mode développement
make test           # Lancer les tests
make test-all       # i18n-lint (STRICT) puis tests
make ci-local       # CI local (i18n STRICT + tests + flake8)
make a11y-audit     # Audit accessibilité (pa11y, BASE_URL configurable)
make a11y-serve-frontend   # Sert le frontend localement (par défaut : 8089)
make a11y-audit-frontend   # Sert temporairement puis lance l'audit a11y
make ci-local       # i18n-lint STRICT + tests + flake8 en local
make lint           # Vérifier le code
make format         # Formater le code
make shell-backend  # Shell dans le container backend
make shell-db       # Shell dans la base de données
```

## 🐳 Gestion Docker

```bash
make build          # Construire/reconstruire les services
make pull           # Télécharger les dernières images
make clean          # Nettoyer les conteneurs et volumes
```

## 💾 Sauvegarde et restauration

```bash
make backup         # Créer une sauvegarde complète
make restore        # Restaurer depuis une sauvegarde (interactif)
```

## 🔧 Gestion des services individuels

```bash
make restart-backend    # Redémarrer le backend uniquement
make restart-frontend   # Redémarrer le frontend uniquement
make restart-traefik    # Redémarrer Traefik uniquement
make restart-db         # Redémarrer la base de données
```

## 🐛 Dépannage

```bash
make debug              # Informations de débogage
make fix-permissions    # Corriger les permissions des fichiers
```

## 🧹 Maintenance

```bash
make reset          # Réinitialiser complètement (DANGEREUX)
make update         # Mettre à jour et redémarrer les services
```

## 📊 URLs des services

Une fois l'application démarrée avec `make start`:

- **Frontend**: http://localhost/
- **API Backend**: http://localhost/api/
- **Santé API**: http://localhost/api/health
- **Grafana**: http://localhost:3001/
- **Traefik Dashboard**: http://localhost:8080/
- **Prometheus**: http://localhost:9090/
- **MinIO Console**: http://localhost:9001/

## 👤 Comptes de test

Utilisez ces comptes pour tester l'application:

- **Admin**: admin@ecolehub.be / admin123
- **Direction**: direction@ecolehub.be / direction123
- **Parent**: demo@example.com / demo123
- **Enseignant**: teacher@ecolehub.be / teacher123

## 💡 Exemples d'utilisation

### Démarrage complet
```bash
# Démarrer l'application
make start

# Vérifier que tout fonctionne
make health
make urls

# Voir les comptes disponibles
make accounts
```

### Développement
```bash
# Mode développement
make dev

# Voir les logs en temps réel
make logs

# Lancer les tests
make test
```

### Gestion des utilisateurs
```bash
# Lister tous les utilisateurs
make users-list

# Créer un nouvel utilisateur
make users-create

# Réinitialiser un mot de passe
make users-reset
```

### Maintenance
```bash
# Créer une sauvegarde
make backup

# Voir les informations de débogage
make debug

# Nettoyer les ressources Docker
make clean
```

## ⚠️ Commandes importantes

- `make reset` supprime TOUTES les données (confirmation requise)
- `make clean` supprime les conteneurs et volumes Docker
- `make backup` crée une sauvegarde de la base de données
- Toujours utiliser `make stop` avant `make clean`

## 📖 Intégration avec les outils existants

Le Makefile utilise les outils existants:
- CLI EcoleHub: `./ecolehub`
- Docker Compose: `docker-compose.stage4.yml`
- Scripts de gestion: `scripts/`

Tous les outils restent utilisables indépendamment du Makefile.
