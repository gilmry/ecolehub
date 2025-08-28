# 🚀 Installation Guide - EcoleHub Stage 0

Guide d'installation pour EcoleHub - EcoleHub.

## ⚡ Installation Rapide (5 minutes)

### Pré-requis
- **Docker** & **Docker Compose** installés
- **Git** pour cloner le repository
- **Port 80 et 8000** disponibles

### Installation Automatique

```bash
# 1. Cloner le projet
git clone <votre-repository-url>
cd schoolhub

# 2. Configuration
cp .env.example .env

# 3. Lancer l'application
docker-compose up -d

# 4. Vérifier le démarrage
curl http://localhost:8000/health

# 5. Accéder à l'application
open http://localhost
```

**✅ C'est terminé !** L'application est accessible sur http://localhost

## 📋 Installation Détaillée

### 1. Vérification Pré-requis

#### Docker
```bash
# Vérifier Docker
docker --version
# Doit afficher: Docker version 20.10.x ou plus récent

# Vérifier Docker Compose
docker-compose --version
# Doit afficher: Docker Compose version 2.x.x ou plus récent
```

#### Ports Disponibles
```bash
# Vérifier que les ports sont libres
netstat -tuln | grep :80    # Doit être vide
netstat -tuln | grep :8000  # Doit être vide
```

### 2. Configuration

#### Variables d'Environnement
```bash
# Copier le template
cp .env.example .env

# Modifier les variables (obligatoire)
nano .env
```

**⚠️ IMPORTANT**: Modifier `SECRET_KEY` en production :
```env
SECRET_KEY=votre-clef-secrete-tres-longue-et-aleatoire-ici
DATABASE_URL=sqlite:///./schoolhub.db
```

#### Configuration Optionnelle
```bash
# Pour un domaine personnalisé
DOMAIN=votre-domaine.com
CORS_ORIGINS=https://votre-domaine.com

# Pour production avec SSL
EMAIL=admin@votre-domaine.com
```

### 3. Démarrage

#### Première Exécution
```bash
# Lancer en mode détaché (arrière-plan)
docker-compose up -d

# Voir les logs de démarrage
docker-compose logs -f
```

#### Vérification
```bash
# Status des containers
docker-compose ps

# Tester l'API
curl http://localhost:8000/health

# Tester le frontend
curl -I http://localhost/
```

### 4. Premier Utilisateur

#### Via Interface Web
1. Aller sur http://localhost
2. Cliquer "S'inscrire"
3. Remplir : email, prénom, nom, mot de passe
4. Ajouter des enfants avec leurs classes

#### Via API (optionnel)
```bash
# Inscription
curl -X POST http://localhost:8000/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "parent@ecolehub.local",
    "password": "motdepasse123",
    "first_name": "Marie",
    "last_name": "Martin"
  }'
```

## 🔧 Configuration Avancée

### SSL/HTTPS (Production)

#### Avec Let's Encrypt
```bash
# Installer Certbot
sudo apt install certbot

# Obtenir certificat
sudo certbot certonly --standalone -d votre-domaine.com

# Modifier nginx.conf (décommenter section HTTPS)
nano nginx.conf

# Relancer
docker-compose restart frontend
```

#### Configuration nginx.conf
```nginx
server {
    listen 443 ssl;
    server_name votre-domaine.com;
    
    ssl_certificate /etc/letsencrypt/live/votre-domaine.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/votre-domaine.com/privkey.pem;
    
    # ... reste de la configuration
}
```

### Base de Données

#### Accès SQLite (Debug)
```bash
# Accéder à la DB
docker-compose exec backend sqlite3 schoolhub.db

# Commandes utiles
.tables                    # Voir les tables
SELECT * FROM users;       # Voir les utilisateurs
SELECT * FROM children;    # Voir les enfants
.quit                      # Quitter
```

#### Backup
```bash
# Sauvegarder la base
docker-compose exec backend sqlite3 schoolhub.db ".backup backup.db"

# Restaurer
docker-compose exec backend sqlite3 schoolhub.db ".restore backup.db"
```

### Monitoring

#### Logs
```bash
# Tous les logs
docker-compose logs

# Logs backend seulement
docker-compose logs backend

# Logs en temps réel
docker-compose logs -f
```

#### Métriques
```bash
# Usage containers
docker stats

# Espace disque
df -h
du -sh .
```

## 🛠️ Dépannage

### Problèmes Courants

#### Port 80 occupé
```bash
# Changer le port dans docker-compose.yml
ports:
  - "8080:80"  # Au lieu de "80:80"
```

#### Erreur de permissions
```bash
# Permissions Docker (Linux)
sudo usermod -aG docker $USER
# Se déconnecter/reconnecter

# Permissions fichiers
sudo chown -R $USER:$USER .
```

#### Container ne démarre pas
```bash
# Voir les erreurs
docker-compose logs backend
docker-compose logs frontend

# Redémarrer un service
docker-compose restart backend

# Reconstruction complète
docker-compose down
docker-compose up -d --build
```

#### Base de données corrompue
```bash
# Supprimer et recréer
docker-compose down
rm backend/schoolhub.db  # ⚠️ Perte de données !
docker-compose up -d
```

### Logs d'Erreur

#### Erreurs Backend
```bash
# Python/FastAPI errors
docker-compose logs backend | grep ERROR

# Database errors
docker-compose logs backend | grep sqlite
```

#### Erreurs Frontend
```bash
# Nginx errors
docker-compose logs frontend | grep error

# Vérifier la configuration
docker-compose exec frontend nginx -t
```

## 🏥 Maintenance

### Mises à Jour

#### Code Application
```bash
# Récupérer dernière version
git pull origin main

# Reconstruire et relancer
docker-compose down
docker-compose up -d --build
```

#### Images Docker
```bash
# Mettre à jour les images
docker-compose pull
docker-compose up -d
```

### Arrêt/Redémarrage

#### Arrêt Propre
```bash
# Arrêt des services
docker-compose down

# Arrêt avec suppression volumes (⚠️ perte données)
docker-compose down -v
```

#### Redémarrage
```bash
# Redémarrage rapide
docker-compose restart

# Redémarrage avec reconstruction
docker-compose down && docker-compose up -d --build
```

## 🆘 Support

### Auto-diagnostic
```bash
# Script de diagnostic
curl -s http://localhost:8000/health | jq .
docker-compose ps
docker-compose logs --tail=20
```

### Contact
- **Issues Techniques**: [GitHub Issues](https://github.com/votre-org/schoolhub/issues)
- **École**: Administration EcoleHub
- **Email**: admin@ecolehub.local (exemple)

### Informations Système
```bash
# Informations pour support
echo "=== SYSTEM INFO ==="
uname -a
docker --version
docker-compose --version
echo "=== CONTAINERS ==="
docker-compose ps
echo "=== HEALTH ==="
curl -s http://localhost:8000/health 2>/dev/null || echo "Backend inaccessible"
```

---

## 📈 Prochaines Étapes

Une fois Stage 0 stable avec 5+ familles :
1. **Stage 1**: Migration PostgreSQL + SEL
2. **Monitoring**: Prometheus + Grafana
3. **SSL**: Certificats Let's Encrypt automatiques
4. **Backup**: Sauvegardes automatisées

---

**Version**: Stage 0 (v0.1.0)  
**École**: EcoleHub 🏫