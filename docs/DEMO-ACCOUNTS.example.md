# 🎓 Comptes de Démo EcoleHub

## 🌐 Accès à la plateforme
- **URL** : https://VOTRE-DOMAINE.com
- **API** : https://VOTRE-DOMAINE.com/api/

## 🔑 Comptes de démonstration

**Mot de passe universel** : `VOTRE-MOT-DE-PASSE-DEMO`

### 👨‍💼 Administrateur
- **Email** : `admin@ecolehub.be`
- **Rôle** : Administrateur système
- **Accès** : Gestion complète de la plateforme

### 🏫 Direction
- **Email** : `direction@ecolehub.be`
- **Rôle** : Direction d'école
- **Accès** : Gestion pédagogique et administrative

### 👨‍👩‍👧‍👦 Parents
1. **Email** : `parent1@example.be`
   **Rôle** : Parent
   **Accès** : Suivi enfants, SEL, événements

2. **Email** : `parent2@example.be`
   **Rôle** : Parent
   **Accès** : Suivi enfants, SEL, événements

## 🔧 Test de connexion API

```bash
# Test de login
curl -X POST https://VOTRE-DOMAINE.com/api/login \\
  -H 'Content-Type: application/x-www-form-urlencoded' \\
  -d 'email=admin@ecolehub.be&password=VOTRE-MOT-DE-PASSE-DEMO'

# Test profil (avec le token obtenu)
curl -H "Authorization: Bearer YOUR_TOKEN" \\
  https://VOTRE-DOMAINE.com/api/me
```

## 📊 Statut des services

Tous les services sont fonctionnels :
- ✅ **Frontend** : Interface utilisateur
- ✅ **Backend** : API REST + WebSockets
- ✅ **PostgreSQL** : Base de données
- ✅ **Redis** : Cache et sessions
- ✅ **MinIO** : Stockage fichiers

## 🔒 Sécurité

- ✅ **HTTPS** : Certificats Let's Encrypt automatiques
- ✅ **JWT** : Authentification par tokens
- ✅ **Services privés** : MinIO, Prometheus, Grafana non exposés
- ✅ **Headers sécurisés** : HSTS, XSS Protection, etc.

## 🎯 Fonctionnalités de démo

La plateforme Stage 4 inclut :
- Gestion des utilisateurs et profils
- Système SEL (échange local)
- Boutique et paiements (Mollie)
- Ressources éducatives
- Messagerie et événements
- Analytics et monitoring
- Support multilingue (FR-BE/NL-BE/EN)