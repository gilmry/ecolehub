# 📋 Guide de Configuration EcoleHub

Ce guide explique comment configurer EcoleHub de manière générique pour différents environnements.

## 🎯 Objectif

Rendre le dépôt GitHub générique et réutilisable par n'importe quelle école, en évitant les configurations spécifiques à une instance particulière.

## 📁 Structure des fichiers

### Fichiers génériques (dans le dépôt)
- `.env.example` - Template de configuration
- `docker-compose.traefik.yml` - Configuration Traefik générique
- `docs/README-TRAEFIK.md` - Guide de déploiement Traefik
- `docs/DEMO-ACCOUNTS.example.md` - Template des comptes de démo
- `docs/CONFIGURATION-GUIDE.md` - Ce guide

### Fichiers spécifiques (ignorés par git)
- `.env` - Configuration locale
- `.env.production` - Configuration production
- `docker-compose.production*.yml` - Configs production spécifiques
- `deploy-*.sh` - Scripts de déploiement personnalisés
- `docs/DEMO-ACCOUNTS.md` - Comptes réels avec mots de passe
- Tous les fichiers listés dans `.gitignore`

## 🚀 Utilisation

### 1. Pour une nouvelle école

```bash
# Cloner le dépôt
git clone https://github.com/gilmry/ecolehub.git
cd ecolehub

# Copier la configuration
cp .env.example .env
cp docs/DEMO-ACCOUNTS.example.md docs/DEMO-ACCOUNTS.md

# Modifier selon vos besoins
nano .env
nano docs/DEMO-ACCOUNTS.md

# Démarrer
docker compose -f docker-compose.traefik.yml up -d
```

### 2. Variables principales à configurer

```bash
# Dans .env
DOMAIN=votre-ecole.example.com
LETSENCRYPT_EMAIL=admin@votre-ecole.example.com
SECRET_KEY=votre-secret-key-unique
DB_PASSWORD=votre-mot-de-passe-securise
# ... autres variables
```

### 3. Personnalisation avancée

Pour des besoins spécifiques, créez vos propres fichiers :
- `docker-compose.production.yml` - Basé sur `docker-compose.traefik.yml`
- `deploy-myschool.sh` - Script de déploiement personnalisé
- Configuration Traefik externe si nécessaire

## 🔒 Sécurité

### Fichiers sensibles
Ces fichiers ne doivent **jamais** être committés :
- `.env` et `.env.production` (mots de passe)
- `docs/DEMO-ACCOUNTS.md` (mots de passe réels)
- Scripts de déploiement (peuvent contenir des IPs/domaines)
- Certificats SSL et clés

### Bonnes pratiques
1. **Toujours** copier `.env.example` vers `.env`
2. **Changer** tous les mots de passe par défaut
3. **Utiliser** des secrets forts (32+ caractères)
4. **Vérifier** que vos fichiers spécifiques sont ignorés par git

## 🌍 Variables d'environnement

### Configuration de base
| Variable | Description | Obligatoire |
|----------|-------------|-------------|
| `DOMAIN` | Domaine principal | ✅ |
| `LETSENCRYPT_EMAIL` | Email certificats SSL | ✅ |
| `SECRET_KEY` | Clé secrète application | ✅ |

### Mots de passe
| Variable | Description | Défaut |
|----------|-------------|---------|
| `DB_PASSWORD` | PostgreSQL | `ecolehub_secure_password` |
| `REDIS_PASSWORD` | Redis | `ecolehub_redis_cache_password` |
| `GRAFANA_PASSWORD` | Grafana | `ecolehub_grafana_admin` |

### APIs externes (optionnel)
| Variable | Description | Stage |
|----------|-------------|-------|
| `MOLLIE_API_KEY` | Paiements | 3+ |
| `PRINTFUL_API_KEY` | Impression | 3+ |

## 📚 Documentation

- [Guide Traefik](./README-TRAEFIK.md)
- [README principal](../README.md)
- [Comptes de démo](./DEMO-ACCOUNTS.example.md)

## 🐛 Support

Pour les questions de configuration :
1. Vérifiez ce guide
2. Consultez le docs/README-TRAEFIK.md
3. Ouvrez une issue sur GitHub