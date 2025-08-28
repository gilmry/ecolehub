# 🏫 EcoleHub Stage 1 - Système SEL

Plateforme scolaire collaborative avec **Système d'Échange Local (SEL)** pour l'EcoleHub.

**Stage 1** : PostgreSQL + Système SEL pour 30 familles.

## 🆕 Nouveautés Stage 1

### 💱 Système SEL (Échange Local)
- **Services** : Garde enfants, aide devoirs, transport, cuisine...
- **Transactions** : Échange de services entre parents
- **Balances** : Limites belges -300 à +600 unités
- **Catégories** : 9 catégories pré-définies avec emojis

### 🗄️ Base de Données
- **Migration** : SQLite → PostgreSQL 15
- **Performance** : Support 30+ familles
- **UUIDs** : Identifiants sécurisés
- **Contraintes** : Validation données belges

## 🚀 Démarrage Stage 1

### Installation
```bash
# 1. Cloner le projet (si pas déjà fait)
git clone git@github.com:gilmry/ecolehub.git
cd ecolehub

# 2. Configuration Stage 1
cp .env.stage1.example .env

# 3. Lancer Stage 1 avec PostgreSQL
docker-compose -f docker-compose.stage1.yml up -d

# 4. Vérifier le démarrage
curl http://localhost:8000/health

# 5. Accéder à l'application
open http://localhost
```

### Pré-requis
- Docker & Docker Compose
- Port 5432 libre (PostgreSQL)
- Ports 80, 8000 libres

## 📊 Fonctionnalités SEL

### 💼 Services
Parents peuvent proposer des services :

**Categories disponibles :**
- 👶 **Garde** : Garde d'enfants, baby-sitting
- 📚 **Devoirs** : Aide aux devoirs, soutien scolaire  
- 🚗 **Transport** : Transport école, activités
- 🍽️ **Cuisine** : Préparation repas, aide cuisine
- 🔨 **Bricolage** : Petits travaux, réparations
- 🌱 **Jardinage** : Entretien jardin, plantes
- 🧹 **Ménage** : Aide ménagère, nettoyage
- 🛒 **Courses** : Courses et commissions
- 💡 **Autre** : Autres services

### 💰 Balance SEL

**Règles belges :**
- **Balance initiale** : 120 unités (2h de crédit)
- **Limite minimum** : -300 unités
- **Limite maximum** : +600 unités  
- **Standard** : 60 unités = 1 heure

**Exemple :**
- Marie garde Emma (2h) → Jean donne 120 unités à Marie
- Balance Marie : 120 + 120 = 240 unités
- Balance Jean : 120 - 120 = 0 unités

### 🔄 Workflow Transactions

1. **Demande** : Parent A crée une transaction vers Parent B
2. **En attente** : Status "pending", pas de transfert encore
3. **Approbation** : Parent B approuve la transaction
4. **Transfert** : Balances mises à jour automatiquement
5. **Historique** : Transaction visible dans l'historique

## 🔌 API Endpoints Stage 1

### Authentification (conservés Stage 0)
```
POST /register      # Inscription + balance SEL
POST /login         # Connexion
GET  /me           # Profil utilisateur
PUT  /me           # Mise à jour profil
```

### Enfants (conservés Stage 0)
```
GET    /children        # Liste enfants
POST   /children        # Ajouter enfant
DELETE /children/{id}   # Supprimer enfant
```

### SEL Système (nouveaux Stage 1)
```
GET  /sel/categories              # Catégories services
GET  /sel/balance                 # Ma balance SEL
GET  /sel/dashboard               # Dashboard complet

GET  /sel/services                # Services disponibles
GET  /sel/services/mine           # Mes services
POST /sel/services                # Créer service
PUT  /sel/services/{id}           # Modifier service

GET  /sel/transactions            # Mes transactions
POST /sel/transactions            # Créer transaction
PUT  /sel/transactions/{id}/approve  # Approuver transaction
PUT  /sel/transactions/{id}/cancel   # Annuler transaction
```

## 💾 Base de Données PostgreSQL

### Configuration
```env
DATABASE_URL=postgresql://ecolehub:password@postgres:5432/ecolehub
DB_PASSWORD=ecolehub_secure_password
```

### Tables Principales
- **users** : Utilisateurs (UUIDs)
- **children** : Enfants liés aux parents
- **sel_services** : Services proposés
- **sel_transactions** : Échanges entre utilisateurs  
- **sel_balances** : Balances utilisateurs
- **sel_categories** : Catégories de services

### Backup
```bash
# Sauvegarder PostgreSQL
docker-compose -f docker-compose.stage1.yml exec postgres pg_dump -U ecolehub ecolehub > backup-stage1.sql

# Restaurer
docker-compose -f docker-compose.stage1.yml exec postgres psql -U ecolehub ecolehub < backup-stage1.sql
```

## 🧪 Tests de Validation

### Test Manuel Complet
1. **Inscription** : S'inscrire sur http://localhost
2. **Balance** : Vérifier 120 unités initiales
3. **Service** : Créer un service (ex: "Garde après école")
4. **Deuxième utilisateur** : Créer un deuxième compte  
5. **Transaction** : Créer une transaction entre les deux
6. **Approbation** : Approuver la transaction
7. **Balances** : Vérifier les balances mises à jour

### Tests API
```bash
# Health check Stage 1
curl http://localhost:8000/health

# Catégories SEL
curl http://localhost:8000/sel/categories

# Balance (avec token)
curl -H "Authorization: Bearer $TOKEN" http://localhost:8000/sel/balance
```

## 🛠️ Debug et Maintenance

### Logs
```bash
# Logs complets
docker-compose -f docker-compose.stage1.yml logs

# Logs PostgreSQL
docker-compose -f docker-compose.stage1.yml logs postgres

# Logs backend
docker-compose -f docker-compose.stage1.yml logs backend
```

### Base PostgreSQL
```bash
# Accéder à PostgreSQL
docker-compose -f docker-compose.stage1.yml exec postgres psql -U ecolehub ecolehub

# Commandes utiles SQL
\dt                           # Voir tables
SELECT * FROM users;          # Voir utilisateurs
SELECT * FROM sel_balances;   # Voir balances
SELECT * FROM sel_transactions; # Voir transactions
```

## 📈 Métriques Stage 1

### Objectifs
- **Utilisateurs** : 30 familles
- **Transactions SEL** : 50+/mois
- **Uptime** : 98%+
- **Temps réponse** : <300ms

### Capacités
- **PostgreSQL** : Jusqu'à 100+ utilisateurs simultanés
- **Transactions** : Plusieurs par seconde
- **Stockage** : Évolutif selon usage

## 🔮 Roadmap

### Migration depuis Stage 0
- Script automatique SQLite → PostgreSQL
- Préservation données utilisateurs/enfants
- Création balances SEL initiales

### Stage 2 (Futur)
- Messagerie temps réel
- Événements scolaires
- Redis cache + WebSockets
- 60+ familles

---

**Version** : Stage 1 (v1.0.0)  
**Base de données** : PostgreSQL 15  
**Capacité** : 30 familles  
**École** : EcoleHub 🏫