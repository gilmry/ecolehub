# 🏫 EcoleHub - Stage 2

Plateforme scolaire collaborative pour l'EcoleHub (Bruxelles).

**Stage Actuel** : Messagerie temps réel + Événements école + Système SEL complet.

## 🚀 Installation Rapide (5 minutes)

### Pré-requis
- Docker & Docker Compose
- Git

### Démarrage Stage 2
```bash
# 1. Cloner le projet
git clone git@github.com:gilmry/ecolehub.git
cd ecolehub

# 2. Lancer Stage 2 (Messaging + Events)
cp .env.stage2.example .env
docker-compose -f docker-compose.stage2.yml up -d

# 3. Ouvrir dans le navigateur
open http://localhost
```

**C'est tout !** 🎉

📖 **Guides détaillés** : [INSTALL.md](INSTALL.md) • [Stage 1](README-STAGE1.md) • [Stage 2](README-STAGE2.md)

## ✅ Fonctionnalités Stage 2

### 🏠 Base (Stages 0+1)
- ✅ **Inscription/Connexion** avec email + mot de passe
- ✅ **Profil utilisateur** + enfants avec classes belges
- ✅ **Système SEL** : Échanges entre parents (-300/+600 unités)
- ✅ **Services** : 10 catégories + propositions communautaires

### 💬 Messages (Stage 2)
- ✅ **Messages directs** : Parent-à-parent avec auto-refresh 3s
- ✅ **Groupes classe** : M1, M2, M3, P1, P2, P3, P4, P5, P6
- ✅ **Annonces école** : Canal officiel EcoleHub
- ✅ **Interface chat** : Bulles, timestamps, auto-scroll

### 📅 Événements École (Stage 2)
- ✅ **🍝 Spaghetti Saint-Nicolas** : Tradition EcoleHub (6 décembre)
- ✅ **Fancy Fair** : Fête annuelle + stands + spectacles
- ✅ **Carnaval** : Déguisements + concours costumes
- ✅ **Classes vertes P6** : Séjour Ardennes belges
- ✅ **Inscriptions** : Avec limites + deadlines

## 🏗️ Architecture Stage 2

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   Frontend  │    │   Nginx     │    │   Backend   │    │ PostgreSQL  │
│   Vue 3     │───▶│ Proxy + WS  │───▶│ FastAPI+SEL │───▶│   + Redis   │
│  6 onglets  │    │             │    │ +Messaging  │    │             │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
```

### Stack Technique Stage 2
- **Backend** : FastAPI + PostgreSQL + Redis + WebSockets
- **Frontend** : Vue 3 responsive avec 6 onglets
- **Cache** : Redis pour sessions + temps réel
- **Messagerie** : Polling 3s + conversations persistantes
- **Déploiement** : Docker Compose 4 services

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

## 📊 Métriques Stage 0

### Objectifs
- **Utilisateurs** : 5-10 familles
- **Uptime** : 95%+
- **Temps réponse** : <500ms
- **Mobile** : Interface responsive

### Validation Avant Stage 1
- [ ] 5+ familles utilisent l'application
- [ ] Authentification fonctionne sans bug
- [ ] Interface mobile correcte
- [ ] SSL configuré en production
- [ ] Backup SQLite fonctionnel

## 🔮 Évolution par Stages

### Stage 1 - Système SEL
```bash
# Migration Stage 0 → Stage 1
./migrate.sh
```
- **SEL complet** : Échanges entre parents
- **PostgreSQL** : Base évolutive (30 familles)
- **Documentation** : [README-STAGE1.md](README-STAGE1.md)

### Stage 2 - Messages + Événements ✨ **ACTUEL**
```bash
# Migration Stage 1 → Stage 2
cp .env.stage2.example .env
docker-compose -f docker-compose.stage2.yml up -d
```
- **💬 Messagerie** : Parent-à-parent temps réel
- **📅 Événements** : École + Spaghetti Saint-Nicolas
- **🔴 Redis** : Cache + performance (60 familles)
- **Documentation** : [README-STAGE2.md](README-STAGE2.md)

### Stages Suivants (Planifiés)
- **Stage 3** : Boutique collaborative + Éducation
- **Stage 4** : Multilingual + Analytics + Admin

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

**Version** : Stage 0 (v0.1.0)  
**Dernière mise à jour** : $(date +%Y-%m-%d)  
**École** : EcoleHub, Bruxelles 🇧🇪