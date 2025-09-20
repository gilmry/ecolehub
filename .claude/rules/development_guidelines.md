# EcoleHub Development Guidelines

## General Principles

### 1. Simplicity First
- Always choose the simplest working solution
- Don't over-engineer for future requirements
- One working file is better than complex architecture

### 2. Production Ready
- Every line of code must be deployable
- HTTPS required for all deployments
- Proper error handling and validation
- GDPR compliant by default

### 3. Configuration Management
- Use environment variables for all configuration
- Generic configuration via `.env.example`
- No hardcoded domain names or secrets
- Document all configuration options

## Technical Guidelines

### Backend (FastAPI)
- Use existing Stage 4 implementation (`main_stage4.py`) as reference
- API endpoints prefixed with `/api/`
- SQLAlchemy models for database
- Pydantic schemas for validation
- JWT authentication

### Frontend (Vue.js)
- Single-page application in `index.html`
- Vue 3 with Composition API
- Tailwind CSS for styling
- API calls to `/api/*` endpoints

### Database
- PostgreSQL for production
- Use existing models and migrations
- Backup procedures documented

### Deployment
- Docker Compose with Traefik
- Let's Encrypt for SSL certificates
- Environment-based configuration
- Health checks for all services

## Code Quality

### Testing
- Use existing test suite as reference
- Unit tests for business logic
- Integration tests for API endpoints
- Test coverage reporting available

### Documentation
- Update README.md for user-facing changes
- Update CONFIGURATION-GUIDE.md for deployment changes
- Comment complex business logic
- Keep Claude instructions up to date

## Security

### Authentication
- JWT tokens for API access
- Role-based access control (admin/parent)
- Secure password hashing (bcrypt)

### Data Protection
- GDPR compliant data handling
- Input validation and sanitization
- SQL injection prevention
- XSS protection

### Infrastructure
- Private networks for internal services
- Only frontend and API publicly accessible
- SSL/TLS encryption everywhere
- Regular security updates