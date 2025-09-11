# 🧪 EcoleHub Backend Tests

Suite de tests automatisés pour EcoleHub Stage 4 - Plateforme scolaire collaborative belge.

## 🚀 Exécution rapide

```bash
# Depuis la racine du projet
make test                # Tous les tests
make test-unit           # Tests unitaires uniquement
make test-integration    # Tests d'intégration uniquement
make test-coverage       # Avec rapport de couverture
```

## 📁 Structure

```
tests/
├── conftest.py                    # Configuration et fixtures communes
├── unit/                          # Tests unitaires (rapides)
│   ├── test_auth.py              # Tests d'authentification
│   ├── test_sel_system.py        # Tests système SEL
│   └── test_belgian_context.py   # Tests contexte scolaire belge
├── integration/                   # Tests d'intégration
│   ├── test_api_complete_flows.py # Parcours utilisateur complets
│   └── test_database_operations.py # Tests base de données
└── test_makefile_integration.py   # Tests intégration Makefile
```

## 🇧🇪 Spécificités Belges Testées

### Système Scolaire
- **Classes maternelles** : M1, M2, M3 (3-6 ans)
- **Classes primaires** : P1, P2, P3, P4, P5, P6 (6-12 ans)
- **CEB** : Certificat d'Études de Base en P6

### Système SEL (Échange Local)
- **Balance initiale** : 120 unités (2h de crédit)
- **Limite minimale** : -300 unités (5h de dette max)
- **Limite maximale** : +600 unités (10h de crédit max)
- **Taux standard** : 60 unités = 1 heure

### Langues Supportées
- **fr-BE** : Français belge (langue principale)
- **nl-BE** : Néerlandais belge (Flandre)
- **en** : Anglais (international)

## 📊 Couverture de Code

**Objectif** : 85%+ de couverture globale

**Zones critiques** (90%+ requis) :
- Authentification et sécurité
- Système SEL (transactions, balances)
- Gestion des enfants et classes belges
- API endpoints principaux

## 🧪 Types de Tests

### Tests Unitaires (`unit/`)
- **Objectif** : Fonctions isolées
- **Vitesse** : < 5 secondes
- **Base** : SQLite en mémoire
- **Exemple** : Validation password, règles SEL

### Tests d'Intégration (`integration/`)
- **Objectif** : Interaction composants
- **Vitesse** : < 30 secondes  
- **Base** : SQLite avec transactions
- **Exemple** : Parcours utilisateur complet

## 🔧 Fixtures Disponibles

### Utilisateurs de Test
```python
test_user_parent     # parent@test.be / test123
test_user_admin      # admin@test.be / admin123
test_user_direction  # direction@test.be / direction123
```

### Données Belges
```python
belgian_classes      # ['M1', 'M2', 'M3', 'P1', 'P2', 'P3', 'P4', 'P5', 'P6']
sel_categories       # Catégories SEL adaptées au contexte belge
test_child           # Enfant test : Emma Dupont, P3
test_sel_service     # Service SEL : Garde après école
```

### Client API
```python
client               # TestClient FastAPI
auth_headers_parent  # Headers avec token parent
auth_headers_admin   # Headers avec token admin
```

## 🏷️ Marqueurs pytest

```python
@pytest.mark.unit         # Test unitaire rapide
@pytest.mark.integration  # Test d'intégration avec DB
@pytest.mark.auth         # Test authentification
@pytest.mark.sel          # Test système SEL
@pytest.mark.belgian      # Test contexte belge
```

## 🐛 Dépannage

### Erreurs courantes

**"No module named 'app'"**
```bash
# Solution : Exécuter depuis backend/
cd backend && python -m pytest tests/
```

**"Database not found"**
```bash
# Solution : Variables d'environnement
export TESTING=1
export DATABASE_URL=sqlite:///test.db
```

**"Redis connection refused"**
```bash
# Solution : Démarrer Redis
make start  # ou docker run -d -p 6379:6379 redis:7-alpine
```

## 📈 CI/CD

Les tests sont automatiquement exécutés sur GitHub Actions :
- Push vers `master` ou `develop`
- Pull requests vers `master`
- Rapport de couverture Codecov
- Scan de sécurité Bandit/Safety

## 💡 Développer de Nouveaux Tests

### Template Test Unitaire
```python
# tests/unit/test_new_feature.py
import pytest
from app.models.new_feature import NewFeature

@pytest.mark.unit
class TestNewFeature:
    def test_create_feature_with_valid_data_success(self, db_session):
        """Test creating feature with valid data succeeds."""
        # Arrange
        feature_data = {"name": "test", "value": 123}
        
        # Act
        feature = NewFeature(**feature_data)
        db_session.add(feature)
        db_session.commit()
        
        # Assert
        assert feature.id is not None
        assert feature.name == "test"
```

### Template Test d'Intégration
```python
# tests/integration/test_new_api.py
import pytest
from fastapi.testclient import TestClient

@pytest.mark.integration
class TestNewAPI:
    def test_complete_workflow_success(self, client: TestClient, auth_headers_parent: dict):
        """Test complete API workflow succeeds."""
        # Arrange
        data = {"field": "value"}
        
        # Act
        response = client.post("/api/new-endpoint", 
                             json=data, 
                             headers=auth_headers_parent)
        
        # Assert
        assert response.status_code == 201
        result = response.json()
        assert result["field"] == "value"
```

---

**Pour plus de détails** : Voir [TESTING-GUIDE.md](../../TESTING-GUIDE.md)