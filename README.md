# 🏫 EcoleHub - Stage 4

Plateforme scolaire collaborative pour l'EcoleHub (Bruxelles).

**Stage Actuel** : Boutique collaborative + Éducation + Administration + Multilingue + Analytics.

## 🚀 Installation Rapide (5 minutes)

### Pré-requis
- Docker & Docker Compose
- Git

### Démarrage Stage 4
```bash
# 1. Cloner le projet
git clone git@github.com:gilmry/ecolehub.git
cd ecolehub

# 2. Lancer Stage 4 (Nouvelle méthode recommandée avec Makefile)
cp .env.stage4.example .env
make start

# Alternative: méthode Docker Compose directe
docker-compose -f docker-compose.stage4.yml up -d

# 3. Vérifier que tout fonctionne
make health

# 4. Voir toutes les URLs disponibles
make urls

# 5. Ouvrir dans le navigateur
open http://localhost
```

### ⭐ Nouveau: Makefile + Tests Automatisés

Le projet dispose maintenant d'un **Makefile complet** et d'une **suite de tests automatisés**:

```bash
# Gestion de l'application
make help           # Voir toutes les commandes disponibles
make start          # Démarrer l'application complète
make stop           # Arrêter tous les services
make status         # Voir le statut des services

# Gestion des utilisateurs
make users-list     # Lister tous les utilisateurs
make accounts       # Voir les comptes de test

# Tests automatisés (nouveau!)
make test           # Lancer tous les tests
make test-unit      # Tests unitaires rapides
make test-coverage  # Rapport de couverture

# Monitoring
make logs           # Voir les logs en temps réel
make health         # Vérifier la santé du backend
make backup         # Créer une sauvegarde
```

📖 **Guides disponibles**:
- [MAKEFILE-GUIDE.md](./MAKEFILE-GUIDE.md) - Commandes centralisées
- [TESTING-GUIDE.md](./TESTING-GUIDE.md) - Tests automatisés

**C'est tout !** 🎉

📖 **Guides détaillés** : [INSTALL.md](INSTALL.md) • [Stage 1](README-STAGE1.md) • [Stage 3](README-STAGE2.md)

## ✅ Fonctionnalités Stage 4

### 🏠 Base (Stages 0+1+2)
- ✅ **Inscription/Connexion** avec email + mot de passe
- ✅ **Profil utilisateur** + enfants avec classes belges
- ✅ **Système SEL** : Échanges entre parents (-300/+600 unités)
- ✅ **Services** : 10 catégories + propositions communautaires
- ✅ **Messages directs** : Parent-à-parent temps réel
- ✅ **Événements école** : Inscriptions + calendrier

### 🛒 Boutique Collaborative (Stage 4)
- ✅ **Achat groupé** : Commandes déclenchées par seuils
- ✅ **Catalogue produits** : Fournitures scolaires + uniformes
- ✅ **Expressions d'intérêt** : Quantités + notes (taille, couleur)
- ✅ **Paiements belges** : Mollie (Bancontact, SEPA, cartes)
- ✅ **Gestion commandes** : Workflow complet

### 📚 Ressources Éducatives (Stage 4)
- ✅ **Bibliothèque ressources** : Documents, formulaires, calendriers
- ✅ **Contenu par classe** : M1-M3, P1-P6
- ✅ **Stockage sécurisé** : MinIO S3 avec validation
- ✅ **Contrôle d'accès** : Public et restreint parents
- ✅ **Catégories** : Devoirs, calendriers, annonces

### ⚙️ Administration (Stage 4)
- ✅ **Interface admin** : Gestion produits + commandes
- ✅ **Authentification rôles** : Admin/direction par email
- ✅ **Dashboard statistiques** : Usage plateforme
- ✅ **Gestion seuils** : Lancement commandes groupées

### 🌍 Multilingue + Analytics (Stage 4)
- ✅ **3 langues** : Français, Néerlandais, Anglais
- ✅ **Contexte belge** : Localisations spécifiques
- ✅ **Analytics** : Métriques usage et performance
- ✅ **Monitoring** : Prometheus + Grafana

## 🏗️ Architecture Stage 4

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   Frontend  │    │   Nginx     │    │   Backend   │    │ PostgreSQL  │
│ Vue 3 PWA   │───▶│ Proxy + SSL │───▶│  FastAPI    │───▶│  Database   │
│ 9 onglets   │    │             │    │ Full Stack  │    │             │
│Multilingue  │    │             │    │             │    │             │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
                                              │
               ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
               │    Redis    │    │   MinIO     │    │   Celery    │
               │   Cache     │    │ Storage S3  │    │  Workers    │
               │             │    │             │    │             │
               └─────────────┘    └─────────────┘    └─────────────┘
```

### Stack Technique Stage 4
- **Backend** : FastAPI + PostgreSQL + Redis + MinIO + Celery
- **Frontend** : Vue 3 PWA responsive avec 9 onglets + i18n
- **Paiements** : Mollie (Bancontact, SEPA, PayPal)
- **Stockage** : MinIO S3 pour fichiers + images
- **Queue** : Celery pour tâches asynchrones
- **Monitoring** : Prometheus + Grafana
- **Déploiement** : Docker Compose 6+ services

## 🇧🇪 Spécificités Belges

### Classes Supportées
- **Maternelle** : M1, M2, M3
- **Primaire** : P1, P2, P3, P4, P5, P6

### RGPD Compliant
- Données minimales collectées
- Consentement explicite
- Droit à la suppression

## 📋 Guide d'Utilisation

### Premier Démarrage
1. Ouvrir http://localhost
2. Cliquer "S'inscrire"
3. Remplir le formulaire (email, prénom, nom, mot de passe)
4. Ajouter vos enfants avec leurs classes

### Fonctionnalités
- **Profil** : Modifier prénom/nom
- **Enfants** : Ajouter/supprimer enfants
- **Classes** : Sélection automatique M1-M3, P1-P6

## 🔧 Configuration

### Variables d'Environnement (.env)
```bash
# OBLIGATOIRE - Changer en production
SECRET_KEY=your-very-long-secret-key-here

# Base de données (SQLite par défaut)
DATABASE_URL=sqlite:///./schoolhub.db
```

### Ports
- **Frontend** : http://localhost (port 80)
- **Backend API** : http://localhost:8000
- **HTTPS** : port 443 (si configuré)

## 🌐 Déploiement Production

### VPS avec Docker
```bash
# Sur votre serveur
git clone <votre-repo>
cd schoolhub

# Configuration sécurisée
cp .env.example .env
nano .env  # Modifier SECRET_KEY

# Lancer en production
docker-compose up -d

# Vérifier le statut
curl http://votre-ip/health
```

### SSL avec Let's Encrypt
```bash
# Installer certbot
apt install certbot

# Obtenir certificat
certbot certonly --standalone -d votre-domaine.com

# Modifier nginx.conf (décommenter section HTTPS)
# Relancer
docker-compose restart frontend
```

## 🔍 API Endpoints

```
GET  /              # Page d'accueil API
POST /register      # Inscription utilisateur  
POST /login         # Connexion
GET  /me            # Profil utilisateur
PUT  /me            # Mise à jour profil
GET  /children      # Liste enfants
POST /children      # Ajouter enfant
DELETE /children/{id} # Supprimer enfant
GET  /health        # Status application
```

## 🐛 Debugging

### Logs
```bash
# Voir les logs backend
docker-compose logs backend

# Voir les logs nginx
docker-compose logs frontend

# Suivre les logs en temps réel
docker-compose logs -f
```

### Base de Données
```bash
# Accéder à SQLite
docker-compose exec backend sqlite3 schoolhub.db

# Voir les tables
.tables

# Voir les utilisateurs
SELECT * FROM users;
```

### Tests Manuels
```bash
# Test santé API
curl http://localhost:8000/health

# Test inscription
curl -X POST http://localhost:8000/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"test123","first_name":"Test","last_name":"User"}'
```

## 📊 Métriques Stage 4

### Objectifs Production
- **Utilisateurs** : 200+ familles
- **Uptime** : 99.9%+
- **Temps réponse** : <100ms
- **Transactions SEL** : 1000+/mois
- **Commandes groupées** : 50+/mois

### Validation Stage 4
- ✅ Interface 9 onglets complète
- ✅ Système paiements belges Mollie
- ✅ Stockage MinIO opérationnel
- ✅ Analytics + monitoring actifs
- ✅ Support multilingue FR/NL/EN

## 🔮 Évolution par Stages

### Stage 1 - Système SEL
```bash
# Migration Stage 0 → Stage 1
./migrate.sh
```
- **SEL complet** : Échanges entre parents
- **PostgreSQL** : Base évolutive (30 familles)
- **Documentation** : [README-STAGE1.md](README-STAGE1.md)

### Stage 4 - Full Stack ✨ **ACTUEL**
```bash
# Migration Stage 3 → Stage 4
cp .env.stage4.example .env
docker-compose -f docker-compose.stage4.yml up -d
```
- **🛒 Boutique** : Achat groupé + paiements belges
- **📚 Éducation** : Ressources par classe + stockage
- **⚙️ Administration** : Interface admin complète
- **🌍 Multilingue** : FR/NL/EN + analytics
- **📊 Monitoring** : Prometheus + Grafana (200+ familles)

### Évolution Future
- **Optimisations** : Performance + sécurité
- **Intégrations** : APIs externes belges
- **Mobile** : Application native (optionnel)

## 🆘 Support

### Problèmes Courants

**Port 80 occupé**
```bash
# Changer le port dans docker-compose.yml
ports:
  - "8080:80"  # Au lieu de "80:80"
```

**Erreur de base de données**
```bash
# Supprimer la DB et recommencer
rm backend/app/schoolhub.db
docker-compose restart backend
```

**Interface ne charge pas**
```bash
# Vérifier les logs
docker-compose logs frontend
# Souvent un problème de cache navigateur (Ctrl+F5)
```

### Contact
- **Technique** : Voir les issues GitHub
- **École** : Contact administration EcoleHub

## 📝 Licence

MIT License - Voir [LICENSE](LICENSE) pour les détails.

Open Source - Réutilisable par d'autres écoles.

---

**Version** : Stage 4 (v4.0.0)  
**Dernière mise à jour** : 2024-08-28  
**École** : EcoleHub, Bruxelles 🇧🇪