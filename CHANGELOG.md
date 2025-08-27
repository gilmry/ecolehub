# Changelog

All notable changes to EcoleHub will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
- **École Notre-Dame Immaculée**: Branded for specific school in Evere
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

This initial release provides a solid foundation for the École Notre-Dame Immaculée parent collaboration platform. The Stage 0 implementation focuses on simplicity, security, and Belgian educational context compliance.

### Installation
```bash
git clone <repository-url>
cd ecolehub
cp .env.example .env
docker-compose up -d
```

### Support
- **Technical Issues**: GitHub Issues
- **School Contact**: École Notre-Dame Immaculée administration

### License
MIT License - See [LICENSE](LICENSE) file for details.