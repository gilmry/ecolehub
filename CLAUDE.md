# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

EcoleHub is a Belgian school collaborative platform with progressive modular growth. The project follows a staged development approach where each stage builds upon the previous one while remaining functional independently.

### Target Context
- École Notre-Dame Immaculée (Catholic primary school in Evere, Brussels)  
- Belgian school system: M1-M3 (maternelle), P1-P6 (primaire), CEB in P6
- Progressive growth from 5 families (Stage 0) to 200+ families (Stage 4)
- Budget constraint: Max 10€/month VPS

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

## Current Stage Implementation

Based on the codebase analysis, this is currently a **planning/documentation phase** repository containing:
- Technical specification document (`schoolhub-unified-technical.md`)
- Implementation prompt (`prompt.txt`)

The actual implementation should follow the staged approach outlined in the documentation.

## Development Commands

Since no actual implementation exists yet, here are the commands that will be used once development starts:

### Stage 0 Development (Target)
```bash
# Backend
cd backend
pip install -r requirements-stage0.txt
python app/main.py

# Frontend (Stage 0 uses HTML + CDN)
# Serve static files via nginx or python -m http.server

# Docker deployment
docker-compose -f docker-compose.stage0.yml up

# Database (SQLite - no migrations needed for Stage 0)
# SQLite file: backend/schoolhub.db

# Health check
curl http://localhost:8000/health
```

### Future Stage Commands
```bash
# Stage migration
./scripts/upgrade-stage.sh 1

# PostgreSQL migrations (Stage 1+)
docker-compose exec backend alembic upgrade head

# SEL module activation
docker-compose exec backend python scripts/enable_module.py sel

# Tests (Stage 1+)
docker-compose exec backend pytest tests/

# Backup
docker-compose exec postgres pg_dump -U schoolhub schoolhub > backup.sql
```

## Project Structure (Target)

Based on the technical specification, the project structure will be:

```
schoolhub/
├── backend/
│   ├── app/
│   │   ├── api/v1/endpoints/    # Stage-specific endpoints
│   │   ├── core/                # Config, security, database
│   │   ├── models/              # SQLAlchemy models per stage
│   │   ├── schemas/             # Pydantic schemas
│   │   ├── services/            # Business logic
│   │   └── main.py             # FastAPI application
│   ├── scripts/                # Migration and setup scripts
│   ├── requirements-stageX.txt # Stage-specific dependencies
│   └── Dockerfile
├── frontend/
│   ├── src/modules/            # Aligned with backend stages
│   ├── public/
│   └── package.json           # From Stage 1+
├── docker/
│   ├── nginx/
│   ├── postgres/
│   └── redis/
└── scripts/                   # Deployment and migration scripts
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