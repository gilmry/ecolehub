# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

EcoleHub is an open-source school collaborative platform with progressive modular growth. The project follows a staged development approach where each stage builds upon the previous one while remaining functional independently.

### Target Context
- Generic school platform for primary schools
- Belgian school system compatible: M1-M3 (maternelle), P1-P6 (primaire), CEB in P6
- Scalable from small schools (5 families) to large ones (200+ families)
- Budget-conscious: Designed to run on affordable VPS

## Architecture Philosophy

### Stage-based Development
The project uses a progressive architecture approach across 5 stages:

- **Stage 0**: Minimal auth + profiles (SQLite, no Redis) - 5-10 families
- **Stage 1**: +SEL system (PostgreSQL) - 30 families  
- **Stage 2**: +Messaging/Events (Redis, WebSockets) - 60 families
- **Stage 3**: +Shop/Education (MinIO, Printful) - 100 families
- **Stage 4**: +Multilingual/Analytics (Full stack) - 200+ families

### Key Principles
1. **Simplicity first**: Always choose the simpler solution
2. **Progressive enhancement**: Each stage must be production-ready
3. **No technical debt**: Clean code from the start, no over-engineering
4. **Open source**: Reusable by other schools

## Technology Stack by Stage

| Stage | Backend | Frontend | Database | Infrastructure |
|-------|---------|----------|----------|----------------|
| **0** | FastAPI minimal | Vue 3 CDN | SQLite | Single server |
| **1** | +Pydantic/Alembic | Vue 3 + Vite | PostgreSQL | Docker |
| **2** | +WebSockets/Celery | +Pinia/PWA | +Redis | Docker Compose |
| **3** | +MinIO/Stripe | +i18n | +Backups | VPS 10€ |
| **4** | +Monitoring | +Analytics | +Replication | K8s ready |

## Current Implementation Status

This is a **fully implemented** repository containing:
- Complete Stage 4 implementation with all features
- Production-ready deployment configurations
- Comprehensive test suite
- Generic configuration system

The implementation includes all stages from 0 to 4 in a single unified platform.

## Development Commands

### Quick Start (Recommended)
```bash
# Configuration
cp .env.example .env
# Edit .env with your domain and passwords

# Start with Traefik (production-ready)
docker compose -f docker-compose.traefik.yml up -d

# Health check
curl https://your-domain.com/health
```

### Administrative Commands
```bash
# View logs
docker compose -f docker-compose.traefik.yml logs -f

# Database backup
docker compose exec postgres pg_dump -U ecolehub ecolehub > backup.sql

# Run tests (if configured)
make test

# Access database
docker compose exec postgres psql -U ecolehub ecolehub
```

## Project Structure (Current)

The actual project structure is:

```
schoolhub/
├── backend/
│   ├── app/
│   │   ├── main_stage4.py      # Complete Stage 4 implementation
│   │   ├── models_stage*.py    # SQLAlchemy models by stage
│   │   ├── schemas_stage*.py   # Pydantic schemas
│   │   ├── *_service.py        # Business logic services
│   │   └── workers/            # Celery async tasks
│   ├── tests/                  # Comprehensive test suite
│   └── Dockerfile
├── frontend/
│   ├── index.html              # Complete Vue.js SPA
│   └── locales/                # i18n translations
├── monitoring/
│   ├── prometheus.yml          # Metrics configuration
│   └── grafana/                # Dashboard configurations
├── scripts/
│   └── init_stage*.sql         # Database initialization
├── docker-compose.traefik.yml  # Production configuration
├── .env.example                # Configuration template
└── archive/                    # Production-specific files (ignored)
```

## Belgian-Specific Configuration

### Classes System
- Maternelle: M1, M2, M3
- Primaire: P1, P2, P3, P4, P5, P6
- CEB certification at P6 level

### Localization
- Primary: French (fr-BE)
- Secondary: Dutch (nl-BE) 
- Optional: English (en)

### Payments (Stage 3+)
- Mollie integration (supports Bancontact)
- Belgian tax compliance

## Stage Migration

Each stage has migration scripts to upgrade from the previous stage:
- `scripts/migrate_to_stage1.py` - SQLite to PostgreSQL
- `scripts/upgrade-stage.sh` - General stage upgrader
- Database schemas preserved during migrations
- No data loss during upgrades

## SEL (Local Exchange System) Rules

For Stage 1+ implementation:
- Initial balance: 120 units (2 hours)
- Minimum balance: -300 units 
- Maximum balance: +600 units
- 1 hour = 60 units standard rate

## Development Workflow

1. **Always start with Stage 0** - must be 100% functional before proceeding
2. **One stage at a time** - complete current stage before planning next
3. **Keep migrations working** - never break upgrade path
4. **Test on 5-10 families** before expanding
5. **Document everything** - other schools will use this

## Important Notes

- **No over-engineering** in early stages
- **Production-ready from Stage 0** - must work with real families
- **GDPR compliance** from the start (Belgian requirements)
- **Open source** - clean, documented, reusable code
- **Progressive enhancement** - each stage adds value without breaking previous functionality