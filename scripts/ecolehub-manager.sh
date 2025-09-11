#!/bin/bash
# EcoleHub Management CLI
# Simplified credential and account management using Docker

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
COMPOSE_FILE="$PROJECT_DIR/docker-compose.stage4.yml"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
WHITE='\033[1;37m'
NC='\033[0m' # No Color

# Helper functions
log_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Check if docker compose is available
check_docker() {
    if ! command -v docker &> /dev/null; then
        log_error "Docker is not installed or not in PATH"
        exit 1
    fi

    if ! docker compose version &> /dev/null; then
        log_error "Docker Compose is not available"
        exit 1
    fi
}

# Execute SQL query in PostgreSQL container
exec_sql() {
    local query="$1"
    docker compose -f "$COMPOSE_FILE" exec -T postgres \
        psql -U ecolehub -d ecolehub -c "$query" 2>/dev/null
}

# Generate secure password
generate_password() {
    local length=${1:-12}
    openssl rand -base64 $((length * 3 / 4)) | tr -d "=+/" | cut -c1-${length}
}

# Hash password using backend
hash_password() {
    local password="$1"
    docker compose -f "$COMPOSE_FILE" exec -T backend python3 -c "
import sys
sys.path.append('/app')
from passlib.context import CryptContext
pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
print(pwd_context.hash('$password'))
" 2>/dev/null | tr -d '\r'
}

# User Management Functions
list_users() {
    local role="$1"
    local limit=${2:-20}
    
    log_info "EcoleHub Users"
    echo "$(tput smul)Email$(tput sgr0)                     $(tput smul)Name$(tput sgr0)                    $(tput smul)Role$(tput sgr0)        $(tput smul)Active$(tput sgr0)  $(tput smul)Created$(tput sgr0)"
    echo "────────────────────────────────────────────────────────────────────────────────"
    
    local query="SELECT email, first_name, last_name, role, is_active, created_at FROM users"
    if [[ -n "$role" ]]; then
        query="$query WHERE role = '$role'"
    fi
    query="$query ORDER BY created_at DESC LIMIT $limit;"
    
    docker compose -f "$COMPOSE_FILE" exec -T postgres \
        psql -U ecolehub -d ecolehub -t -c "$query" | while IFS='|' read -r email fname lname role active created; do
        
        # Trim whitespace
        email=$(echo "$email" | xargs)
        fname=$(echo "$fname" | xargs) 
        lname=$(echo "$lname" | xargs)
        role=$(echo "$role" | xargs)
        active=$(echo "$active" | xargs)
        created=$(echo "$created" | cut -d' ' -f1 | xargs)
        
        if [[ -n "$email" ]]; then
            local status="❌"
            if [[ "$active" == "t" ]]; then
                status="✅"
            fi
            
            printf "%-30s %-25s %-12s %-8s %s\n" \
                "$email" \
                "$fname $lname" \
                "$role" \
                "$status" \
                "$created"
        fi
    done
}

create_user() {
    local email="$1"
    local first_name="$2"
    local last_name="$3"
    local password="$4"
    local role="${5:-parent}"
    
    if [[ -z "$email" || -z "$first_name" || -z "$last_name" ]]; then
        log_error "Usage: create_user <email> <first_name> <last_name> [password] [role]"
        return 1
    fi
    
    # Generate password if not provided
    if [[ -z "$password" ]]; then
        password=$(generate_password)
        local generated=true
    else
        local generated=false
    fi
    
    log_info "Creating user: $first_name $last_name ($email)"
    
    # Hash the password
    local hashed_password
    hashed_password=$(hash_password "$password")
    
    # Insert user into database
    local query="INSERT INTO users (email, first_name, last_name, hashed_password, role, is_active) VALUES ('$email', '$first_name', '$last_name', '$hashed_password', '$role', true);"
    
    if exec_sql "$query" >/dev/null; then
        log_success "User created successfully!"
        echo -e "${WHITE}   📧 Email: $email${NC}"
        echo -e "${WHITE}   👤 Name: $first_name $last_name${NC}"
        echo -e "${WHITE}   🎭 Role: $role${NC}"
        if [[ "$generated" == "true" ]]; then
            echo -e "${YELLOW}   🔑 Password: $password${NC}"
            echo -e "${YELLOW}   ⚠️  Please share this password securely!${NC}"
        fi
    else
        log_error "Failed to create user. Email might already exist."
    fi
}

reset_password() {
    local email="$1"
    local new_password="$2"
    
    if [[ -z "$email" ]]; then
        log_error "Usage: reset_password <email> [new_password]"
        return 1
    fi
    
    # Generate password if not provided
    if [[ -z "$new_password" ]]; then
        new_password=$(generate_password)
        local generated=true
    else
        local generated=false
    fi
    
    log_info "Resetting password for: $email"
    
    # Hash the password
    local hashed_password
    hashed_password=$(hash_password "$new_password")
    
    # Update password in database
    local query="UPDATE users SET hashed_password = '$hashed_password', updated_at = NOW() WHERE email = '$email';"
    
    if exec_sql "$query" | grep -q "UPDATE 1"; then
        log_success "Password reset successful!"
        echo -e "${WHITE}   📧 Email: $email${NC}"
        if [[ "$generated" == "true" ]]; then
            echo -e "${YELLOW}   🔑 New Password: $new_password${NC}"
            echo -e "${YELLOW}   ⚠️  Please share this password securely!${NC}"
        fi
    else
        log_error "Failed to reset password. User not found."
    fi
}

toggle_user_status() {
    local email="$1"
    local action="$2"  # activate or deactivate
    
    if [[ -z "$email" || -z "$action" ]]; then
        log_error "Usage: toggle_user_status <email> <activate|deactivate>"
        return 1
    fi
    
    local status="true"
    local message="activated"
    local icon="✅"
    
    if [[ "$action" == "deactivate" ]]; then
        status="false"
        message="deactivated"
        icon="⏸️ "
    fi
    
    local query="UPDATE users SET is_active = $status, updated_at = NOW() WHERE email = '$email';"
    
    if exec_sql "$query" | grep -q "UPDATE 1"; then
        log_success "User $message: $email"
    else
        log_error "User not found: $email"
    fi
}

# Credential Management Functions
show_credentials() {
    log_info "EcoleHub Stage 4 - Service Credentials"
    echo "═══════════════════════════════════════════════════════════════"
    
    # Load environment variables
    if [[ -f "$PROJECT_DIR/.env" ]]; then
        source "$PROJECT_DIR/.env"
    fi
    
    echo -e "\n${CYAN}📊 DATABASE (PostgreSQL)${NC}"
    echo "  Host: localhost:5432"
    echo "  Database: ecolehub"
    echo "  Username: ecolehub"
    echo "  Password: ${DB_PASSWORD:-ecolehub_secure_password}"
    
    echo -e "\n${CYAN}🗄️  CACHE (Redis)${NC}"
    echo "  Host: localhost:6379"
    echo "  Password: ${REDIS_PASSWORD:-redis_secure_password}"
    
    echo -e "\n${CYAN}📦 STORAGE (MinIO)${NC}"
    echo "  Console: http://localhost:9001"
    echo "  API: http://localhost:9000"
    echo "  Access Key: ${MINIO_ACCESS_KEY:-ecolehub_minio}"
    echo "  Secret Key: ${MINIO_SECRET_KEY:-minio_secure_password}"
    
    echo -e "\n${CYAN}📈 MONITORING${NC}"
    echo "  Grafana: http://localhost:3001"
    echo "  Username: admin"
    echo "  Password: ${GRAFANA_PASSWORD:-admin_ecolehub_monitoring}"
    echo "  Prometheus: http://localhost:9090"
    
    echo -e "\n${CYAN}🏫 APPLICATION${NC}"
    echo "  Frontend: http://localhost"
    echo "  Backend API: http://localhost:8000"
    echo "  API Docs: http://localhost:8000/docs"
    
    echo -e "\n${CYAN}👥 TEST ACCOUNTS${NC}"
    echo "  Demo User: demo@example.com / demo123 (parent)"
    echo "  Parent 1: parent1@example.be / parent123 (parent - Marie Dupont)"
    echo "  Parent 2: parent2@example.be / parent123 (parent - Jean Martin)"
    echo "  Test User: test@example.com / test123 (parent)"
    echo "  Teacher: teacher@ecolehub.be / teacher123 (admin - Marie Professor)"
    echo "  Admin: admin@ecolehub.be / admin123 (admin)"
    echo "  Direction: direction@ecolehub.be / direction123 (direction)"
}

generate_secrets() {
    log_info "Generating new secure credentials..."
    
    local secrets_file="$PROJECT_DIR/.env.secrets.new"
    
    cat > "$secrets_file" << EOF
# EcoleHub - New Generated Secrets
# Generated on: $(date)

# Application security
SECRET_KEY=$(openssl rand -base64 64 | tr -d "=+/" | cut -c1-64)

# Database
DB_PASSWORD=$(generate_password 16)

# Redis
REDIS_PASSWORD=$(generate_password 16)

# MinIO
MINIO_ACCESS_KEY=ecolehub_minio
MINIO_SECRET_KEY=$(generate_password 20)

# Monitoring
GRAFANA_PASSWORD=$(generate_password 12)

# Payment APIs (replace with real keys)
MOLLIE_API_KEY=test_mollie_key_replace_in_production
PRINTFUL_API_KEY=test_printful_key_replace_in_production
EOF

    log_success "New secure credentials generated!"
    echo -e "${WHITE}💾 Secrets saved to: $secrets_file${NC}"
    echo -e "${YELLOW}⚠️  IMPORTANT: Update your .env file and restart services!${NC}"
    
    echo -e "\n${WHITE}New credentials:${NC}"
    cat "$secrets_file" | grep -E "^[A-Z_]+"
}

# Service Management Functions
service_status() {
    log_info "EcoleHub Services Status"
    echo "────────────────────────────────────────────────────────────"
    docker compose -f "$COMPOSE_FILE" ps
}

restart_service() {
    local service="$1"
    
    if [[ -z "$service" ]]; then
        log_error "Usage: restart_service <service_name>"
        return 1
    fi
    
    log_info "Restarting service: $service"
    if docker compose -f "$COMPOSE_FILE" restart "$service"; then
        log_success "Service '$service' restarted successfully"
    else
        log_error "Failed to restart service '$service'"
    fi
}

# Main function
main() {
    check_docker
    
    case "${1:-help}" in
        # User management
        "users")
            case "${2:-list}" in
                "list")
                    list_users "$3" "$4"
                    ;;
                "create")
                    create_user "$3" "$4" "$5" "$6" "$7"
                    ;;
                "reset-password")
                    reset_password "$3" "$4"
                    ;;
                "activate")
                    toggle_user_status "$3" "activate"
                    ;;
                "deactivate")
                    toggle_user_status "$3" "deactivate"
                    ;;
                *)
                    echo "Usage: $0 users <list|create|reset-password|activate|deactivate> [args...]"
                    ;;
            esac
            ;;
        
        # Credential management
        "creds")
            case "${2:-show}" in
                "show"|"list")
                    show_credentials
                    ;;
                "generate")
                    generate_secrets
                    ;;
                *)
                    echo "Usage: $0 creds <show|list|generate>"
                    ;;
            esac
            ;;
        
        # Service management
        "services")
            case "${2:-status}" in
                "status")
                    service_status
                    ;;
                "restart")
                    restart_service "$3"
                    ;;
                *)
                    echo "Usage: $0 services <status|restart> [service_name]"
                    ;;
            esac
            ;;
        
        # Help and examples
        "help"|"-h"|"--help")
            cat << 'EOF'
🏫 EcoleHub Management CLI
Belgian school collaborative platform administration

USAGE:
    ecolehub <command> <subcommand> [options...]

COMMANDS:
    users       User account management
    creds       Credential management  
    services    Service management

USER MANAGEMENT:
    ecolehub users list [role] [limit]                   # List users
    ecolehub users create <email> <fname> <lname> [pwd] [role]  # Create user
    ecolehub users reset-password <email> [new_password] # Reset password
    ecolehub users activate <email>                      # Activate user
    ecolehub users deactivate <email>                    # Deactivate user

CREDENTIAL MANAGEMENT:
    ecolehub creds show                                  # Show all credentials
    ecolehub creds list                                  # Show all credentials (alias)
    ecolehub creds generate                              # Generate new secrets

SERVICE MANAGEMENT:
    ecolehub services status                             # Show service status
    ecolehub services restart <service>                  # Restart service

EXAMPLES:
    ecolehub users create john@school.be "John" "Doe"
    ecolehub users list parent 10
    ecolehub users reset-password admin@ecolehub.be
    ecolehub creds show
    ecolehub services restart backend

For more information, visit: https://github.com/ecolehub/ecolehub
EOF
            ;;
        
        *)
            log_error "Unknown command: $1"
            echo "Use '$0 help' for usage information"
            exit 1
            ;;
    esac
}

# Execute main function with all arguments
main "$@"