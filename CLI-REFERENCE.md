# 🏫 EcoleHub CLI - Quick Reference

The EcoleHub CLI provides comprehensive credential and account management for the Belgian school collaborative platform.

## 🚀 Quick Start

```bash
# Make CLI executable (if needed)
chmod +x ./ecolehub

# Show help
./ecolehub help

# List all users
./ecolehub users list

# Show all credentials
./ecolehub creds show

# Check service status
./ecolehub services status
```

## 👥 User Management

### List Users
```bash
# List all users
./ecolehub users list

# List only parents (limit 10)
./ecolehub users list parent 10

# List admins
./ecolehub users list admin
```

### Create Users
```bash
# Create user with auto-generated password
./ecolehub users create "john@school.be" "John" "Doe"

# Create admin user with specific password
./ecolehub users create "admin@school.be" "Admin" "User" "mypassword123" "admin"

# Create teacher
./ecolehub users create "teacher@school.be" "Marie" "Dupont" "" "direction"
```

### Manage Users
```bash
# Reset password (auto-generated)
./ecolehub users reset-password "user@example.com"

# Reset with specific password
./ecolehub users reset-password "user@example.com" "newpassword123"

# Deactivate user
./ecolehub users deactivate "spam@example.com"

# Activate user
./ecolehub users activate "user@example.com"
```

## 🔐 Credential Management

### Show Credentials
```bash
# Display all service credentials
./ecolehub creds show
./ecolehub creds list    # Same as show
```

### Generate New Secrets
```bash
# Generate secure credentials for production
./ecolehub creds generate

# This creates .env.secrets.new with:
# - New SECRET_KEY
# - New database passwords
# - New Redis password
# - New MinIO credentials
# - New Grafana password
```

## 🐳 Service Management

### Service Status
```bash
# Show all service status
./ecolehub services status
```

### Restart Services
```bash
# Restart specific service
./ecolehub services restart backend
./ecolehub services restart frontend
./ecolehub services restart postgres
./ecolehub services restart redis
```

## 🎭 User Roles

- **parent** (default): Regular family user
- **admin**: Full platform access, analytics, user management
- **direction**: School management, announcements, events

## 📊 Current Credentials

### Application Access
- **Frontend**: http://localhost
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

### 👥 Ready-to-Use Test Accounts

| Role | Email | Password | Name/Description |
|------|-------|----------|------------------|
| **Parent** | demo@example.com | demo123 | Demo User |
| **Parent** | parent1@example.be | parent123 | Marie Dupont |
| **Parent** | parent2@example.be | parent123 | Jean Martin |
| **Parent** | test@example.com | test123 | Test User |
| **Admin** | teacher@ecolehub.be | teacher123 | Marie Professor |
| **Admin** | admin@ecolehub.be | admin123 | Admin EcoleHub |
| **Direction** | direction@ecolehub.be | direction123 | Direction EcoleHub |

### 🎭 Role Capabilities
- **Parent**: SEL services, messaging, events, shop interests, education resources
- **Admin**: Full platform access, analytics, user management, system configuration  
- **Direction**: School management, official announcements, event creation, platform oversight

### Services
- **Database**: localhost:5432 (ecolehub/ecolehub_secure_password)
- **Redis**: localhost:6379 (redis_secure_password)  
- **MinIO**: http://localhost:9001 (ecolehub_minio/minio_secure_password)
- **Grafana**: http://localhost:3001 (admin/admin_ecolehub_monitoring)
- **Prometheus**: http://localhost:9090

## ⚠️ Security Notes

1. **Easy Testing Passwords**: All test accounts use simple passwords (demo123, admin123, etc.) for easy development and testing
2. **Change default passwords** in production
3. **Use strong passwords** for all accounts in production
4. **Store generated passwords** securely
5. **Regularly rotate credentials**
6. **Monitor user access** and deactivate unused accounts

### 🧪 Testing Quick Reference
- **Parent role testing**: demo@example.com / demo123
- **Admin role testing**: admin@ecolehub.be / admin123  
- **Direction role testing**: direction@ecolehub.be / direction123

## 🆘 Troubleshooting

### CLI Issues
```bash
# Check Docker is running
docker --version
docker compose version

# Check services are running
./ecolehub services status

# Check database connectivity
docker compose -f docker-compose.stage4.yml exec postgres psql -U ecolehub -d ecolehub -c "SELECT 1;"
```

### Permission Issues
```bash
# Make CLI executable
chmod +x ./ecolehub
chmod +x ./scripts/ecolehub-manager.sh
```

### Password Issues
- If password hashing fails, ensure backend container is running
- Use `./ecolehub services restart backend` if needed
- Generated passwords are 12 characters by default

## 📱 Examples

### Setup New School
```bash
# Create admin account
./ecolehub users create "direction@school.be" "Director" "Name" "secure123" "direction"

# Create teacher accounts  
./ecolehub users create "teacher1@school.be" "Marie" "Dupont" "" "admin"
./ecolehub users create "teacher2@school.be" "Jean" "Martin" "" "direction"

# Reset existing account passwords for fresh start
./ecolehub users reset-password admin@ecolehub.be
./ecolehub users reset-password direction@ecolehub.be

# Generate production credentials
./ecolehub creds generate

# Check everything is running
./ecolehub services status
```

### User Maintenance
```bash
# List inactive users
./ecolehub users list | grep ❌

# Reset password for forgotten credentials
./ecolehub users reset-password "parent@school.be"

# Clean up spam accounts
./ecolehub users deactivate "spam@example.com"
```

---

**EcoleHub CLI v1.0** - Belgian School Collaborative Platform  
For more information: https://github.com/ecolehub/ecolehub