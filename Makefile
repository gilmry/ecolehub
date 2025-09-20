# 🏫 EcoleHub Stage 4 - Makefile
# Belgian school collaborative platform management
# 
# Quick start:
#   make help     - Show this help
#   make start    - Start all services
#   make stop     - Stop all services
#   make status   - Show service status

.PHONY: help start stop restart status logs clean build dev test lint format backup restore

# Default target
.DEFAULT_GOAL := help

# Docker Compose configuration
# Default to Stage 4 compose as documented; allow override and fallback.
# Order:
# 1) docker-compose.stage4.yml (dev/full stack; matches docs)
# 2) docker-compose.traefik.yml (production with HTTPS)
# 3) docker-compose.yml (fallback)
COMPOSE_FILE ?= $(shell if [ -f docker-compose.stage4.yml ]; then echo docker-compose.stage4.yml; \
                        elif [ -f docker-compose.traefik.yml ]; then echo docker-compose.traefik.yml; \
                        else echo docker-compose.yml; fi)
COMPOSE := docker compose -f $(COMPOSE_FILE)

# Colors for output
GREEN := \033[0;32m
BLUE := \033[0;34m
YELLOW := \033[0;33m
RED := \033[0;31m
NC := \033[0m # No Color

##@ 🚀 Main Commands

help: ## Show this help message
	@echo "🏫 $(GREEN)EcoleHub Stage 4$(NC) - Management Commands"
	@echo ""
	@echo "Using compose file: $(YELLOW)$(COMPOSE_FILE)$(NC)"
	@echo "$(BLUE)Available commands:$(NC)"
	@awk 'BEGIN {FS = ":.*##"; printf "\n"} /^[a-zA-Z_0-9-]+:.*?##/ { printf "  $(BLUE)%-15s$(NC) %s\n", $$1, $$2 } /^##@/ { printf "\n$(YELLOW)%s$(NC)\n", substr($$0, 5) } ' $(MAKEFILE_LIST)
	@echo ""
	@echo "$(YELLOW)Example usage:$(NC)"
	@echo "  make start        # Start the application"
	@echo "  make logs         # View logs"
	@echo "  make users-list   # List all users"
	@echo "  COMPOSE_FILE=docker-compose.traefik.yml make start  # Override file"
	@echo ""

start: ## Start all services
	@echo "🚀 $(GREEN)Starting EcoleHub Stage 4...$(NC)"
	$(COMPOSE) up -d
	@echo "⏳ Waiting for services to be ready..."
	@sleep 15
	@echo "✅ $(GREEN)Services started!$(NC)"
	@echo "   🌐 Frontend: http://localhost/"
	@echo "   🔌 API: http://localhost/api/"
	@echo "   📊 Grafana: http://localhost:3001/"
	@echo "   🔍 Traefik: http://localhost:8080/"

start-traefik: ## Start using docker-compose.traefik.yml
	@$(MAKE) start COMPOSE_FILE=docker-compose.traefik.yml

start-stage4: ## Start using docker-compose.stage4.yml
	@$(MAKE) start COMPOSE_FILE=docker-compose.stage4.yml

stop: ## Stop all services
	@echo "🛑 $(YELLOW)Stopping EcoleHub services...$(NC)"
	$(COMPOSE) down
	@echo "✅ $(GREEN)Services stopped$(NC)"

restart: ## Restart all services
	@echo "🔄 $(YELLOW)Restarting EcoleHub services...$(NC)"
	$(COMPOSE) restart
	@echo "✅ $(GREEN)Services restarted$(NC)"

status: ## Show service status
	@echo "📊 $(BLUE)EcoleHub Service Status:$(NC)"
	$(COMPOSE) ps

##@ 🐳 Docker Management

build: ## Build/rebuild all services
	@echo "🔨 $(YELLOW)Building EcoleHub services...$(NC)"
	$(COMPOSE) build --no-cache
	@echo "✅ $(GREEN)Build complete$(NC)"

pull: ## Pull latest images
	@echo "⬇️ $(YELLOW)Pulling latest images...$(NC)"
	$(COMPOSE) pull
	@echo "✅ $(GREEN)Images updated$(NC)"

clean: ## Clean up containers and volumes
	@echo "🧹 $(YELLOW)Cleaning up Docker resources...$(NC)"
	$(COMPOSE) down -v --remove-orphans
	@docker system prune -f
	@echo "✅ $(GREEN)Cleanup complete$(NC)"

##@ 📋 Logs & Monitoring

logs: ## View all service logs
	$(COMPOSE) logs -f

logs-backend: ## View backend logs only
	$(COMPOSE) logs -f backend

logs-frontend: ## View frontend logs only
	$(COMPOSE) logs -f frontend

logs-traefik: ## View Traefik logs only
	$(COMPOSE) logs -f traefik

health: ## Check backend health
	@echo "🏥 $(BLUE)Checking backend health...$(NC)"
	@curl -s http://localhost/api/health | jq . || echo "❌ Backend not responding"

##@ 👥 User Management

users-list: ## List all users
	@echo "👥 $(BLUE)EcoleHub Users:$(NC)"
	./ecolehub users list

users-create: ## Create new user (interactive)
	@echo "👤 $(BLUE)Creating new user...$(NC)"
	@read -p "Email: " email; \
	read -p "First Name: " fname; \
	read -p "Last Name: " lname; \
	read -p "Role (parent/admin/direction): " role; \
	./ecolehub users create "$$email" "$$fname" "$$lname" "" "$$role"

users-reset: ## Reset user password (interactive)
	@echo "🔑 $(BLUE)Resetting user password...$(NC)"
	@read -p "User email: " email; \
	./ecolehub users reset-password "$$email"

##@ 🔐 Credentials & Security

creds-show: ## Show all credentials
	@echo "🔐 $(BLUE)System Credentials:$(NC)"
	./ecolehub creds show

creds-generate: ## Generate new secure credentials
	@echo "🔒 $(YELLOW)Generating new secure credentials...$(NC)"
	./ecolehub creds generate
	@echo "⚠️  $(RED)Remember to update your .env file!$(NC)"

##@ 🛠️ Development

dev: ## Start in development mode with live reload
	@echo "🚧 $(BLUE)Starting development environment...$(NC)"
	$(COMPOSE) up -d postgres redis minio
	@echo "💻 Backend: Run manually in your IDE"
	@echo "🌐 Frontend: Served via nginx on http://localhost/"

test: ## Run backend tests
	@echo "🧪 $(BLUE)Running tests...$(NC)"
	$(COMPOSE) exec backend pip install -r requirements.test.txt -q
	$(COMPOSE) exec backend pytest tests/ -v

test-unit: ## Run unit tests only
	@echo "🧪 $(BLUE)Running unit tests...$(NC)"
	$(COMPOSE) exec backend pip install -r requirements.test.txt -q
	$(COMPOSE) exec backend pytest tests/unit/ -v -m unit

test-integration: ## Run integration tests only
	@echo "🧪 $(BLUE)Running integration tests...$(NC)"
	$(COMPOSE) exec backend pip install -r requirements.test.txt -q
	$(COMPOSE) exec backend pytest tests/integration/ -v -m integration

test-auth: ## Run authentication tests only
	@echo "🧪 $(BLUE)Running authentication tests...$(NC)"
	$(COMPOSE) exec backend pip install -r requirements.test.txt -q
	$(COMPOSE) exec backend pytest tests/ -v -m auth

test-sel: ## Run SEL system tests only
	@echo "🧪 $(BLUE)Running SEL system tests...$(NC)"
	$(COMPOSE) exec backend pip install -r requirements.test.txt -q
	$(COMPOSE) exec backend pytest tests/ -v -m sel

test-coverage: ## Run tests with coverage report
	@echo "🧪 $(BLUE)Running tests with coverage...$(NC)"
	$(COMPOSE) exec backend pip install -r requirements.test.txt -q
	$(COMPOSE) exec backend pytest tests/ --cov=app --cov-report=html --cov-report=term

test-install: ## Install test dependencies
	@echo "📦 $(BLUE)Installing test dependencies...$(NC)"
	$(COMPOSE) exec backend pip install -r requirements.test.txt
	@echo "✅ $(GREEN)Test dependencies installed$(NC)"

lint: ## Run code linting
	@echo "🔍 $(BLUE)Running linters...$(NC)"
	$(COMPOSE) exec backend python -m flake8 app/ tests/ || true
	$(COMPOSE) exec backend python -m black --check app/ tests/ || true
	$(COMPOSE) exec backend python -m isort --check-only app/ tests/ || true

format: ## Format code automatically
	@echo "📝 $(BLUE)Auto-formatting Python code...$(NC)"
	./scripts/format-python.sh

format-docker: ## Format code using Docker containers
	@echo "📝 $(BLUE)Formatting code in containers...$(NC)"
	$(COMPOSE) exec backend python -m autoflake --in-place --remove-all-unused-imports --remove-unused-variables --recursive app/ tests/ || true
	$(COMPOSE) exec backend python -m isort app/ tests/ --profile black || true
	$(COMPOSE) exec backend python -m autopep8 --in-place --aggressive --aggressive --recursive app/ tests/ || true
	$(COMPOSE) exec backend python -m black app/ tests/ || true

shell-backend: ## Open shell in backend container
	$(COMPOSE) exec backend /bin/bash

shell-db: ## Open database shell
	$(COMPOSE) exec postgres psql -U ecolehub -d ecolehub

##@ 💾 Backup & Restore

backup: ## Create full backup
	@echo "💾 $(BLUE)Creating backup...$(NC)"
	@mkdir -p backups
	@timestamp=$$(date +%Y%m%d_%H%M%S); \
	$(COMPOSE) exec postgres pg_dump -U ecolehub ecolehub > backups/ecolehub_$$timestamp.sql
	@echo "✅ $(GREEN)Backup created in backups/$(NC)"

restore: ## Restore from backup (interactive)
	@echo "📥 $(BLUE)Available backups:$(NC)"
	@ls -la backups/
	@read -p "Backup filename: " backup; \
	$(COMPOSE) exec -T postgres psql -U ecolehub -d ecolehub < backups/$$backup

##@ 🔧 Service Management

restart-backend: ## Restart backend service only
	$(COMPOSE) restart backend

restart-frontend: ## Restart frontend service only
	$(COMPOSE) restart frontend

restart-traefik: ## Restart Traefik proxy
	$(COMPOSE) restart traefik

restart-db: ## Restart database
	$(COMPOSE) restart postgres

##@ 📖 Information

urls: ## Show all service URLs
	@echo "🌐 $(BLUE)EcoleHub Service URLs:$(NC)"
	@echo "   Frontend:    $(GREEN)http://localhost/$(NC)"
	@echo "   API:         $(GREEN)http://localhost/api/$(NC)"
	@echo "   Health:      $(GREEN)http://localhost/api/health$(NC)"
	@echo "   Grafana:     $(GREEN)http://localhost:3001/$(NC)"
	@echo "   Traefik:     $(GREEN)http://localhost:8080/$(NC)"
	@echo "   Prometheus:  $(GREEN)http://localhost:9090/$(NC)"
	@echo "   MinIO:       $(GREEN)http://localhost:9001/$(NC)"

accounts: ## Show test accounts
	@echo "👤 $(BLUE)Test Accounts:$(NC)"
	@echo "   Admin:     $(GREEN)admin@ecolehub.be$(NC) / admin123"
	@echo "   Direction: $(GREEN)direction@ecolehub.be$(NC) / direction123"
	@echo "   Parent:    $(GREEN)demo@example.com$(NC) / demo123"
	@echo "   Teacher:   $(GREEN)teacher@ecolehub.be$(NC) / teacher123"

version: ## Show version information
	@echo "📋 $(BLUE)EcoleHub Version Information:$(NC)"
	@echo "   Stage: 4 (Full Production)"
	@echo "   Database: PostgreSQL"
	@echo "   Cache: Redis"
	@echo "   Storage: MinIO"
	@echo "   Proxy: Traefik v3"
	@echo "   Monitoring: Grafana + Prometheus"

##@ 🧹 Maintenance

reset: ## Reset everything (DANGEROUS - will delete all data)
	@echo "⚠️  $(RED)This will delete ALL data. Are you sure?$(NC)"
	@read -p "Type 'yes' to confirm: " confirm; \
	if [ "$$confirm" = "yes" ]; then \
		echo "🗑️ $(RED)Resetting EcoleHub...$(NC)"; \
		$(COMPOSE) down -v --remove-orphans; \
		docker volume prune -f; \
		echo "✅ $(GREEN)Reset complete$(NC)"; \
	else \
		echo "❌ Reset cancelled"; \
	fi

update: ## Update and restart services
	@echo "🔄 $(BLUE)Updating EcoleHub...$(NC)"
	git pull
	$(COMPOSE) pull
	$(COMPOSE) up -d --build
	@echo "✅ $(GREEN)Update complete$(NC)"

##@ 🐛 Troubleshooting

debug: ## Show debug information
	@echo "🐛 $(BLUE)EcoleHub Debug Information:$(NC)"
	@echo ""
	@echo "$(YELLOW)Docker Compose Version:$(NC)"
	@docker compose version
	@echo ""
	@echo "$(YELLOW)Service Status:$(NC)"
	@$(COMPOSE) ps
	@echo ""
	@echo "$(YELLOW)Network Configuration:$(NC)"
	@docker network inspect schoolhub_ecolehub --format='{{range .Containers}}{{.Name}} {{end}}' 2>/dev/null || echo "Network not found"
	@echo ""
	@echo "$(YELLOW)Backend Health:$(NC)"
	@curl -s http://localhost/api/health 2>/dev/null || echo "Backend not responding"

fix-permissions: ## Fix file permissions
	@echo "🔧 $(BLUE)Fixing file permissions...$(NC)"
	chmod +x ./ecolehub
	chmod +x scripts/*.sh
	@echo "✅ $(GREEN)Permissions fixed$(NC)"

# Hidden targets (no help text)
_check-docker:
	@docker --version >/dev/null 2>&1 || (echo "❌ Docker not found" && exit 1)

_check-compose:
	@docker compose version >/dev/null 2>&1 || (echo "❌ Docker Compose not found" && exit 1)

_check-deps: _check-docker _check-compose
	@echo "✅ Dependencies OK"
##@ 🌐 Internationalization

i18n-lint: ## Scan frontend for hardcoded strings (STRICT=1 to fail on findings)
	@echo "🔎 Scanning for non-i18n strings..."
	@./scripts/i18n-lint.sh

##@ ♿ Accessibility

a11y-serve-frontend: ## Serve frontend statically on a local port (A11Y_FRONTEND_PORT=8089 by default)
	@echo "📡 Serving frontend at http://localhost:$${A11Y_FRONTEND_PORT:-8089} (Ctrl+C to stop)"
	@cd frontend && python3 -m http.server $${A11Y_FRONTEND_PORT:-8089}

a11y-audit: ## Run accessibility audit (pa11y; set BASE_URL if needed)
	@echo "♿ Running a11y audit against: $${BASE_URL:-http://localhost}"
	@./scripts/a11y-audit.sh

a11y-audit-frontend: ## Serve frontend temporarily and run a11y audit (no Docker needed)
	@echo "♿ Starting temporary frontend server and auditing..."
	@bash -c 'set -euo pipefail; \
	  PORT=$${A11Y_FRONTEND_PORT:-8089}; \
	  (cd frontend && python3 -m http.server $$PORT >/dev/null 2>&1 &) ; \
	  PID=$$!; \
	  trap "kill $$PID >/dev/null 2>&1 || true" EXIT; \
	  sleep 2; \
	  BASE_URL=http://localhost:$$PORT ./scripts/a11y-audit.sh'

a11y-playwright: ## Run Python Playwright + axe-core test (serve frontend first)
	@echo "🎭 Running Playwright a11y test..."
	@bash -c 'set -euo pipefail; \
	  PORT=$${A11Y_FRONTEND_PORT:-8089}; \
	  (cd frontend && python3 -m http.server $$PORT >/dev/null 2>&1 &) ; \
	  PID=$$!; trap "kill $$PID >/dev/null 2>&1 || true" EXIT; \
	  sleep 2; \
	  BASE_URL=http://localhost:$$PORT pytest -q tests/a11y/test_axe_playwright.py -m a11y'

##@ ✅ Tests & QA

test-all: ## Run i18n lint (STRICT) then tests
	@echo "🔎 Running i18n lint in STRICT mode..."
	@STRICT=1 ./scripts/i18n-lint.sh
	@echo "🧪 Running test suite..."
	@$(MAKE) test

ci-local: ## Run CI-like checks locally (mirrors GitHub CI)
	@./scripts/ci-local.sh

ci-local-docker: ## Build & run backend image locally (like CI docker-build-test)
	@echo "🐳 Building backend image..."
	@cd backend && docker build -t ecolehub-backend:test --build-arg STAGE=4 .
	@echo "▶️ Running container health check..."
	@docker run --rm -d --name test-backend -e DATABASE_URL=sqlite:///test.db -e STAGE=4 -p 8000:8000 ecolehub-backend:test
	@sleep 10
	@echo "ℹ️ (Optional) curl http://localhost:8000/health"
	@docker stop test-backend >/dev/null
