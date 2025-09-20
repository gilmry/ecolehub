# 🔒 Politique de Sécurité EcoleHub

## 🛡️ Versions Supportées

EcoleHub suit une politique de support des versions alignée sur les besoins des écoles :

| Version | Supportée | Fin de Support | Notes |
| ------- | --------- | -------------- | ----- |
| 4.x.x   | ✅ Oui    | TBD            | Version actuelle (Stage 4) |
| 3.x.x   | ✅ Oui    | Juin 2026      | Support étendu pour écoles en production |
| 2.x.x   | ⚠️ Sécurité uniquement | Janvier 2026 | Correctifs critiques seulement |
| 1.x.x   | ❌ Non    | Septembre 2025 | Migration recommandée |
| < 1.0   | ❌ Non    | -              | Versions de développement |

## 🚨 Signaler une Vulnérabilité

### 🔴 Vulnérabilités Critiques (Action Immédiate)
Pour les problèmes de sécurité critiques affectant les données d'enfants ou la sécurité des écoles :

**📧 Email sécurisé** : security@ecolehub.be
- Chiffrement PGP recommandé
- Réponse sous **24h maximum**
- Patch d'urgence sous **72h**

### 🟡 Vulnérabilités Non-Critiques
**GitHub Security Advisory** : [Signaler de manière privée](https://github.com/gilmry/ecolehub/security/advisories)
- Réponse sous **5 jours ouvrés**
- Évaluation et plan de correction

### ⚪ Questions de Sécurité Générales
**Discussions GitHub** : Onglet [Discussions](https://github.com/gilmry/ecolehub/discussions)
- Pour questions non-sensibles
- Bonnes pratiques de déploiement

## 🎯 Périmètre de Sécurité

### 🔒 Données Critiques Protégées
- **Données d'identification des enfants** (noms, classes, photos)
- **Informations familiales** (emails, téléphones, adresses)
- **Données financières** (transactions SEL, boutique)
- **Messages privés** entre parents/enseignants
- **Données d'authentification** (mots de passe, tokens)

### 🏫 Contexte Scolaire Spécifique
- **RGPD renforcé** : Protection des mineurs
- **Loi belge** : Conformité réglementaire éducation
- **Confidentialité** : Séparation entre écoles
- **Intégrité pédagogique** : Pas d'accès non autorisé aux données de classe

## ⚡ Classification des Vulnérabilités

### 🔴 **CRITIQUE** (Patch < 24h)
- Accès non autorisé aux données d'enfants
- Escalade de privilèges vers données sensibles
- Injection SQL touchant données personnelles
- Fuite de données RGPD (emails, noms, etc.)
- Bypass d'authentification
- Exécution de code arbitraire côté serveur

### 🟠 **HAUTE** (Patch < 1 semaine)
- Déni de service affectant le fonctionnement école
- Cross-Site Scripting (XSS) persistant
- Cross-Site Request Forgery (CSRF)
- Fuite d'informations système
- Bypass des contrôles d'accès non-critique

### 🟡 **MOYENNE** (Patch < 1 mois)
- XSS non-persistant
- Fuite d'informations mineures
- Vulnérabilités dans dépendances (non-critique)
- Problèmes de configuration

### 🔵 **BASSE** (Patch dans release suivante)
- Problèmes d'interface utilisateur
- Améliorations de sécurité préventives
- Durcissement de configuration

## 🔐 Mesures de Sécurité Actuelles

### Architecture
- **Chiffrement** : HTTPS obligatoire, TLS 1.3
- **Base de données** : Chiffrement au repos
- **Secrets** : Docker secrets / variables d'environnement
- **Sessions** : JWT avec expiration courte
- **CORS** : Configuration restrictive

### Code
- **Validation** : Pydantic pour tous les inputs
- **ORM** : SQLAlchemy (protection injection SQL)
- **Hash** : bcrypt/pbkdf2 pour mots de passe
- **Logs** : Pas de données sensibles dans les logs

### Infrastructure
- **Conteneurs** : Images Docker minimales
- **Réseau** : Isolation entre services
- **Monitoring** : Prometheus + alertes
- **Sauvegardes** : Chiffrées, testées régulièrement

### CI/CD
- **Scans automatiques** : Bandit + Safety
- **Tests RGPD** : Validation données sensibles
- **Dépendances** : Mises à jour sécurité automatiques
- **Accessibilité** : WCAG 2.0 AA minimum

## 🛠️ Processus de Correction

### 1. **Réception** (0-24h)
- Accusé de réception sécurisé
- Assignation équipe sécurité
- Évaluation criticité initiale

### 2. **Investigation** (24-72h)
- Reproduction du problème
- Évaluation impact réel
- Identification solution

### 3. **Développement** (selon criticité)
- Développement du correctif
- Tests en environnement isolé
- Validation pas de régression

### 4. **Déploiement**
- **Critique** : Patch immédiat + communication
- **Non-critique** : Intégration release programmée
- Documentation mise à jour

### 5. **Communication**
- **Avis de sécurité** public (après correction)
- **Guide de mise à jour** pour écoles
- **CVE** si applicable

## 👥 Équipe Sécurité

### Contacts Principaux
- **Security Lead** : security@ecolehub.be
- **RGPD Officer** : dpo@ecolehub.be
- **Technical Lead** : tech@ecolehub.be

### Responsabilités
- **Monitoring** : Surveillance proactive vulnérabilités
- **Response** : Traitement incidents sécurité
- **Prevention** : Amélioration continue sécurité
- **Education** : Formation équipes et communauté

## 🏆 Programme de Reconnaissance

### 🎖️ Hall of Fame Sécurité
Les chercheurs responsables sont reconnus publiquement (avec accord) dans :
- `SECURITY-RESEARCHERS.md`
- Release notes
- Site web EcoleHub

### 🚀 Récompenses Non-Monétaires
- **Mention spéciale** dans la communauté
- **Early access** aux nouvelles fonctionnalités
- **Consultation** sur améliorations sécurité
- **Certificat** de reconnaissance EcoleHub

## 📋 Checklist pour Signalement

Avant de signaler, vérifiez que vous avez :

- [ ] **Testé en environnement isolé** (pas sur données réelles d'école)
- [ ] **Documenté les étapes** de reproduction
- [ ] **Évalué l'impact** potentiel
- [ ] **Vérifié la version** affectée
- [ ] **Anonymisé** tout exemple avec données fictives
- [ ] **Utilisé un canal sécurisé** pour communication

## ⚖️ Légal & Éthique

### Divulgation Responsable
- **90 jours** maximum avant divulgation publique
- **Coordination** avec l'équipe EcoleHub
- **Protection** des écoles en production

### Recherche Autorisée
- ✅ Tests sur votre propre installation
- ✅ Environnements de développement publics
- ❌ Tests sur écoles en production sans autorisation
- ❌ Accès non autorisé à données réelles

### Respect du Cadre Éducatif
La recherche en sécurité sur EcoleHub doit respecter :
- **Bien-être des enfants** en priorité absolue
- **Confiance des familles** dans le système
- **Réglementations RGPD** particulièrement strictes

---

## 🙏 Remerciements

La sécurité d'EcoleHub est une responsabilité partagée. Merci à tous les chercheurs, développeurs et membres de la communauté éducative qui contribuent à maintenir la plateforme sûre pour nos enfants et nos écoles.

**Ensemble, protégeons l'école numérique ! 🏫🔒**

---

**Questions sur cette politique ?** Contactez-nous à security@ecolehub.be