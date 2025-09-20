# 🔄 Pull Request EcoleHub

## 📋 Résumé

<!-- Description claire et concise des changements -->

### Type de Changement
- [ ] 🐛 **Bug fix** (correction d'un problème existant)
- [ ] ✨ **Feature** (nouvelle fonctionnalité)
- [ ] 💄 **UI/UX** (améliorations interface utilisateur)
- [ ] ♿ **Accessibility** (amélioration accessibilité)
- [ ] 🔒 **Security** (correctif de sécurité)
- [ ] 📚 **Documentation** (mise à jour docs)
- [ ] 🔧 **Chore** (maintenance, dépendances, etc.)
- [ ] 🎨 **Refactor** (restructuration code sans changement fonctionnel)

## 🎯 Contexte & Motivation

### Problème Résolu
<!-- Quel problème cette PR résout-elle ? -->
- Référence issue : Fixes #[numéro]

### Cas d'Usage École
<!-- Comment cela améliore l'expérience des écoles ? -->

## 🔧 Changements Techniques

### Fichiers Modifiés
<!-- Liste des principaux fichiers modifiés et pourquoi -->

### Architecture
- [ ] Backend (FastAPI)
- [ ] Frontend (Vue.js)
- [ ] Base de données (migrations)
- [ ] Infrastructure (Docker, CI/CD)
- [ ] Tests

### APIs Impactées
<!-- Nouvelles routes, modifications d'endpoints existants -->

## 🧪 Tests

### Tests Ajoutés/Modifiés
- [ ] Tests unitaires
- [ ] Tests d'intégration
- [ ] Tests RGPD/conformité
- [ ] Tests accessibilité
- [ ] Tests de performance

### Commandes de Test
```bash
# Comment tester ces changements
make ci-local
# ou
pytest tests/...
```

### Cas de Test Manuels
<!-- Si tests manuels nécessaires, décrire les étapes -->

## 🔒 Sécurité & RGPD

### Données Traitées
Cette PR implique-t-elle :
- [ ] Données d'enfants
- [ ] Informations personnelles parents
- [ ] Données financières (SEL/boutique)
- [ ] Messages/communications privées
- [ ] Aucune donnée sensible

### Conformité
- [ ] ✅ Respecte les principes RGPD
- [ ] ✅ Anonymisation/pseudonymisation si nécessaire
- [ ] ✅ Chiffrement données sensibles
- [ ] ✅ Logs ne contiennent pas de données personnelles
- [ ] ✅ Consentement géré correctement

### Review Sécurité
- [ ] Code review sécurité effectué
- [ ] Scan automatique (Bandit/Safety) passé
- [ ] Pas de secrets hardcodés

## ♿ Accessibilité

- [ ] ✅ Éléments HTML sémantiques
- [ ] ✅ Labels appropriés sur les formulaires
- [ ] ✅ Contraste couleurs suffisant
- [ ] ✅ Navigation clavier possible
- [ ] ✅ Compatible lecteurs d'écran
- [ ] ✅ Tests pa11y/axe-core passés

## 🌍 Internationalisation

- [ ] Textes externalisés (locales/)
- [ ] Traductions FR disponibles
- [ ] Traductions NL si applicable
- [ ] Format dates/nombres belge
- [ ] Compatible UTF-8

## 📱 Compatibilité

### Navigateurs Testés
- [ ] Chrome/Chromium
- [ ] Firefox
- [ ] Safari
- [ ] Edge

### Appareils
- [ ] Desktop
- [ ] Mobile
- [ ] Tablette

### Stages EcoleHub
Cette PR est compatible avec :
- [ ] Stage 0 (SQLite, 5-10 familles)
- [ ] Stage 1 (PostgreSQL, 30 familles)
- [ ] Stage 2 (Redis, 60 familles)
- [ ] Stage 3 (MinIO, 100 familles)
- [ ] Stage 4 (Complet, 200+ familles)

## 📸 Captures d'Écran

### Avant
<!-- Si changement UI, montrer l'état avant -->

### Après
<!-- Montrer les changements apportés -->
<!-- ⚠️ ANONYMISER les données d'exemple -->

## 🚀 Déploiement

### Migrations Nécessaires
- [ ] Migration base de données
- [ ] Changement configuration
- [ ] Mise à jour dépendances
- [ ] Redémarrage services requis

### Instructions Déploiement
<!-- Étapes spéciales pour déployer ces changements -->

### Rollback Plan
<!-- Comment annuler ces changements si problème -->

## ✅ Checklist Pre-Merge

### Code Quality
- [ ] ✅ CI/CD passe (linting, tests, sécurité, accessibilité)
- [ ] ✅ Code self-documenting ou commenté
- [ ] ✅ Pas de console.log ou prints de debug
- [ ] ✅ Gestion d'erreur appropriée
- [ ] ✅ Performance acceptable

### Documentation
- [ ] ✅ README mis à jour si nécessaire
- [ ] ✅ CHANGELOG.md mis à jour
- [ ] ✅ Documentation API si nouveaux endpoints
- [ ] ✅ Guide d'installation mis à jour si nécessaire

### Review
- [ ] ✅ Self-review effectué
- [ ] ✅ Code conforme aux standards du projet
- [ ] ✅ Approuvé par au moins 1 maintainer
- [ ] ✅ Tous les commentaires de review adressés

## 🔗 Références

### Issues Liées
- Closes #[numéro]
- Related to #[numéro]

### Documentation
- [Lien vers doc pertinente]

### Discussions
- [Lien vers discussion GitHub]

---

## 📝 Notes pour les Reviewers

<!-- Informations spécifiques pour faciliter la review -->

### Points d'Attention
<!-- Zones du code nécessitant attention particulière -->

### Questions Ouvertes
<!-- Points sur lesquels vous souhaitez l'avis des reviewers -->

---

**Merci pour votre contribution à EcoleHub ! 🏫✨**

En soumettant cette PR, je confirme que :
- [ ] Je respecte le [Code de Conduite](../CODE_OF_CONDUCT.md)
- [ ] J'ai lu le [Guide de Contribution](../CONTRIBUTING.md)
- [ ] Cette contribution peut être utilisée sous licence MIT
- [ ] J'ai anonymisé toutes les données d'exemple