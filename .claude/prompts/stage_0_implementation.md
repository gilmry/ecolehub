# Prompt Stage 0 - Implémentation Minimale

## FOCUS ABSOLU: Stage 0 uniquement

Tu dois implémenter SEULEMENT le Stage 0 d'EcoleHub. Ne pas penser aux stages suivants.

### Objectif Stage 0
Créer une plateforme fonctionnelle pour 5-10 familles avec:
- Inscription/Connexion
- Profil utilisateur  
- Gestion enfants/classes
- Déployable en production

### Stack Technique Stage 0
**Backend:**
- FastAPI minimal (1 fichier main.py suffit)
- SQLite (PAS de PostgreSQL)
- JWT pour l'auth
- Bcrypt pour les mots de passe
- CORS configuré

**Frontend:**
- HTML simple + Vue 3 CDN
- Tailwind CDN
- LocalStorage pour token
- Fetch API (pas d'axios)

**Infrastructure:**
- Docker Compose simple
- Nginx pour servir le frontend
- Certificats SSL (Let's Encrypt)

### Structure de fichiers EXACTE

```
backend/
├── app/
│   ├── main.py          # Tout le backend en 1 fichier
│   └── schoolhub.db     # SQLite database
├── requirements.txt     # 5-8 packages max
└── Dockerfile

frontend/
└── index.html          # Tout le frontend en 1 fichier

docker-compose.yml      # 2 services: backend + frontend
.env.example           # Variables d'environnement
README.md              # Instructions en 5 étapes max
```

### Modèles de données (SQLite)

```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email VARCHAR(255) UNIQUE NOT NULL,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    is_active BOOLEAN DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE children (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    parent_id INTEGER REFERENCES users(id),
    first_name VARCHAR(100) NOT NULL,
    class_name VARCHAR(10) CHECK (class_name IN ('M1','M2','M3','P1','P2','P3','P4','P5','P6')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Endpoints API Stage 0

```
POST /register      # Inscription
POST /login         # Connexion
GET /me             # Profil utilisateur
PUT /me             # Mise à jour profil
GET /children       # Liste enfants
POST /children      # Ajouter enfant
DELETE /children/{id} # Supprimer enfant
GET /health         # Health check
```

### Fonctionnalités Frontend

1. **Page de connexion/inscription**
   - Formulaire avec email/mot de passe
   - Bouton pour basculer inscription/connexion
   - Validation côté client

2. **Dashboard après connexion**
   - Profil utilisateur (nom, email)
   - Liste des enfants avec classes
   - Formulaire ajout enfant
   - Bouton déconnexion

3. **Gestion d'état simple**
   - Token JWT en localStorage
   - État auth dans Vue data()
   - Pas de Pinia/Vuex au Stage 0

### Contraintes STRICTES Stage 0

**Ce qu'on VEUT:**
- Code simple et lisible
- Fonctionne en 5 minutes
- Déployable immédiatement
- Pas de bugs critiques

**Ce qu'on NE VEUT PAS:**
- Architecture complexe
- Services/repositories
- Tests unitaires (pour l'instant)
- TypeScript
- Build process complexe
- Async/await si pas nécessaire
- ORM complexe
- Migrations de DB
- Redis, Celery, WebSockets
- Modules npm

### Commandes de déploiement

```bash
# Installation
git clone repo
cd schoolhub
cp .env.example .env

# Lancement
docker-compose up -d

# Test
curl http://localhost/health
# Ouvrir http://localhost
```

### Critères de succès Stage 0

- [ ] Inscription d'un utilisateur fonctionne
- [ ] Connexion fonctionne
- [ ] Ajout d'un enfant fonctionne  
- [ ] Interface responsive (mobile OK)
- [ ] Déployable sur VPS en 10 minutes
- [ ] Code < 500 lignes total
- [ ] README clair pour déploiement

### Validation de l'implémentation

Avant de considérer Stage 0 terminé:
1. Tester le flow complet manuellement
2. Vérifier que ça marche sur mobile
3. Déployer sur un VPS de test
4. Faire tester par 2-3 personnes

**IMPORTANT**: Stage 0 doit être 100% fonctionnel avant de penser au Stage 1.