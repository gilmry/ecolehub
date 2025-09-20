# 🎭 EcoleHub E2E Tests & Video Documentation

Infrastructure de tests end-to-end et génération automatique de documentation vidéo pour EcoleHub Stage 4.

## 🚀 Démarrage rapide

```bash
# Installation des dépendances E2E
make test-e2e-install

# Lancer tous les tests E2E
make test-e2e

# Générer la documentation vidéo
make generate-docs
```

## 📁 Structure

```
e2e/
├── README.md                    # Ce fichier
├── fixtures/
│   └── test-data.ts            # Données de test (utilisateurs, classes belges, SEL)
├── pages/                      # Page Object Model
│   ├── login-page.ts           # Page de connexion
│   ├── dashboard-page.ts       # Tableau de bord principal
│   └── sel-services-page.ts    # Services SEL
├── utils/
│   └── base-page.ts            # Utilitaires de base pour tous les tests
├── auth.spec.ts                # Tests d'authentification
├── sel-system.spec.ts          # Tests système SEL
├── navigation.spec.ts          # Tests de navigation
├── belgian-context.spec.ts     # Tests contexte scolaire belge
└── documentation-flow.spec.ts  # Tests pour génération vidéo
```

## 🧪 Types de tests

### Tests d'authentification (`auth.spec.ts`)
- Connexion/déconnexion parents, admin, direction
- Gestion des erreurs d'authentification
- Validation des sessions

### Tests du système SEL (`sel-system.spec.ts`)
- Affichage des soldes SEL
- Création et demande de services
- Navigation dans les différents onglets

### Tests de navigation (`navigation.spec.ts`)
- Navigation entre toutes les sections
- Changement de langue (fr-BE, nl-BE, en)
- Interface responsive mobile/desktop
- Fonctionnalités spécifiques admin

### Tests contexte belge (`belgian-context.spec.ts`)
- Interface française par défaut
- Validation des classes belges (M1-M3, P1-P6)
- Règles SEL belges (120 unités initiales, limites)
- Localisation franco-belge

### Documentation vidéo (`documentation-flow.spec.ts`)
- Parcours utilisateur complet
- Démonstration toutes fonctionnalités
- Génération de vidéos pour documentation

## 🎬 Génération de documentation vidéo

### Scripts disponibles

```bash
# Génération complète avec script automatisé
./scripts/generate-video-docs.sh

# Commandes make disponibles
make generate-docs              # Script complet
make test-e2e-video-docs       # Tests documentation uniquement
```

### Configuration vidéo

Les vidéos sont configurées via `playwright-video-docs.config.ts` :
- Résolution optimisée : 1280x720
- Enregistrement forcé : `video: 'on'`
- Captures d'écran : `screenshot: 'on'`
- Exécution séquentielle pour cohérence

### Fichiers générés

```
test-results/
├── videos/                     # Vidéos des tests (.webm)
├── screenshots/                # Captures d'écran (.png)
└── traces/                     # Traces Playwright (.zip)

docs/videos/                    # Vidéos de documentation
```

## 🎭 Commandes Playwright

### Tests de base
```bash
# Tests standard
npm test
npm run test:headed            # Mode visible
npm run test:debug             # Mode débogage

# Tests mobiles
npm run test:mobile

# Interface utilisateur
npm run test:ui

# Génération documentation
npm run test:video-docs
```

### Tests via Makefile
```bash
# Installation
make test-e2e-install

# Exécution
make test-e2e                  # Tests complets
make test-e2e-mobile          # Tests mobiles
make test-e2e-ui              # Mode UI interactif
make test-e2e-headed          # Navigateur visible
make test-e2e-debug           # Mode débogage

# Documentation
make test-e2e-video-docs      # Génération vidéos
make generate-docs            # Script complet
```

## 🔧 Configuration

### Fichiers de configuration

- `playwright.config.ts` : Configuration principale
- `playwright-video-docs.config.ts` : Configuration pour documentation
- `package.json` : Scripts npm et dépendances

### Variables d'environnement

```bash
BASE_URL=http://localhost:8000  # URL de l'application
STAGE=4                         # Stage EcoleHub
TESTING=1                       # Mode test
```

### Données de test

Les utilisateurs de test sont définis dans `fixtures/test-data.ts` :

```typescript
// Utilisateurs de test
parent@test.be / test123        # Parent : Marie Dupont
admin@test.be / admin123        # Admin : Admin System
direction@test.be / direction123 # Direction : Jean Direction

// Classes belges testées
M1, M2, M3                      # Maternelle (3-6 ans)
P1, P2, P3, P4, P5, P6         # Primaire (6-12 ans), P6 = CEB

// Système SEL belge
120 unités initiales            # 2 heures de crédit
-300 / +600 unités limites     # 5h débit / 10h crédit max
60 unités = 1 heure            # Taux standard
```

## 🚀 CI/CD Integration

### GitHub Actions

Les tests E2E sont intégrés dans `.github/workflows/e2e-tests.yml` :

```yaml
# Jobs disponibles
e2e-tests:           # Tests E2E standard
video-documentation: # Génération documentation vidéo
mobile-tests:        # Tests mobiles spécifiques
```

### Déclencheurs

- **Push** : branches `master`, `develop`
- **Pull Request** : vers `master`
- **Manuel** : avec option génération vidéo

### Artefacts générés

- `playwright-report` : Rapport HTML (7 jours)
- `playwright-videos` : Vidéos des tests (7 jours)
- `ecolehub-video-documentation` : Vidéos documentation (30 jours)

## 📊 Rapports et analyse

### Visualisation des résultats

```bash
# Rapport HTML interactif
npm run test:report

# Serveur local (après tests)
npx playwright show-report --host=0.0.0.0 --port=9323
```

### Analyse des échecs

Les tests génèrent automatiquement :
- **Vidéos** : Enregistrement complet des échecs
- **Screenshots** : Capture au moment de l'échec
- **Traces** : Debugging interactif complet

## 🛠️ Développement

### Ajouter nouveaux tests

1. **Créer page object** dans `pages/`
2. **Définir données test** dans `fixtures/test-data.ts`
3. **Écrire spec** dans `e2e/nom-feature.spec.ts`
4. **Tester localement** avec `make test-e2e-headed`

### Structure d'un test

```typescript
import { test, expect } from '@playwright/test';
import { LoginPage } from './pages/login-page';
import { TestUsers } from './fixtures/test-data';

test.describe('Ma fonctionnalité', () => {
  test.beforeEach(async ({ page }) => {
    const loginPage = new LoginPage(page);
    await page.goto('/');
    await loginPage.loginAsParent();
  });

  test('devrait faire quelque chose', async ({ page }) => {
    // Test implementation
    await page.takeScreenshot({ path: 'screenshot.png' });
  });
});
```

### Page Object Model

```typescript
export class MaPage extends BasePage {
  readonly element: Locator;

  constructor(page: Page) {
    super(page);
    this.element = page.locator('#mon-element');
  }

  async faireAction() {
    await this.element.click();
    await this.waitForLoadingToFinish();
  }
}
```

## 🔧 Dépannage

### Erreurs courantes

**❌ "Application not ready"**
```bash
# Vérifier que l'application démarre
docker compose -f docker-compose.traefik.yml up -d
curl http://localhost:8000/health
```

**❌ "Browser not found"**
```bash
# Réinstaller les navigateurs
npx playwright install --with-deps
```

**❌ "Test timeout"**
```bash
# Augmenter le timeout dans playwright.config.ts
timeout: 60000  # 60 secondes
```

### Mode debugging

```bash
# Mode pas-à-pas avec interface
make test-e2e-debug

# Traces interactives
npx playwright show-trace test-results/trace.zip
```

## 📈 Métriques

### Performance attendue

- **Tests complets** : ~5-10 minutes
- **Tests mobiles** : ~3-5 minutes
- **Documentation vidéo** : ~10-15 minutes
- **Taille vidéos** : ~10-50 MB par test

### Couverture fonctionnelle

- ✅ Authentification (100%)
- ✅ Navigation principale (100%)
- ✅ Système SEL (85%)
- ✅ Contexte belge (90%)
- ✅ Interface mobile (80%)

## 🤝 Contribution

1. **Tests locaux** : `make test-e2e-headed`
2. **Documentation** : Mettre à jour ce README
3. **Nouvelles pages** : Suivre le pattern Page Object Model
4. **CI/CD** : Vérifier passage dans GitHub Actions

---

**Version** : Stage 4 (v4.0.0)
**Framework** : Playwright + TypeScript
**Documentation** : Vidéos automatiques
**Maintenance** : Tests CI/CD intégrés 🎭