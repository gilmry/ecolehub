# 🏫 EcoleHub

[![CI](https://github.com/gilmry/ecolehub/actions/workflows/ci.yml/badge.svg?branch=master)](https://github.com/gilmry/ecolehub/actions/workflows/ci.yml)
[![Coverage](https://codecov.io/gh/gilmry/ecolehub/branch/master/graph/badge.svg)](https://app.codecov.io/gh/gilmry/ecolehub)
[![A11Y](https://img.shields.io/badge/a11y-STRICT-green)](#-accessibilite)

Plateforme scolaire collaborative open-source pour écoles primaires.

**Version complète** : Système SEL + Messagerie + Boutique + Éducation + Analytics + Multilingue.

## 🚀 Installation Rapide (5 minutes)

### Pré-requis
- Docker & Docker Compose
- Git

### Démarrage
```bash
# 1. Cloner le projet
git clone https://github.com/gilmry/ecolehub.git
cd ecolehub

# 2. Configuration
cp .env.example .env
# Modifier .env avec votre domaine et mots de passe

# 3. Lancer avec Traefik (recommandé)
docker compose -f docker-compose.traefik.yml up -d

# 4. Vérifier que tout fonctionne
curl https://votre-domaine.com/health

# 5. Accéder à votre instance
open https://votre-domaine.com
```

## 📖 Documentation

- **[CHANGELOG.md](./CHANGELOG.md)** - Historique des versions
- **[CONFIGURATION-GUIDE.md](./docs/CONFIGURATION-GUIDE.md)** - Configuration générale
- **[README-TRAEFIK.md](./docs/README-TRAEFIK.md)** - Déploiement avec Traefik
- **[TESTING-GUIDE.md](./docs/TESTING-GUIDE.md)** - Tests automatisés
- **[Comptes de démo](./docs/DEMO-ACCOUNTS.example.md)** - Template des comptes de test
- **[TODO / Roadmap](./docs/TODO.md)** - Prochaines tâches et priorités

## 🎯 Administration

```bash
# Gestion des services
docker compose -f docker-compose.traefik.yml logs -f
docker compose -f docker-compose.traefik.yml ps
docker compose -f docker-compose.traefik.yml down

# Tests (si configuré)
make test           # Tests d'intégration
make test-unit      # Tests unitaires

## ♿ Accessibilité

La CI exécute des audits d’accessibilité stricts:
- Pa11y (WCAG2AA) sur le frontend servi localement (rapport JSON en artefact)
- Playwright + axe-core pour un test a11y de bout en bout (rapport HTML en artefact)

En local:
```bash
make ci-local  # lance un audit Pa11y STRICT après les tests
```

# Sauvegarde base de données
docker compose exec postgres pg_dump -U ecolehub ecolehub > backup.sql
```

## ✅ Fonctionnalités

### 🏠 Base
- ✅ **Inscription/Connexion** avec email + mot de passe
- ✅ **Profil utilisateur** + enfants avec classes belges (M1-M3, P1-P6)
- ✅ **Système SEL** : Échanges entre parents (-300/+600 unités)
- ✅ **Services** : 10 catégories + propositions communautaires

### 💬 Communication
- ✅ **Messages directs** : Parent-à-parent temps réel
- ✅ **Événements école** : Inscriptions + calendrier
- ✅ **Conversations groupe** : Par classe automatique

### 🛒 Boutique Collaborative
- ✅ **Achat groupé** : Commandes déclenchées par seuils
- ✅ **Catalogue produits** : Fournitures scolaires + uniformes
- ✅ **Expressions d'intérêt** : Quantités + notes (taille, couleur)
- ✅ **Paiements belges** : Mollie (Bancontact, SEPA, cartes)

### 📚 Ressources Éducatives
- ✅ **Bibliothèque ressources** : Documents, formulaires, calendriers
- ✅ **Contenu par classe** : M1-M3, P1-P6
- ✅ **Stockage sécurisé** : MinIO S3 avec validation
- ✅ **Contrôle d'accès** : Public et restreint parents

### ⚙️ Administration
- ✅ **Interface admin** : Gestion produits + commandes
- ✅ **Authentification rôles** : Admin/direction par email
- ✅ **Dashboard statistiques** : Usage plateforme
- ✅ **Monitoring** : Prometheus + Grafana

### 🌍 Multilingue
- ✅ **3 langues** : Français (BE), Néerlandais (BE), Anglais
- ✅ **Contexte belge** : Classes, monnaie, culture
- ✅ **Analytics** : Métriques détaillées d'usage

## 🔍 API Endpoints

Tous les endpoints API sont préfixés par `/api`:

```
GET  /api/me         # Profil utilisateur
POST /api/login      # Connexion
POST /api/register   # Inscription
GET  /api/children   # Liste enfants
GET  /api/sel/categories # Catégories SEL
GET  /health         # Status application
GET  /metrics        # Métriques Prometheus
```

## 🐛 Debugging

### Logs
```bash
# Voir les logs backend
docker compose -f docker-compose.traefik.yml logs backend

# Voir les logs Traefik
docker compose -f docker-compose.traefik.yml logs traefik

# Suivre les logs en temps réel
docker compose -f docker-compose.traefik.yml logs -f
```

### Base de Données
```bash
# Accéder à PostgreSQL
docker compose exec postgres psql -U ecolehub ecolehub

# Voir les tables
\dt

# Voir les utilisateurs
SELECT email, first_name, last_name FROM users;
```

### Tests Manuels
```bash
# Test santé API
curl https://votre-domaine.com/health

# Test connexion (avec les comptes de démo)
curl -X POST https://votre-domaine.com/api/login \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  -d 'email=admin@ecolehub.be&password=VOTRE_MOT_DE_PASSE'
```

## 🏗️ Architecture

- **Backend** : FastAPI + PostgreSQL + Redis
- **Frontend** : Vue.js 3 + Tailwind CSS
- **Proxy** : Traefik v3 avec Let's Encrypt
- **Stockage** : MinIO S3 compatible
- **Monitoring** : Prometheus + Grafana
- **Async** : Celery + Redis

## 📊 Performance

### Objectifs Production
- **Utilisateurs** : 200+ familles
- **Uptime** : 99.9%+
- **Temps réponse** : <100ms
- **Transactions SEL** : 1000+/mois
- **Commandes groupées** : 50+/mois

## 🤝 Contribution

Contributions bienvenues ! Voir [TESTING-GUIDE.md](./docs/TESTING-GUIDE.md) pour les tests.

## 📄 Licence

MIT - Libre d'usage pour toute école.

---

🏫 **EcoleHub** - Par des parents, pour des parents. Made in Belgium 🇧🇪
