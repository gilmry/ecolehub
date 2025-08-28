# 🏫 EcoleHub Stage 2 - Messages + Événements

Plateforme scolaire collaborative avec **messagerie temps réel** et **système d'événements** pour l'EcoleHub.

**Stage 2** : Messages + Événements + Redis pour 60 familles.

## 🆕 Nouveautés Stage 2

### 💬 Messagerie Temps Réel
- **Messages directs** : Parent-à-parent avec conversations privées
- **Groupes classe** : Conversations automatiques par classe (M1-M3, P1-P6)  
- **Annonces école** : Communication officielle EcoleHub
- **Auto-refresh** : Messages mis à jour toutes les 3 secondes
- **Interface chat** : Bulles messages, timestamps, auto-scroll

### 📅 Événements EcoleHub
- **Spaghetti de Saint-Nicolas** : Tradition de l'école (6 décembre)
- **Fancy Fair** : Grande fête annuelle avec stands et spectacles
- **Carnaval** : Défilé costumes et concours
- **Classes vertes P6** : Séjour Ardennes belges
- **Réunions CEB** : Préparation Certificat d'Études de Base

### 🔴 Infrastructure Redis
- **Cache temps réel** : Sessions et données fréquentes
- **WebSocket ready** : Infrastructure pour fonctionnalités futures
- **Performance** : Support 60+ familles simultanées

## 🚀 Migration vers Stage 2

### Depuis Stage 1
```bash
# Arrêt Stage 1
docker-compose -f docker-compose.stage1.yml down

# Lancement Stage 2  
cp .env.stage2.example .env
docker-compose -f docker-compose.stage2.yml up -d

# Vérification
curl http://localhost:8000/health
```

### Pré-requis
- Docker & Docker Compose
- Ports 5432, 6379, 8000, 80 libres
- Données Stage 1 préservées

## 📱 Interface Stage 2

### Navigation (6 onglets)
1. **🏠 Dashboard** - Balance SEL + Services disponibles
2. **💼 Services SEL** - Créer services + propositions (Stage 1)
3. **💱 Transactions** - Workflow SEL (Stage 1)
4. **💬 Messages** - Conversations temps réel ✨ **NOUVEAU**
5. **📅 Événements** - École + Classes ✨ **NOUVEAU**
6. **👤 Profil** - Enfants + données

### Messages Parent-à-Parent

**2 façons d'envoyer un message :**

#### 1. Onglet Messages
- **"✉️ Nouveau message"** → Sélectionner parent → Envoyer
- **Conversations existantes** → Cliquer pour ouvrir chat
- **Auto-refresh** : Nouveaux messages toutes les 3 secondes

#### 2. Depuis Services SEL
- **Service intéressant** → **"💬 Message"** 
- **Contexte automatique** : "À propos de votre service..."
- **Redirection** vers onglet Messages

### Événements École

**Types d'événements :**
- 🏫 **École** : Réunions, rentrée, CEB
- 📚 **Classes** : Sorties, activités spécifiques
- 🎉 **Fêtes** : Saint-Nicolas, Fancy Fair, Carnaval

**Fonctionnalités :**
- **Inscription** avec limites de places
- **Filtres** par type d'événement
- **Calendrier** belge avec dates spécifiques EcoleHub

## 🔌 API Stage 2

### Héritées Stage 1
```
# Authentification
POST /register, /login
GET /me, PUT /me

# Enfants  
GET /children, POST /children, DELETE /children/{id}

# SEL
GET /sel/categories, /sel/balance, /sel/services
POST /sel/services, /sel/transactions
PUT /sel/transactions/{id}/approve
```

### Nouvelles Stage 2
```
# Messaging
GET /conversations                    # Mes conversations
GET /conversations/{id}/messages      # Messages d'une conversation
POST /conversations/direct           # Créer conversation directe
POST /conversations/{id}/messages    # Envoyer message
GET /users/list                     # Liste parents (pour messaging)

# Events
GET /events                         # Événements école
POST /events/{id}/register          # S'inscrire à un événement

# WebSocket (futur)
WS /ws                             # Temps réel (infrastructure)
```

## 💾 Infrastructure Stage 2

### Services Docker
- **PostgreSQL 15** : Base principale avec UUIDs
- **Redis 7** : Cache + sessions temps réel
- **Backend Stage 2** : FastAPI avec messaging + events
- **Frontend** : Interface 6 onglets
- **Nginx** : Proxy avec support WebSocket

### Configuration
```env
# Base données
DATABASE_URL=postgresql://ecolehub:password@postgres:5432/ecolehub
DB_PASSWORD=ecolehub_secure_password

# Redis
REDIS_URL=redis://:redis_password@redis:6379/0
REDIS_PASSWORD=redis_secure_password

# Sécurité
SECRET_KEY=your-very-long-secret-key

# Stage
STAGE=2
```

### Ports
- **Frontend** : http://localhost (port 80)
- **API** : http://localhost:8000
- **PostgreSQL** : localhost:5432
- **Redis** : localhost:6379

## 🧪 Tests de Validation

### Test Messages Parent-Parent
1. **Navigateur 1** : S'inscrire comme Marie
2. **Navigateur 2 (privé)** : S'inscrire comme Jean  
3. **Marie** → Messages → Nouveau message → Jean
4. **Jean** voit le message en 3 secondes max
5. **Jean** répond → Marie voit la réponse

### Test Événements École
1. **Onglet Événements** → Voir événements EcoleHub
2. **"Spaghetti de Saint-Nicolas"** → S'inscrire
3. **Filtre "Fêtes"** → Voir Fancy Fair + Carnaval
4. **Vérifier limites** : Places disponibles/maximum

### Test Groupes Classe
1. **Ajouter enfant** en classe P3
2. **Onglet Messages** → Voir "Classe P3" automatiquement
3. **Conversation classe** pour communication parents P3

## 🇧🇪 Spécificités EcoleHub

### Événements Traditionnels
- **🍝 Spaghetti de Saint-Nicolas** : 6 décembre (120 places)
- **🎪 Fancy Fair** : Mai (300 personnes max)
- **🎭 Carnaval** : Février/mars (déguisements)
- **📚 Réunions CEB** : Préparation P6

### Communications
- **Annonces école** : Canal officiel administration
- **Groupes classe** : M1, M2, M3, P1, P2, P3, P4, P5, P6
- **Messages privés** : Coordination services SEL

## 📈 Métriques Stage 2

### Objectifs
- **Utilisateurs** : 60 familles
- **Messages** : 100+/jour
- **Événements** : 10+/mois
- **Uptime** : 99%+
- **Temps réponse** : <200ms

### Capacités
- **Redis** : Cache haute performance
- **PostgreSQL** : Milliers de messages
- **Polling** : 3 secondes latence max
- **Events** : Centaines d'inscriptions

## 🔮 Roadmap

### Stage 3 (Futur)
- Boutique collaborative avec commandes groupées
- Module éducatif (devoirs, notes)
- Intégration Printful + Mollie
- MinIO stockage fichiers
- 100+ familles

---

**Version** : Stage 2 (v2.0.0)  
**Infrastructure** : PostgreSQL + Redis  
**Capacité** : 60 familles  
**École** : EcoleHub 🏫  
**Spécialité** : Spaghetti de Saint-Nicolas ! 🍝