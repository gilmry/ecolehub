# Règles de Développement EcoleHub

## Principes Généraux

### 1. Simplicité Absolue
- Toujours choisir la solution la plus simple
- Si tu hésites entre 2 approches, prends la plus directe
- Pas de patterns complexes si pas nécessaire
- Un fichier qui fait tout > 10 fichiers "bien organisés" pour Stage 0

### 2. Production-Ready Dès le Début
- Chaque ligne de code doit être déployable
- Gestion d'erreur basique mais présente
- HTTPS obligatoire même en développement
- Logs essentiels seulement

### 3. Approche Progressive
- Ne JAMAIS implémenter plusieurs stages en même temps
- Stage actuel doit être parfait avant le suivant
- Migrations entre stages sans perte de données
- Backward compatibility maintenue

## Règles Techniques

### Backend (FastAPI)
```python
# ✅ BON - Tout en 1 fichier pour Stage 0
from fastapi import FastAPI, Depends, HTTPException
# ... tout le code dans main.py

# ❌ MAUVAIS - Structure complexe pour Stage 0
# from app.services.user_service import UserService
# from app.repositories.user_repository import UserRepository
```

### Frontend (Vue 3)
```html
<!-- ✅ BON - CDN pour Stage 0 -->
<script src="https://unpkg.com/vue@3/dist/vue.global.js"></script>

<!-- ❌ MAUVAIS - Build process Stage 0 -->
<script type="module" src="/src/main.js"></script>
```

### Base de Données
```python
# ✅ BON - SQLite Stage 0
DATABASE_URL = "sqlite:///./schoolhub.db"

# ❌ MAUVAIS - PostgreSQL Stage 0  
DATABASE_URL = "postgresql://user:pass@localhost/db"
```

## Règles de Sécurité

### Authentification
- JWT avec expiration (7 jours max)
- Mots de passe hashés avec bcrypt
- CORS configuré correctement
- Pas de secrets en dur dans le code

### RGPD/Privacy
- Données minimales collectées
- Consentement explicite
- Possibilité de suppression compte
- Logs sans données personnelles

## Conventions de Code

### Nommage
- **Classes Python**: PascalCase (`User`, `SELTransaction`)
- **Fonctions/variables**: snake_case (`get_user`, `user_id`)
- **Endpoints API**: kebab-case (`/api/v1/user-profile`)
- **Variables env**: UPPER_SNAKE_CASE (`DATABASE_URL`)

### Structure des Commits
```
type(scope): description

feat(auth): add JWT token validation
fix(sel): correct balance calculation limits
docs(readme): update deployment instructions
```

### Classes Belges (Validation)
```python
VALID_CLASSES = ['M1', 'M2', 'M3', 'P1', 'P2', 'P3', 'P4', 'P5', 'P6']
```

## Gestion d'Erreurs

### API Responses
```python
# ✅ BON
@app.post("/register")
def register(user: UserCreate):
    try:
        # logic
        return {"message": "Utilisateur créé"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

# ❌ MAUVAIS - Trop complexe Stage 0
# Custom exception classes, error handlers, etc.
```

### Frontend Error Handling
```javascript
// ✅ BON
try {
    const response = await fetch('/api/register', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(userData)
    });
    if (!response.ok) {
        throw new Error('Erreur inscription');
    }
} catch (error) {
    alert(error.message); // Simple pour Stage 0
}
```

## Performance Guidelines

### Stage 0 (SQLite)
- Pas d'optimisation prématurée
- Index seulement si problème de performance
- Requêtes directes, pas de cache

### Stage 1+ (PostgreSQL)
- Index sur foreign keys
- Connection pooling
- Cache Redis pour sessions

## Testing Strategy

### Stage 0
- Tests manuels uniquement
- Checklist de validation
- Test sur mobile

### Stage 1+
- Tests unitaires essentiels
- Tests d'intégration API
- Tests end-to-end critiques

## Déploiement

### Variables d'Environnement
```bash
# Obligatoires toujours
SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///./schoolhub.db

# Stage 1+
DB_PASSWORD=secure-password
REDIS_PASSWORD=secure-redis-password

# Stage 3+
MOLLIE_API_KEY=mollie-key
PRINTFUL_API_KEY=printful-key
```

### Docker
- Images Alpine Linux (plus légères)
- Multi-stage builds pour production
- Health checks obligatoires
- Logs structurés

## Anti-Patterns à Éviter

### ❌ Sur-ingénierie
```python
# Pas pour Stage 0
class UserServiceFactory:
    def create_user_service(self, db_type: str):
        # ...
```

### ❌ Prématuré
```python
# Pas besoin Stage 0
async def get_user_with_cache(user_id: int):
    # Redis cache logic
```

### ❌ Complexité inutile
```javascript
// Stage 0 - Simple suffit
const state = reactive({
    user: null,
    isAuthenticated: false
});

// Pas besoin de Pinia/Vuex Stage 0
```

## Validation Avant Commit

1. Code fonctionne en local
2. Docker Compose démarre sans erreur
3. Flow utilisateur complet testé
4. Responsive OK sur mobile
5. Pas de secrets committes
6. README à jour

## Métriques de Qualité

### Stage 0
- Temps de démarrage < 30 secondes
- Interface responsive
- 0 erreur JavaScript console
- SSL configuré

### Performance Targets
| Stage | Users | Response Time | Uptime |
|-------|-------|---------------|--------|
| 0     | 5-10  | <500ms        | 95%    |
| 1     | 30    | <300ms        | 98%    |
| 2     | 60    | <200ms        | 99%    |