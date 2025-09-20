# Configuration Traefik EcoleHub

Ce guide explique comment déployer EcoleHub avec Traefik en utilisant la configuration générique.

## 🚀 Déploiement Rapide

### 1. Configuration de base

Copiez le fichier de configuration exemple :
```bash
cp .env.example .env
```

Modifiez `.env` avec vos paramètres :
```bash
# Votre domaine
DOMAIN=votre-ecole.example.com

# Email pour Let's Encrypt
LETSENCRYPT_EMAIL=admin@votre-ecole.example.com

# CORS (ajoutez votre domaine)
CORS_ORIGINS=https://votre-ecole.example.com,http://localhost

# Changez les mots de passe (IMPORTANT)
SECRET_KEY=votre-secret-key-tres-long-et-securise
DB_PASSWORD=votre-mot-de-passe-db-securise
REDIS_PASSWORD=votre-mot-de-passe-redis-securise
GRAFANA_PASSWORD=votre-mot-de-passe-grafana-securise
```

### 2. Démarrage des services

```bash
# Avec Traefik intégré (recommandé pour débutants)
docker compose -f docker-compose.traefik.yml up -d

# Ou avec Traefik externe (pour setups avancés)
# Voir section "Traefik Externe" plus bas
```

### 3. Accès aux services

Une fois déployé, vous pouvez accéder à :

- **Application principale** : https://votre-domaine.com
- **Dashboard Traefik** : https://traefik.votre-domaine.com
  - Utilisateur : `admin`
  - Mot de passe : `admin` (changez le hash dans la config!)

## 📋 Variables d'environnement

### Variables obligatoires

| Variable | Description | Exemple |
|----------|-------------|---------|
| `DOMAIN` | Votre domaine principal | `ecole-demo.com` |
| `LETSENCRYPT_EMAIL` | Email pour certificats SSL | `admin@ecole-demo.com` |
| `SECRET_KEY` | Clé secrète de l'application | `très-long-secret-key-unique` |

### Variables optionnelles

| Variable | Description | Défaut |
|----------|-------------|--------|
| `STAGE` | Stage EcoleHub (0-4) | `4` |
| `CORS_ORIGINS` | Domaines autorisés | `http://localhost,https://localhost` |
| `DB_PASSWORD` | Mot de passe PostgreSQL | `ecolehub_secure_password` |
| `REDIS_PASSWORD` | Mot de passe Redis | `ecolehub_redis_cache_password` |
| `GRAFANA_PASSWORD` | Mot de passe Grafana | `ecolehub_grafana_admin` |

## 🔒 Sécurité

### Certificats SSL automatiques

Traefik gère automatiquement les certificats Let's Encrypt pour tous vos domaines.

### Authentification Dashboard

Le dashboard Traefik est protégé par authentification basique.
**Important** : Changez le mot de passe par défaut !

Générez un nouveau hash :
```bash
# Remplacez 'nouveaumotdepasse' par votre mot de passe
echo $(htpasswd -nB admin nouveaumotdepasse) | sed -e s/\\$/\\$\\$/g
```

Puis remplacez la ligne dans `docker-compose.traefik.yml` :
```yaml
- "traefik.http.middlewares.traefik-auth.basicauth.users=admin:VOTRE_NOUVEAU_HASH"
```

### Services internes

Les services suivants ne sont **pas** exposés publiquement :
- PostgreSQL (base de données)
- Redis (cache)
- MinIO (stockage fichiers)
- Prometheus (métriques)
- Grafana (monitoring)

## 🌐 Traefik Externe

Si vous avez déjà un Traefik existant sur votre serveur :

### 1. Assurez-vous que le réseau existe
```bash
docker network create web
```

### 2. Utilisez une configuration sans Traefik
Créez `docker-compose.external-traefik.yml` basé sur `docker-compose.traefik.yml`
mais sans le service `traefik`.

### 3. Connectez vos services au réseau Traefik
Les services `backend` et `frontend` doivent être connectés au réseau `web`.

## 🐛 Dépannage

### Vérification des services
```bash
# Status des conteneurs
docker compose -f docker-compose.traefik.yml ps

# Logs Traefik
docker compose -f docker-compose.traefik.yml logs traefik

# Logs backend
docker compose -f docker-compose.traefik.yml logs backend
```

### Tests de connectivité
```bash
# Test API backend
curl https://votre-domaine.com/health

# Test frontend
curl https://votre-domaine.com/

# Test dashboard Traefik
curl -u admin:motdepasse https://traefik.votre-domaine.com/api/overview
```

### Problèmes courants

**Erreur 502 Bad Gateway**
- Vérifiez que le backend démarre correctement
- Vérifiez les logs : `docker compose logs backend`

**Certificat SSL non généré**
- Vérifiez que votre domaine pointe vers votre serveur
- Vérifiez l'email Let's Encrypt dans `.env`
- Vérifiez les logs Traefik : `docker compose logs traefik`

**Dashboard Traefik inaccessible**
- Vérifiez que `traefik.votre-domaine.com` pointe vers votre serveur
- Vérifiez l'authentification basique

## 📚 Documentation

- [Documentation Traefik](https://doc.traefik.io/traefik/)
- [Configuration Let's Encrypt](https://doc.traefik.io/traefik/https/acme/)
- [EcoleHub Documentation](../README.md)