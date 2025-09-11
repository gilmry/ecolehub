#!/bin/bash
# EcoleHub - Script de génération sécurisée des secrets
# Usage: ./scripts/generate-secrets.sh [--force] [--stage N]

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
SECRETS_DIR="$PROJECT_DIR/secrets"

# Configuration
STAGE=${STAGE:-4}  # Stage par défaut
FORCE_REGENERATE=false

# Couleurs pour les messages
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Fonction d'aide
show_usage() {
    cat << EOF
Usage: $0 [OPTIONS]

Génère les secrets sécurisés pour EcoleHub

OPTIONS:
    -s, --stage STAGE     Stage à configurer (0-4, défaut: 4)
    -f, --force          Force la régénération des secrets existants
    -h, --help           Affiche cette aide

EXEMPLES:
    $0                   # Génère secrets Stage 4
    $0 --stage 2         # Génère secrets Stage 2
    $0 --force           # Régénère TOUS les secrets

SECRETS GÉNÉRÉS:
    - secret_key         # JWT signing (64 chars)
    - db_password        # PostgreSQL (32 chars)
    - redis_password     # Redis (32 chars)
    - minio_secret_key   # MinIO (40 chars)
    - grafana_password   # Grafana admin (16 chars)

Les secrets sont stockés dans: $SECRETS_DIR/
EOF
}

# Fonction de logging
log() {
    local level=$1
    shift
    case $level in
        INFO)  echo -e "${GREEN}[INFO]${NC} $*" ;;
        WARN)  echo -e "${YELLOW}[WARN]${NC} $*" ;;
        ERROR) echo -e "${RED}[ERROR]${NC} $*" >&2 ;;
        DEBUG) echo -e "${BLUE}[DEBUG]${NC} $*" ;;
    esac
}

# Fonction de génération de secret aléatoire
generate_secret() {
    local length=$1
    local chars=${2:-'A-Za-z0-9'}
    
    if command -v openssl >/dev/null 2>&1; then
        openssl rand -base64 $((length * 3 / 4)) | tr -d "=+/" | cut -c1-${length}
    elif [[ -c /dev/urandom ]]; then
        tr -dc "$chars" </dev/urandom | head -c${length}
    else
        log ERROR "Impossible de générer des secrets sécurisés (openssl ou /dev/urandom requis)"
        exit 1
    fi
}

# Fonction de génération de mot de passe sécurisé
generate_password() {
    local length=${1:-32}
    # Éviter les caractères problématiques pour Docker/bash
    generate_secret $length 'A-Za-z0-9@#%^&*'
}

# Fonction de génération de clé JWT
generate_jwt_key() {
    # Clé JWT de 64 caractères (recommandation sécurité)
    generate_secret 64
}

# Fonction de création d'un secret
create_secret() {
    local name=$1
    local value=$2
    local file_path="$SECRETS_DIR/${name}.txt"
    
    if [[ -f "$file_path" ]] && [[ "$FORCE_REGENERATE" != "true" ]]; then
        log WARN "Secret $name existe déjà (utilisez --force pour régénérer)"
        return 0
    fi
    
    # Créer le fichier avec permissions restrictives
    umask 077
    echo -n "$value" > "$file_path"
    chmod 600 "$file_path"
    
    log INFO "Secret $name généré (${#value} caractères)"
}

# Fonction spéciale pour l'authentification Traefik
create_traefik_auth_file() {
    local auth_file="$SECRETS_DIR/traefik_users.txt"
    local admin_password=$(generate_password 16)
    
    if [[ -f "$auth_file" ]] && [[ "$FORCE_REGENERATE" != "true" ]]; then
        log WARN "Auth Traefik existe déjà (utilisez --force pour régénérer)"
        return 0
    fi
    
    # Générer hash bcrypt pour Traefik (format htpasswd)
    if command -v htpasswd >/dev/null 2>&1; then
        # Utiliser htpasswd si disponible
        htpasswd -nbB admin "$admin_password" > "$auth_file"
    elif command -v openssl >/dev/null 2>&1; then
        # Fallback avec openssl (moins sécurisé mais fonctionne)
        local hash=$(openssl passwd -apr1 "$admin_password")
        echo "admin:$hash" > "$auth_file"
    else
        # Fallback simple (développement uniquement)
        log WARN "htpasswd/openssl non disponibles - auth simple utilisée"
        echo "admin:$(echo -n "$admin_password" | base64)" > "$auth_file"
    fi
    
    chmod 600 "$auth_file"
    
    # Sauvegarder le mot de passe en clair pour documentation
    echo -n "$admin_password" > "$SECRETS_DIR/traefik_admin_password.txt"
    chmod 600 "$SECRETS_DIR/traefik_admin_password.txt"
    
    log INFO "Auth Traefik créée - utilisateur: admin, mot de passe: voir traefik_admin_password.txt"
}

# Fonction principale de génération
generate_all_secrets() {
    log INFO "Génération des secrets pour EcoleHub Stage $STAGE"
    
    # Créer le répertoire secrets s'il n'existe pas
    mkdir -p "$SECRETS_DIR"
    chmod 700 "$SECRETS_DIR"
    
    # Secrets critiques (tous stages)
    create_secret "secret_key" "$(generate_jwt_key)"
    
    if [[ $STAGE -ge 1 ]]; then
        create_secret "db_password" "$(generate_password 32)"
    fi
    
    if [[ $STAGE -ge 2 ]]; then
        create_secret "redis_password" "$(generate_password 32)"
    fi
    
    if [[ $STAGE -ge 3 ]]; then
        create_secret "minio_access_key" "ecolehub_admin"
        create_secret "minio_secret_key" "$(generate_password 40)"
    fi
    
    if [[ $STAGE -ge 4 ]]; then
        create_secret "grafana_password" "$(generate_password 16)"
        
        # Traefik dashboard auth (format htpasswd)
        create_traefik_auth_file
    fi
    
    # Secrets API externes (optionnels - placeholders pour production)
    if [[ $STAGE -ge 3 ]]; then
        if [[ ! -f "$SECRETS_DIR/mollie_api_key.txt" ]]; then
            create_secret "mollie_api_key" "test_mollie_key_replace_in_production"
            log WARN "MOLLIE_API_KEY est un placeholder - remplacez en production!"
        fi
        
        if [[ ! -f "$SECRETS_DIR/printful_api_key.txt" ]]; then
            create_secret "printful_api_key" "test_printful_key_replace_in_production"  
            log WARN "PRINTFUL_API_KEY est un placeholder - remplacez en production!"
        fi
    fi
    
    log INFO "Tous les secrets ont été générés dans: $SECRETS_DIR/"
}

# Fonction de validation des secrets existants
validate_secrets() {
    log INFO "Validation des secrets existants..."
    
    local secrets_found=0
    local secrets_invalid=0
    
    for secret_file in "$SECRETS_DIR"/*.txt; do
        if [[ -f "$secret_file" ]]; then
            local filename=$(basename "$secret_file")
            local secret_name="${filename%.txt}"
            local secret_length=$(stat -c%s "$secret_file" 2>/dev/null || wc -c < "$secret_file")
            local permissions=$(stat -c "%a" "$secret_file" 2>/dev/null || echo "unknown")
            
            secrets_found=$((secrets_found + 1))
            
            # Vérifier les permissions
            if [[ "$permissions" != "600" ]]; then
                log WARN "Secret $secret_name: permissions incorrectes ($permissions, attendu: 600)"
                secrets_invalid=$((secrets_invalid + 1))
            fi
            
            # Vérifier la longueur minimale
            if [[ $secret_length -lt 16 ]]; then
                log WARN "Secret $secret_name: trop court ($secret_length chars, min: 16)"
                secrets_invalid=$((secrets_invalid + 1))
            else
                log INFO "Secret $secret_name: OK ($secret_length chars, perms: $permissions)"
            fi
        fi
    done
    
    if [[ $secrets_found -eq 0 ]]; then
        log WARN "Aucun secret trouvé - exécutez la génération"
        return 1
    fi
    
    if [[ $secrets_invalid -gt 0 ]]; then
        log ERROR "$secrets_invalid/$secrets_found secrets ont des problèmes"
        return 1
    fi
    
    log INFO "Validation réussie: $secrets_found secrets corrects"
    return 0
}

# Fonction d'export pour .env (développement)
export_env_file() {
    local env_file="$PROJECT_DIR/.env.secrets"
    
    log INFO "Export des secrets vers $env_file (développement uniquement)"
    
    cat > "$env_file" << 'EOF'
# Secrets EcoleHub - DÉVELOPPEMENT UNIQUEMENT
# Ne jamais commiter ce fichier!
# En production, utilisez Docker secrets

EOF
    
    for secret_file in "$SECRETS_DIR"/*.txt; do
        if [[ -f "$secret_file" ]]; then
            local filename=$(basename "$secret_file")
            local secret_name="${filename%.txt}"
            local secret_value=$(<"$secret_file")
            local env_name=$(echo "$secret_name" | tr '[:lower:]' '[:upper:]')
            
            echo "${env_name}=${secret_value}" >> "$env_file"
        fi
    done
    
    chmod 600 "$env_file"
    log INFO "Fichier .env.secrets créé (ne pas commiter!)"
}

# Fonction d'affichage du résumé
show_summary() {
    log INFO "=== RÉSUMÉ DES SECRETS GÉNÉRÉS ==="
    
    for secret_file in "$SECRETS_DIR"/*.txt; do
        if [[ -f "$secret_file" ]]; then
            local filename=$(basename "$secret_file")
            local secret_name="${filename%.txt}"
            local secret_length=$(stat -c%s "$secret_file" 2>/dev/null || wc -c < "$secret_file")
            local preview=$(head -c8 "$secret_file")
            
            printf "  %-20s %3d chars  %s...\n" "$secret_name" "$secret_length" "$preview"
        fi
    done
    
    echo
    log INFO "PROCHAINES ÉTAPES:"
    echo "  1. Vérifiez les secrets dans: $SECRETS_DIR/"
    echo "  2. En production: remplacez mollie_api_key et printful_api_key"
    echo "  3. Lancez Docker Compose: docker compose -f docker-compose.stage${STAGE}.yml up -d"
    echo "  4. Les secrets sont automatiquement montés dans /run/secrets/"
    echo
    log WARN "SÉCURITÉ: Ne jamais commiter le dossier secrets/ !"
}

# Parse des arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -s|--stage)
            STAGE="$2"
            shift 2
            ;;
        -f|--force)
            FORCE_REGENERATE=true
            shift
            ;;
        -h|--help)
            show_usage
            exit 0
            ;;
        --validate)
            validate_secrets
            exit $?
            ;;
        --export-env)
            export_env_file
            exit 0
            ;;
        *)
            log ERROR "Option inconnue: $1"
            show_usage
            exit 1
            ;;
    esac
done

# Validation des paramètres
if [[ ! "$STAGE" =~ ^[0-4]$ ]]; then
    log ERROR "Stage invalide: $STAGE (doit être 0-4)"
    exit 1
fi

# Vérifications préliminaires
if [[ $EUID -eq 0 ]]; then
    log WARN "Exécution en tant que root - les permissions peuvent être incorrectes"
fi

# Affichage de la configuration
log INFO "Configuration:"
echo "  Stage: $STAGE"
echo "  Répertoire secrets: $SECRETS_DIR"
echo "  Force regeneration: $FORCE_REGENERATE"
echo

# Exécution principale
main() {
    generate_all_secrets
    validate_secrets
    show_summary
    
    log INFO "✅ Génération des secrets terminée avec succès!"
}

# Point d'entrée
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi