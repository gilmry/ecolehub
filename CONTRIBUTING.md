# 🤝 Contributing to EcoleHub / Guide de Contribution à EcoleHub

> **English**: Thank you for your interest in contributing to EcoleHub! This project provides a progressive, open-source collaborative platform for Belgian schools, designed to scale from small schools (5 families) to large ones (200+ families) while maintaining GDPR compliance and accessibility standards.

**Français** : Merci de votre intérêt pour contribuer à EcoleHub ! Ce projet vise à fournir une plateforme collaborative open source pour les écoles belges, avec une approche progressive et modulaire.

## 🎯 Vision du Projet

EcoleHub est conçu pour :
- Être **réutilisable par toutes les écoles** (de 5 à 200+ familles)
- Respecter le **système éducatif belge** (M1-M3, P1-P6, CEB)
- Maintenir une **approche budget-consciente** (VPS abordable)
- Suivre une **architecture progressive** en 5 stages

## 🏫 Qui Peut Contribuer

### Écoles & Équipes Pédagogiques
- **Directeurs/Directrices** : Retours sur fonctionnalités, besoins spécifiques
- **Enseignants** : Tests utilisateur, suggestions d'amélioration
- **Secrétaires** : Feedback sur les workflows administratifs
- **Parents tech-savvy** : Tests, documentation, traductions

### Développeurs & Tech
- **Développeurs Python/FastAPI** : Backend, API, tests
- **Développeurs Frontend** : Vue.js, UX/UI, accessibilité
- **DevOps** : Docker, CI/CD, déploiement
- **Designers** : UX/UI adaptée au milieu éducatif

### Experts Métier
- **Juristes RGPD** : Conformité data protection
- **Traducteurs** : Français ↔ Néerlandais ↔ Anglais
- **Accessibility experts** : WCAG, inclusivité

## 🚀 Comment Commencer

### 1. 📋 Premiers Pas
```bash
# Cloner le projet
git clone https://github.com/gilmry/ecolehub.git
cd ecolehub

# Configuration rapide
cp .env.example .env
# Éditer .env avec vos paramètres

# Démarrage (production-ready)
docker compose -f docker-compose.traefik.yml up -d
```

### 2. 🧪 Tests et Développement
```bash
# Tests complets
make ci-local

# Tests spécifiques
cd backend
pytest tests/unit/        # Tests unitaires
pytest tests/integration/ # Tests d'intégration
pytest tests/gdpr/        # Tests RGPD
```

### 3. 📁 Structure du Projet
```
schoolhub/
├── backend/              # FastAPI Stage 4 complet
│   ├── app/
│   │   ├── main_stage4.py
│   │   ├── models_stage*.py
│   │   └── *_service.py
│   └── tests/           # Tests complets
├── frontend/            # Vue.js SPA
├── .github/             # Workflows CI/CD
└── docker-compose.traefik.yml  # Production
```

## 📝 Types de Contributions

### 🐛 Signaler un Bug
- Utilisez notre [template d'issue](https://github.com/gilmry/ecolehub/issues/new?template=bug_report.md)
- **Anonymisez les données** d'école/enfant dans vos exemples
- Précisez votre contexte (taille école, stage utilisé)

### ✨ Proposer une Fonctionnalité
- Consultez d'abord les [issues existantes](https://github.com/gilmry/ecolehub/issues)
- Créez une [feature request](https://github.com/gilmry/ecolehub/issues/new?template=feature_request.md)
- Décrivez le **cas d'usage éducatif** concret

### 🏫 Feedback d'École
- Partagez votre expérience d'utilisation
- Proposez des améliorations workflow
- Signalez les besoins spécifiques au système belge

### 🔧 Contribuer du Code

#### Standards de Qualité
- **Tests** : Couverture > 80%, tous les tests passent
- **Linting** : flake8 sans erreur
- **RGPD** : Conformité stricte pour données enfants
- **Accessibilité** : WCAG 2.0 AA minimum
- **Documentation** : Code self-documenting

#### Workflow Git
1. **Fork** le repository
2. **Branch** depuis master : `git checkout -b feature/nom-fonctionnalite`
3. **Commit** avec messages clairs (voir format ci-dessous)
4. **Tests** : `make ci-local` doit passer
5. **Pull Request** avec notre template

#### Format des Commits
```
type(scope): description courte

Corps du message détaillant les changements.
Respecter la convention Conventional Commits.

Types: feat, fix, docs, style, refactor, test, chore
Scopes: auth, sel, messages, events, shop, admin, ci, etc.
```

### 🌍 Traductions & i18n
- Fichiers dans `frontend/locales/`
- Priorités : **fr-BE** > **nl-BE** > **en**
- Respecter la terminologie éducative belge

## 🔒 Sécurité & RGPD

### Impératifs Absolus
- **Jamais de vraies données** d'école dans les commits
- **Anonymisation** systématique des exemples
- **Chiffrement** des données sensibles
- **Tests RGPD** obligatoires pour nouvelles fonctionnalités

### Données Sensibles Interdites
- Noms/prénoms réels d'enfants
- Emails réels de parents
- Adresses d'écoles
- Photos d'enfants
- Numéros de téléphone

## 🏗 Architecture & Stages

EcoleHub suit une approche **progressive** :

| Stage | Cible | Tech | Infrastructure |
|-------|-------|------|----------------|
| **0** | 5-10 familles | SQLite + Vue CDN | Serveur simple |
| **1** | ~30 familles | PostgreSQL + SEL | Docker |
| **2** | ~60 familles | +Redis + WebSockets | Docker Compose |
| **3** | ~100 familles | +MinIO + Stripe | VPS 10€ |
| **4** | 200+ familles | +Monitoring + i18n | K8s ready |

### Principes de Développement
1. **Simplicité d'abord** - Solution la plus simple qui fonctionne
2. **Pas de dette technique** - Code propre dès le début
3. **Production-ready** - Chaque stage doit fonctionner en production
4. **Migrations préservées** - Jamais casser le chemin de mise à jour

## 🤝 Processus de Review

### Pour les Mainteneurs
- **Délai** : Response sous 48h en semaine
- **Tests** : CI doit passer (linting + tests + sécurité + accessibilité)
- **RGPD** : Review spécifique pour données sensibles
- **Pédagogie** : Validation que ça marche pour les écoles

### Pour les Contributeurs
- **Patience** : Reviews approfondies pour la qualité
- **Feedback** : Intégrer les retours constructivement
- **Tests** : Ajouter tests pour nouvelles fonctionnalités

## 📞 Communication

### Canaux
- **Issues GitHub** : Bugs, features, discussions
- **Discussions** : Questions générales, aide
- **Email** : contact@ecolehub.be (sujets sensibles)

### Règles
- **Français** prioritaire (public belge)
- **Bienveillance** dans tous les échanges
- **Transparence** sauf pour sécurité/données sensibles

## 🎉 Reconnaissance

Les contributeurs sont mis en valeur dans :
- `CONTRIBUTORS.md` (mainteneurs réguliers)
- Release notes des versions
- Documentation de remerciements

## 📄 Licence

En contribuant, vous acceptez que vos contributions soient sous licence **MIT**, permettant la réutilisation libre par toutes les écoles.

---

## 🙏 Merci !

Chaque contribution, petite ou grande, aide les écoles belges à avoir accès à une plateforme collaborative de qualité. Ensemble, construisons l'école numérique de demain ! 🏫✨

---

**Questions ?** N'hésitez pas à ouvrir une [issue](https://github.com/gilmry/ecolehub/issues) ou nous contacter à contact@ecolehub.be