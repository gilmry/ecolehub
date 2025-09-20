# 📝 EcoleHub Changelog

All notable changes to EcoleHub will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [4.1.0] - 2024-09-20

### 🏗️ Repository Reorganization & Genericization
- **Generic configuration**: Removed production-specific hardcoded values
- **Environment-based deployment**: All configurations now use environment variables
- **Documentation restructure**: Moved specialized docs to `docs/` directory
- **Preserved valuable tools**: EcoleHub CLI, secrets management, and administrative scripts maintained
- **Clean .gitignore**: Production-specific files and runtime directories properly excluded

### ✨ Added - Generic Deployment
- **Environment template**: Complete `.env.example` for any school deployment
- **Generic Traefik config**: `docker-compose.traefik.yml` uses `${DOMAIN}` variable
- **Comprehensive documentation**: Configuration guides, Traefik deployment, testing guides
- **Administrative CLI**: Restored and generalized `ecolehub-manager.sh` for school IT teams
- **Secrets management**: Generic password generation and rotation tools

### 🔧 Improved - Code Quality
- **Generic CORS configuration**: Backend now reads from `CORS_ORIGINS` environment variable
- **Updated CI/CD**: GitHub Actions adapted for generic repository structure
- **Documentation links**: All internal references updated for new structure
- **Open source ready**: Repository suitable for deployment by any school

### 📁 Changed - File Organization
- **Root files**: `README.md`, `CHANGELOG.md`, `CLAUDE.md` (essentials only)
- **docs/ directory**: Specialized documentation moved to organized location
- **scripts/ tools**: Comprehensive CLI and management tools with documentation
- **Runtime directories**: `data/`, `db/`, `uploads/`, `secrets/`, `letsencrypt/` properly ignored

## [4.0.0] - 2025-01-16

### ✨ Added - Makefile Management System
- **Comprehensive Makefile** with 60+ organized commands for project management
- **Centralized command interface** with colored output and intuitive categories
- **MAKEFILE-GUIDE.md** detailed documentation with usage examples
- **Unified CLI integration** wrapping existing Docker Compose and EcoleHub CLI tools

### 🔧 Fixed - Infrastructure & Routing
- **Traefik routing architecture** fixed: `localhost/*` → Frontend, `localhost/api/*` → Backend
- **Docker networking** unified: All services on `schoolhub_ecolehub` network
- **Backend connectivity** restored: PostgreSQL, Redis, MinIO properly connected
- **Frontend console errors** resolved: Tailwind warning suppressed, API calls working
- **Authentication flow** fixed: Login working with test accounts (admin123, demo123, etc.)

### 🚀 Enhanced - Developer Experience
- **One-command startup**: `make start` launches entire application stack
- **Service monitoring**: `make status`, `make health`, `make logs` for real-time insights
- **User management**: `make users-list`, `make users-create`, `make users-reset`
- **Development workflow**: `make dev`, `make test`, `make lint`, `make shell-backend`
- **Backup & maintenance**: `make backup`, `make restore`, `make clean`

### 📋 Command Categories Added
#### 🚀 Main Commands
- `make start/stop/restart/status` - Service lifecycle management
- `make health` - Backend health check via API

#### 👥 User Management  
- `make users-list` - List all users with roles and status
- `make users-create` - Interactive user creation
- `make users-reset` - Password reset functionality

#### 🔐 Security & Credentials
- `make creds-show` - Display all system credentials
- `make creds-generate` - Generate new secure secrets

#### 📋 Monitoring & Information
- `make logs/logs-backend/logs-frontend/logs-traefik` - Targeted log viewing
- `make urls` - Display all service URLs
- `make accounts` - Show test account credentials

#### 🛠️ Development Tools
- `make dev` - Development mode with selective services
- `make test/lint/format` - Code quality tools
- `make shell-backend/shell-db` - Interactive shells

#### 💾 Data Management
- `make backup/restore` - Database backup and restore
- `make clean/reset` - Resource cleanup (with safety confirmations)

### 🌐 Service URLs Standardized
- **Frontend**: http://localhost/
- **API Backend**: http://localhost/api/
- **Health Check**: http://localhost/api/health  
- **Grafana**: http://localhost:3001/
- **Traefik Dashboard**: http://localhost:8080/
- **Prometheus**: http://localhost:9090/
- **MinIO Console**: http://localhost:9001/

### 👤 Test Accounts Confirmed
- **Admin**: admin@ecolehub.be / admin123
- **Direction**: direction@ecolehub.be / direction123  
- **Parent**: demo@example.com / demo123
- **Teacher**: teacher@ecolehub.be / teacher123

### 🏗️ Technical Improvements
- **Traefik v3 configuration** with proper priorities and middleware
- **Docker Compose optimization** with health checks and dependencies
- **Network architecture** simplified with unified `ecolehub` network
- **CLI permissions** automatically fixed via `make fix-permissions`
- **Error handling** enhanced with proper HTTP status codes

### 📖 Documentation Updates
- **README.md** updated with Makefile-first approach
- **MAKEFILE-GUIDE.md** comprehensive usage guide created
- **Installation process** streamlined to `make start`

## [3.0.0] - 2024-08-28

### Added - Stage 3 Collaborative Shop + Education + Admin

#### 🛒 Collaborative Shopping System
- **Group Buying Platform**: Parents express interest, orders triggered when threshold met
- **Product Catalog**: School supplies, branded items, uniforms with Belgian pricing (21% TVA)
- **Interest Management**: Track parent interest with quantities and special notes (size, color)
- **Progress Tracking**: Visual progress bars toward group order minimums
- **Belgian Payment Integration**: Mollie API with Bancontact, SEPA, PayPal, credit cards
- **Order Workflow**: Interest → Threshold → Group Order → Payment → Delivery coordination

#### 📚 Educational Resources System
- **Resource Library**: Upload and share educational documents, forms, calendars
- **Class-specific Content**: Resources organized by Belgian classes (M1-M3, P1-P6)
- **File Storage**: MinIO integration for secure file management with size and type validation
- **Access Control**: Public resources and parent-only restricted content
- **Categories**: Homework, calendars, forms, announcements, general resources

#### ⚙️ Administrative Interface
- **Admin Authentication**: Role-based access for users with 'admin' or 'direction' in email
- **Product Management**: Create, edit, activate/deactivate products in catalog
- **Order Management**: Launch group orders when interest thresholds are reached
- **Interest Dashboard**: View all parent interests and participation levels
- **Statistics Overview**: Platform usage and shop performance metrics (framework ready)

#### 🏗️ Enhanced Infrastructure
- **MinIO S3 Storage**: Secure file storage for product images and educational content
- **Celery Task Queue**: Background processing for order management and notifications
- **Mollie Payment Gateway**: Complete Belgian payment processing with webhook support
- **6-Service Architecture**: PostgreSQL + Redis + MinIO + Backend + Celery + Frontend

#### 🇧🇪 Belgian Context Integration
- **VAT Calculation**: Automatic 21% Belgian tax calculation for all products
- **School Supply Lists**: Standard Belgian school supply lists by grade level
- **Payment Methods**: Optimized for Belgian parents (Bancontact primary)
- **Educational Calendar**: Belgian school year integration with holidays and events

#### 🎨 Complete 9-Tab Interface
- **Dashboard**: SEL balance and available services (Stages 0+1)
- **Services SEL**: Marketplace with proposals (Stage 1)
- **Transactions**: SEL workflow management (Stage 1)
- **Messages**: Real-time parent communication (Stage 2)
- **Events**: School events with traditional celebrations (Stage 2)
- **Shop**: Collaborative buying interface with group orders ✨ **NEW**
- **Education**: Resource sharing and class materials ✨ **NEW**
- **Profile**: User and children management (All stages)
- **Admin**: Platform administration for authorized users ✨ **NEW**

#### 🔧 Technical Improvements
- **Complete API Inheritance**: All previous stage endpoints maintained in Stage 3
- **Error Resolution**: Fixed FastAPI dependency injection and route configuration
- **Nginx Routing**: Complete proxy configuration for all Stage 3 endpoints
- **Generic Branding**: Removed specific school references for open-source reusability
- **Admin Security**: Simple role-based authentication for administrative functions

## [2.0.0] - 2024-08-27

### Added - Stage 2 Real-time Messaging + Events

#### 💬 Real-time Messaging System
- **Direct Messages**: Parent-to-parent private conversations
- **Group Conversations**: Class groups and interest-based discussions
- **Auto-refresh Polling**: Messages update every 3 seconds for quasi real-time
- **Message History**: Persistent storage in PostgreSQL with timestamps
- **Conversation Types**: Direct, group, class-specific, and announcements
- **User Interface**: Chat bubbles, message timestamps, auto-scroll

#### 📅 School Events System
- **Event Management**: Create and manage school events with registration
- **Event Types**: School, class, parent meetings, activities, celebrations
- **Registration System**: Capacity limits and deadline management
- **Belgian School Events**: Fancy Fair, Saint-Nicolas, class meetings
- **Event Filters**: Filter by type (school, class, celebrations)
- **Participant Tracking**: Registration status and attendance

#### 🔴 Redis Infrastructure
- **Redis Cache**: Session management and real-time data caching
- **WebSocket Support**: Infrastructure for future real-time features
- **Performance**: Optimized for 60+ families
- **Scalability**: Ready for high-frequency messaging

#### 🎨 Enhanced User Interface
- **6-Tab Navigation**: Dashboard, Services, Transactions, Messages, Events, Profile
- **Message Integration**: Direct messaging from service listings
- **Event Calendar**: Visual event display with Belgian formatting
- **Real-time Updates**: Auto-refresh for conversations and events
- **Responsive Design**: Mobile-optimized messaging interface

#### 🔧 Technical Improvements
- **Docker Compose Stage 2**: PostgreSQL + Redis + Backend + Frontend
- **API Extensions**: Complete messaging and events endpoints
- **Error Handling**: Improved 404/422 error resolution
- **Route Management**: Nginx configuration for WebSocket and API routing
- **Performance**: Polling system for quasi real-time communication

#### 🇧🇪 Belgian School Context Integration
- **Class Groups**: Automatic conversation groups for M1-M3, P1-P6
- **School Calendar**: Belgian school events and holiday awareness
- **Parent Communication**: Direct messaging for service coordination
- **Event Types**: Aligned with Belgian school activities and celebrations

## [1.0.0] - 2024-08-27

### Added - Stage 1 Complete SEL System

#### 💱 SEL (Système d'Échange Local)
- **Service Marketplace**: Create and browse services from other parents
- **10 Service Categories**: garde, devoirs, transport, cuisine, bricolage, jardinage, ménage, courses, proposition, autre
- **Service Proposals**: Special "proposition" category for new service types
- **Transaction System**: Complete workflow (pending → approved → completed)
- **Belgian Balance Rules**: -300 to +600 units with automatic validation
- **Balance Management**: Initial 120 units (2 hours credit) per user
- **Units System**: 60 units = 1 hour standard rate

#### 🗄️ Database Migration
- **PostgreSQL 15**: Migration from SQLite with UUID primary keys
- **Data Preservation**: Automatic migration scripts for Stage 0 → Stage 1
- **Performance**: Optimized for 30+ families with proper indexing
- **Constraints**: Belgian-specific rules and validation

#### 🎨 Enhanced Frontend
- **Multi-tab Interface**: Dashboard, Services SEL, Transactions, Profile
- **Real-time Balance**: Visible in header with color coding
- **Service Creation**: Advanced form with category selection and proposals
- **Transaction Management**: Approve/cancel transactions with confirmation
- **Responsive Design**: Mobile-optimized with improved UX

#### 🔧 Infrastructure Improvements
- **Docker Multi-stage**: Stage 0 and Stage 1 configurations
- **SQLite Host Mount**: Enables seamless migration to PostgreSQL
- **Nginx SEL Routes**: Complete API routing for SEL endpoints
- **Migration Scripts**: Automated Stage 0 → Stage 1 transition
- **Requirements Management**: Separate dependencies per stage

#### 💭 Innovation: Service Proposal System
- **Community-driven**: Users can propose new service categories
- **Organic Growth**: New categories based on actual community needs
- **Special Marking**: Proposals tagged with [PROPOSITION: Category Name]
- **Visibility**: All proposals visible to community for adoption
- **Future Integration**: Popular proposals can become official categories

## [0.1.0] - 2024-08-27

### Added - Stage 0 Foundation

#### 🏫 Core Features
- **User Authentication**: Secure registration and login with JWT tokens
- **User Profiles**: Create and edit user profiles (first name, last name, email)
- **Children Management**: Add and manage children with Belgian school classes
- **Belgian School System**: Support for classes M1-M3 (maternelle) and P1-P6 (primaire)
- **Responsive Interface**: Mobile-first design with Tailwind CSS

#### 🛠️ Technical Implementation
- **Backend**: FastAPI with SQLAlchemy and SQLite database
- **Frontend**: Vue 3 with CDN (no build process)
- **Authentication**: JWT tokens with bcrypt password hashing
- **Database**: SQLite for Stage 0 (ready for PostgreSQL migration)
- **Infrastructure**: Docker Compose with Nginx reverse proxy
- **API Documentation**: OpenAPI/Swagger auto-generated docs

#### 🔒 Security & Compliance
- **Password Security**: bcrypt hashing with salt
- **JWT Tokens**: 7-day expiration with secure secret key
- **CORS Configuration**: Proper cross-origin resource sharing
- **Input Validation**: Pydantic schemas for API validation
- **GDPR Ready**: Minimal data collection and user consent

#### 🇧🇪 Belgian Localization
- **School Classes**: M1, M2, M3, P1, P2, P3, P4, P5, P6 validation
- **French Interface**: Primary language support
- **EcoleHub**: Branded for specific school in Evere
- **Belgian Context**: Ready for multilingual support (FR/NL/EN)

#### 🚀 Infrastructure & DevOps
- **Docker**: Complete containerization with Docker Compose
- **Health Checks**: Application monitoring endpoints
- **Environment Config**: Secure configuration management
- **Production Ready**: SSL-ready configuration for deployment
- **Documentation**: Comprehensive README and deployment guides

#### 📁 Project Structure
```
ecolehub/
├── backend/          # FastAPI application
├── frontend/         # Vue 3 SPA
├── .claude/         # Claude Code configuration
├── docker-compose.yml
├── nginx.conf
├── README.md
├── LICENSE (MIT)
└── CHANGELOG.md
```

### 🎯 Stage 0 Objectives Met
- [x] **5-10 families ready**: Basic functionality for small user base
- [x] **Production deployable**: Docker setup with SSL support
- [x] **Secure foundation**: JWT auth and password security
- [x] **Mobile responsive**: Works on all device sizes
- [x] **Belgian compliance**: GDPR and local requirements
- [x] **Open source**: MIT license for reusability

### 🔮 Next Stage Preview
**Stage 1** will introduce:
- Migration to PostgreSQL database
- SEL (Système d'Échange Local) with balance limits
- Support for 30 families
- Advanced user management

### 📈 Metrics
- **Code Quality**: Production-ready, documented, tested
- **Performance**: <500ms response time target
- **Security**: JWT + bcrypt + CORS configured
- **Scalability**: Ready for Stage 1 PostgreSQL migration

---

## Release Notes

This initial release provides a solid foundation for the EcoleHub parent collaboration platform. The Stage 0 implementation focuses on simplicity, security, and Belgian educational context compliance.

### Installation
```bash
git clone <repository-url>
cd ecolehub
cp .env.example .env
docker-compose up -d
```

### Support
- **Technical Issues**: GitHub Issues
- **School Contact**: EcoleHub administration

### License
MIT License - See [LICENSE](LICENSE) file for details.