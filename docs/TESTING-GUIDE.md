# 🧪 EcoleHub Testing Guide

Guide complet pour l'exécution et le développement de tests automatisés pour EcoleHub Stage 4.

## 🚀 Démarrage rapide

```bash
# Démarrer l'application
make start

# Installer les dépendances de test
make test-install

# Lancer tous les tests
make test

# Tests spécifiques
make test-unit           # Tests unitaires uniquement
make test-integration    # Tests d'intégration uniquement
make test-auth          # Tests d'authentification
make test-sel           # Tests système SEL
```

## 📁 Structure des tests

```
backend/tests/
├── __init__.py
├── conftest.py                    # Configuration globale et fixtures
├── unit/                          # Tests unitaires (rapides)
│   ├── __init__.py
│   ├── test_auth.py              # Authentification
│   ├── test_sel_system.py        # Système SEL
│   └── test_belgian_context.py   # Contexte scolaire belge
├── integration/                   # Tests d'intégration (avec DB)
│   ├── __init__.py
│   ├── test_api_complete_flows.py # Parcours utilisateur complets
│   └── test_database_operations.py # Opérations base de données
└── test_makefile_integration.py   # Tests d'intégration Makefile
```

## 🧪 Types de tests

### Tests Unitaires (`make test-unit`)
- **Objectif** : Tester des fonctions/classes isolées
- **Vitesse** : Rapide (< 5 secondes)
- **Base de données** : SQLite en mémoire
- **Exemple** : Validation des mots de passe, règles SEL

### Tests d'Intégration (`make test-integration`)
- **Objectif** : Tester l'interaction entre composants
- **Vitesse** : Modéré (< 30 secondes)
- **Base de données** : SQLite avec transactions
- **Exemple** : Parcours complet utilisateur, API + DB

### Tests par Module
- **Auth** (`make test-auth`) : Système d'authentification
- **SEL** (`make test-sel`) : Système d'Échange Local
- **Belgian Context** : Adaptation au système scolaire belge

## 🇧🇪 Tests Contexte Belge

### Système Scolaire
```python
# Classes belges testées
maternelle = ["M1", "M2", "M3"]       # 3-6 ans
primaire = ["P1", "P2", "P3", "P4", "P5", "P6"]  # 6-12 ans, P6 = CEB
```

### Règles SEL Belges
```python
# Limites testées
initial_balance = 120      # 2 heures de crédit initial
minimum_balance = -300     # Maximum débit (5 heures)
maximum_balance = 600      # Maximum crédit (10 heures)
standard_rate = 60         # 60 unités = 1 heure
```

### Langues Supportées
- **fr-BE** : Français (Belgique) - langue principale
- **nl-BE** : Néerlandais (Belgique) - région flamande
- **en** : Anglais - international

## 🔧 Configuration Tests

### Fichiers de Configuration
- **`pytest.ini`** : Configuration principale pytest
- **`requirements.test.txt`** : Dépendances de test
- **`conftest.py`** : Fixtures partagées

### Variables d'Environnement de Test
```bash
TESTING=1                          # Mode test activé
DATABASE_URL=sqlite:///test.db     # Base de test
REDIS_URL=redis://localhost:6379/15 # Redis DB 15 pour tests
SECRET_KEY=test-secret-key         # Clé de test
STAGE=4                           # Stage testé
```

### Fixtures Disponibles
```python
# Utilisateurs de test
test_user_parent    # Parent: parent@test.be / test123
test_user_admin     # Admin: admin@test.be / admin123
test_user_direction # Direction: direction@test.be / direction123

# Données de test
test_child         # Enfant: Emma Dupont, P3
test_sel_service   # Service SEL: Garde après école
belgian_classes    # Classes belges M1-M3, P1-P6
sel_categories     # Catégories SEL adaptées Belgique

# Headers d'authentification
auth_headers_parent     # Headers avec token parent
auth_headers_admin      # Headers avec token admin
auth_headers_direction  # Headers avec token direction
```

## 📊 Couverture de Code

### Objectif de Couverture
- **Minimum** : 80% (requis pour CI)
- **Objectif** : 90% pour modules critiques
- **Critique** : 95% pour authentification et SEL

### Générer Rapport de Couverture
```bash
# Rapport terminal + HTML
make test-coverage

# Rapport HTML détaillé généré dans backend/htmlcov/
open backend/htmlcov/index.html
```

### Zones Critiques à Couvrir
1. **Authentification** : 95%+ requis
2. **Système SEL** : 90%+ requis (transaction, balance)
3. **Gestion utilisateurs** : 85%+ requis
4. **Contexte belge** : 90%+ requis (classes, règles)

## 🚀 CI/CD Pipeline

### GitHub Actions (`.github/workflows/ci.yml`)
```yaml
# Pipeline déclenché sur
- Push vers master/develop
- Pull Request vers master

# Jobs exécutés
1. 🐍 Backend Tests      # Tests Python complets
2. 🔨 Makefile Integration # Tests intégration Makefile
3. 🔒 Security Scan      # Analyse sécurité Bandit/Safety
4. 🐳 Docker Build       # Test construction image
5. 📖 Documentation      # Vérification documentation
```

### Tests Exécutés en CI
- Tests unitaires par catégorie (auth, SEL, contexte belge)
- Tests d'intégration API + DB
- Analyse de couverture de code
- Scan de sécurité des dépendances
- Validation structure Makefile

## 🔍 Développement de Tests

### Ajouter Nouveau Test Unitaire
```python
# backend/tests/unit/test_new_feature.py
import pytest
from app.models.new_feature import NewFeature

@pytest.mark.unit
class TestNewFeature:
    def test_feature_creation(self, db_session):
        """Test creating new feature."""
        feature = NewFeature(name="test")
        db_session.add(feature)
        db_session.commit()
        assert feature.id is not None
```

### Ajouter Test d'Intégration
```python
# backend/tests/integration/test_new_api.py
import pytest
from fastapi.testclient import TestClient

@pytest.mark.integration
class TestNewAPI:
    def test_complete_flow(self, client: TestClient, auth_headers_parent: dict):
        """Test complete API workflow."""
        response = client.post("/new-endpoint", 
                             json={"data": "test"}, 
                             headers=auth_headers_parent)
        assert response.status_code == 201
```

### Marqueurs Pytest Disponibles
```python
@pytest.mark.unit         # Test unitaire rapide
@pytest.mark.integration  # Test d'intégration avec DB
@pytest.mark.auth         # Test authentification
@pytest.mark.sel          # Test système SEL
@pytest.mark.admin        # Test fonctionnalité admin
@pytest.mark.messages     # Test messagerie
@pytest.mark.events       # Test événements
@pytest.mark.shop         # Test boutique
```

## 🐛 Dépannage Tests

### Erreurs Courantes

**❌ "No module named 'app'"**
```bash
# Solution: Exécuter depuis le répertoire backend/
cd backend
python -m pytest tests/
```

**❌ "Database not found"**
```bash
# Solution: Variables d'environnement test non définies
export TESTING=1
export DATABASE_URL=sqlite:///test.db
```

**❌ "Redis connection refused"**
```bash
# Solution: Démarrer Redis pour tests d'intégration
docker run -d -p 6379:6379 redis:7-alpine
# Ou utiliser Redis du docker-compose
make start
```

### Débuggage Tests
```bash
# Mode verbose avec détails
make test ARGS="-v -s"

# Test spécifique avec traceback complet
pytest tests/unit/test_auth.py::TestAuth::test_login -v --tb=long

# Arrêt au premier échec
pytest tests/ -x

# Mode de débogage avec pdb
pytest tests/unit/test_auth.py --pdb
```

## 📈 Métriques et Monitoring

### Tests de Performance
- Temps d'exécution < 30s pour suite complète
- Tests unitaires < 5s
- Tests d'intégration < 25s

### Reporting CI/CD
- Rapport Codecov automatique
- Notifications GitHub sur échec
- Badge de statut dans README

## 🎯 Bonnes Pratiques

### Structure de Test
1. **Arrange** : Préparer les données
2. **Act** : Exécuter l'action
3. **Assert** : Vérifier le résultat

### Nommage des Tests
```python
# Format : test_<what>_<when>_<expected>
def test_user_login_with_valid_credentials_returns_token(self):
def test_sel_balance_with_insufficient_funds_raises_error(self):
def test_belgian_class_with_invalid_level_rejects(self):
```

### Isolation des Tests
- Chaque test est indépendant
- Base de données nettoyée entre tests
- Fixtures pour données cohérentes

---

## 📞 Support

**Problèmes de tests** : Créer une issue GitHub avec :
- Commande make utilisée
- Message d'erreur complet
- Environnement (Docker/local)

**Contribuer** : Voir `CONTRIBUTING.md` pour guidelines de développement

---

**Version** : Stage 4 (v4.0.0)  
**Dernière mise à jour** : 2025-01-16  
**Coverage Objective** : 85%+ 🎯