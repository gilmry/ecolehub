#!/usr/bin/env python3
"""
EcoleHub CLI - Credential and Account Management Tool
Open-source school collaborative platform administration
"""

import os
import sys
import argparse
import json
import subprocess
import getpass
from typing import Dict, List, Optional
import psycopg2
from psycopg2.extras import RealDictCursor
import hashlib
import secrets
import string

class EcoleHubCLI:
    def __init__(self):
        self.load_config()
        self.db_connection = None
    
    def load_config(self):
        """Load configuration from environment or .env file"""
        env_file = os.path.join(os.path.dirname(__file__), '..', '.env')
        if os.path.exists(env_file):
            with open(env_file, 'r') as f:
                for line in f:
                    if '=' in line and not line.strip().startswith('#'):
                        key, value = line.strip().split('=', 1)
                        os.environ[key] = value
        
        self.config = {
            'db_host': os.getenv('DB_HOST', 'localhost'),
            'db_port': os.getenv('DB_PORT', '5432'),
            'db_name': os.getenv('DB_NAME', 'ecolehub'),
            'db_user': os.getenv('DB_USER', 'ecolehub'),
            'db_password': os.getenv('DB_PASSWORD', 'ecolehub_secure_password'),
            'redis_url': os.getenv('REDIS_URL', 'redis://:redis_secure_password@localhost:6379/0'),
            'minio_access_key': os.getenv('MINIO_ACCESS_KEY', 'ecolehub_minio'),
            'minio_secret_key': os.getenv('MINIO_SECRET_KEY', 'minio_secure_password'),
            'grafana_password': os.getenv('GRAFANA_PASSWORD', 'admin_ecolehub_monitoring'),
            'secret_key': os.getenv('SECRET_KEY', 'change-this-in-production-very-important'),
        }
    
    def connect_db(self):
        """Connect to PostgreSQL database"""
        if not self.db_connection:
            try:
                self.db_connection = psycopg2.connect(
                    host=self.config['db_host'],
                    port=self.config['db_port'],
                    database=self.config['db_name'],
                    user=self.config['db_user'],
                    password=self.config['db_password'],
                    cursor_factory=RealDictCursor
                )
            except psycopg2.Error as e:
                print(f"❌ Database connection failed: {e}")
                sys.exit(1)
        return self.db_connection
    
    def hash_password(self, password: str) -> str:
        """Hash password using backend-compatible bcrypt"""
        try:
            # Use the backend's password hashing system
            from password_utils import hash_password_via_backend
            return hash_password_via_backend(password)
        except ImportError:
            # Fallback method if password_utils is not available
            import subprocess
            
            hash_script = f'''
import sys
sys.path.append("/app")
from passlib.context import CryptContext
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
print(pwd_context.hash("{password}"))
'''
            
            try:
                result = subprocess.run([
                    'docker', 'compose', '-f', 'docker-compose.stage4.yml', 
                    'exec', '-T', 'backend', 'python', '-c', hash_script
                ], capture_output=True, text=True, 
                cwd=os.path.dirname(__file__) + '/..')
                
                if result.returncode == 0:
                    return result.stdout.strip()
                else:
                    raise Exception("Backend hashing failed")
            except Exception as e:
                print(f"⚠️  Warning: Using fallback password hashing: {e}")
                # Simple fallback (not secure for production)
                import hashlib
                return f"fallback_{hashlib.sha256(password.encode()).hexdigest()}"
    
    def generate_password(self, length: int = 12) -> str:
        """Generate secure random password"""
        alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
        return ''.join(secrets.choice(alphabet) for i in range(length))

class UserManager(EcoleHubCLI):
    """User account management commands"""
    
    def list_users(self, role: Optional[str] = None, limit: int = 20):
        """List all users with optional role filter"""
        conn = self.connect_db()
        cursor = conn.cursor()
        
        query = "SELECT email, first_name, last_name, role, is_active, created_at FROM users"
        params = []
        
        if role:
            query += " WHERE role = %s"
            params.append(role)
        
        query += " ORDER BY created_at DESC LIMIT %s"
        params.append(limit)
        
        cursor.execute(query, params)
        users = cursor.fetchall()
        
        if not users:
            print("👥 No users found")
            return
        
        print(f"👥 EcoleHub Users ({len(users)} found)")
        print("-" * 80)
        print(f"{'Email':<30} {'Name':<25} {'Role':<12} {'Active':<8} {'Created'}")
        print("-" * 80)
        
        for user in users:
            status = "✅" if user['is_active'] else "❌"
            created = user['created_at'].strftime('%Y-%m-%d')
            name = f"{user['first_name']} {user['last_name']}"
            print(f"{user['email']:<30} {name:<25} {user['role']:<12} {status:<8} {created}")
    
    def create_user(self, email: str, first_name: str, last_name: str, 
                   password: Optional[str] = None, role: str = "parent"):
        """Create a new user account"""
        if not password:
            password = self.generate_password()
            generated = True
        else:
            generated = False
        
        hashed_password = self.hash_password(password)
        
        conn = self.connect_db()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                INSERT INTO users (email, first_name, last_name, hashed_password, role, is_active)
                VALUES (%s, %s, %s, %s, %s, true)
                RETURNING id, email
            """, (email, first_name, last_name, hashed_password, role))
            
            user = cursor.fetchone()
            conn.commit()
            
            print(f"✅ User created successfully!")
            print(f"   📧 Email: {user['email']}")
            print(f"   👤 Name: {first_name} {last_name}")
            print(f"   🎭 Role: {role}")
            if generated:
                print(f"   🔑 Password: {password}")
                print(f"   ⚠️  Please share this password securely!")
            
        except psycopg2.IntegrityError:
            conn.rollback()
            print(f"❌ User with email {email} already exists!")
        except psycopg2.Error as e:
            conn.rollback()
            print(f"❌ Failed to create user: {e}")
    
    def reset_password(self, email: str, new_password: Optional[str] = None):
        """Reset user password"""
        if not new_password:
            new_password = self.generate_password()
            generated = True
        else:
            generated = False
        
        hashed_password = self.hash_password(new_password)
        
        conn = self.connect_db()
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE users SET hashed_password = %s, updated_at = NOW()
            WHERE email = %s
            RETURNING email, first_name, last_name
        """, (hashed_password, email))
        
        user = cursor.fetchone()
        
        if user:
            conn.commit()
            print(f"✅ Password reset successful!")
            print(f"   📧 Email: {user['email']}")
            print(f"   👤 Name: {user['first_name']} {user['last_name']}")
            if generated:
                print(f"   🔑 New Password: {new_password}")
                print(f"   ⚠️  Please share this password securely!")
        else:
            print(f"❌ User with email {email} not found!")
    
    def deactivate_user(self, email: str):
        """Deactivate user account"""
        conn = self.connect_db()
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE users SET is_active = false, updated_at = NOW()
            WHERE email = %s
            RETURNING email, first_name, last_name
        """, (email,))
        
        user = cursor.fetchone()
        
        if user:
            conn.commit()
            print(f"⏸️  User deactivated: {user['first_name']} {user['last_name']} ({user['email']})")
        else:
            print(f"❌ User with email {email} not found!")
    
    def activate_user(self, email: str):
        """Activate user account"""
        conn = self.connect_db()
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE users SET is_active = true, updated_at = NOW()
            WHERE email = %s
            RETURNING email, first_name, last_name
        """, (email,))
        
        user = cursor.fetchone()
        
        if user:
            conn.commit()
            print(f"✅ User activated: {user['first_name']} {user['last_name']} ({user['email']})")
        else:
            print(f"❌ User with email {email} not found!")

class CredentialManager(EcoleHubCLI):
    """Service credential management"""
    
    def show_all_credentials(self):
        """Display all service credentials"""
        print("🔐 EcoleHub Stage 4 - Service Credentials")
        print("=" * 60)
        
        # Database
        print("\n📊 DATABASE (PostgreSQL)")
        print(f"  Host: {self.config['db_host']}:{self.config['db_port']}")
        print(f"  Database: {self.config['db_name']}")
        print(f"  Username: {self.config['db_user']}")
        print(f"  Password: {self.config['db_password']}")
        
        # Redis
        print(f"\n🗄️  CACHE (Redis)")
        print(f"  URL: {self.config['redis_url']}")
        redis_password = self.config['redis_url'].split('@')[0].split(':')[-1]
        print(f"  Password: {redis_password}")
        
        # MinIO
        print(f"\n📦 STORAGE (MinIO)")
        print(f"  Console: http://localhost:9001")
        print(f"  API: http://localhost:9000")
        print(f"  Access Key: {self.config['minio_access_key']}")
        print(f"  Secret Key: {self.config['minio_secret_key']}")
        
        # Monitoring
        print(f"\n📈 MONITORING")
        print(f"  Grafana: http://localhost:3001")
        print(f"  Username: admin")
        print(f"  Password: {self.config['grafana_password']}")
        print(f"  Prometheus: http://localhost:9090")
        
        # Application
        print(f"\n🏫 APPLICATION")
        print(f"  Frontend: http://localhost")
        print(f"  Backend API: http://localhost:8000")
        print(f"  API Docs: http://localhost:8000/docs")
        print(f"  Secret Key: {self.config['secret_key'][:20]}...")
    
    def generate_new_secrets(self):
        """Generate new secure secrets for production"""
        print("🔐 Generating new secure credentials...")
        
        new_secrets = {
            'SECRET_KEY': secrets.token_urlsafe(64),
            'DB_PASSWORD': self.generate_password(16),
            'REDIS_PASSWORD': self.generate_password(16),
            'MINIO_SECRET_KEY': self.generate_password(20),
            'GRAFANA_PASSWORD': self.generate_password(12)
        }
        
        print("\n✅ New secure credentials generated:")
        print("-" * 50)
        for key, value in new_secrets.items():
            print(f"{key}={value}")
        
        # Write to .env.secrets file
        secrets_file = os.path.join(os.path.dirname(__file__), '..', '.env.secrets.new')
        with open(secrets_file, 'w') as f:
            f.write("# EcoleHub - New Generated Secrets\n")
            f.write("# Generated on: " + str(__import__('datetime').datetime.now()) + "\n\n")
            for key, value in new_secrets.items():
                f.write(f"{key}={value}\n")
        
        print(f"\n💾 Secrets saved to: {secrets_file}")
        print("⚠️  IMPORTANT: Update your .env file and restart services!")

class ServiceManager(EcoleHubCLI):
    """Docker service management"""
    
    def status(self):
        """Show status of all services"""
        try:
            result = subprocess.run([
                'docker', 'compose', '-f', 'docker-compose.stage4.yml', 'ps'
            ], capture_output=True, text=True, cwd=os.path.dirname(__file__) + '/..')
            
            if result.returncode == 0:
                print("🐳 EcoleHub Services Status")
                print("-" * 50)
                print(result.stdout)
            else:
                print(f"❌ Failed to get service status: {result.stderr}")
        except FileNotFoundError:
            print("❌ Docker or docker-compose not found!")
    
    def restart_service(self, service: str):
        """Restart specific service"""
        try:
            result = subprocess.run([
                'docker', 'compose', '-f', 'docker-compose.stage4.yml', 'restart', service
            ], capture_output=True, text=True, cwd=os.path.dirname(__file__) + '/..')
            
            if result.returncode == 0:
                print(f"🔄 Service '{service}' restarted successfully")
            else:
                print(f"❌ Failed to restart service '{service}': {result.stderr}")
        except FileNotFoundError:
            print("❌ Docker or docker-compose not found!")

def main():
    parser = argparse.ArgumentParser(
        description="EcoleHub CLI - Credential and Account Management",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # User Management
  %(prog)s users list                          # List all users
  %(prog)s users create john@example.com "John" "Doe"  # Create user
  %(prog)s users reset-password admin@ecolehub.be      # Reset password
  %(prog)s users deactivate spam@example.com           # Deactivate user
  
  # Credentials
  %(prog)s creds show                          # Show all credentials
  %(prog)s creds generate                      # Generate new secrets
  
  # Services
  %(prog)s services status                     # Show service status
  %(prog)s services restart backend           # Restart specific service
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # User management commands
    users_parser = subparsers.add_parser('users', help='User account management')
    users_subparsers = users_parser.add_subparsers(dest='user_action')
    
    # List users
    list_parser = users_subparsers.add_parser('list', help='List users')
    list_parser.add_argument('--role', help='Filter by role (parent, admin, direction)')
    list_parser.add_argument('--limit', type=int, default=20, help='Limit results')
    
    # Create user
    create_parser = users_subparsers.add_parser('create', help='Create new user')
    create_parser.add_argument('email', help='User email')
    create_parser.add_argument('first_name', help='First name')
    create_parser.add_argument('last_name', help='Last name')
    create_parser.add_argument('--password', help='Password (auto-generated if not provided)')
    create_parser.add_argument('--role', default='parent', choices=['parent', 'admin', 'direction'])
    
    # Reset password
    reset_parser = users_subparsers.add_parser('reset-password', help='Reset user password')
    reset_parser.add_argument('email', help='User email')
    reset_parser.add_argument('--password', help='New password (auto-generated if not provided)')
    
    # Deactivate user
    deactivate_parser = users_subparsers.add_parser('deactivate', help='Deactivate user')
    deactivate_parser.add_argument('email', help='User email')
    
    # Activate user
    activate_parser = users_subparsers.add_parser('activate', help='Activate user')
    activate_parser.add_argument('email', help='User email')
    
    # Credential management commands
    creds_parser = subparsers.add_parser('creds', help='Credential management')
    creds_subparsers = creds_parser.add_subparsers(dest='cred_action')
    
    creds_subparsers.add_parser('show', help='Show all service credentials')
    creds_subparsers.add_parser('generate', help='Generate new secure secrets')
    
    # Service management commands
    services_parser = subparsers.add_parser('services', help='Service management')
    services_subparsers = services_parser.add_subparsers(dest='service_action')
    
    services_subparsers.add_parser('status', help='Show service status')
    restart_parser = services_subparsers.add_parser('restart', help='Restart service')
    restart_parser.add_argument('service', help='Service name to restart')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # Execute commands
    if args.command == 'users':
        user_mgr = UserManager()
        
        if args.user_action == 'list':
            user_mgr.list_users(args.role, args.limit)
        elif args.user_action == 'create':
            user_mgr.create_user(args.email, args.first_name, args.last_name, args.password, args.role)
        elif args.user_action == 'reset-password':
            user_mgr.reset_password(args.email, args.password)
        elif args.user_action == 'deactivate':
            user_mgr.deactivate_user(args.email)
        elif args.user_action == 'activate':
            user_mgr.activate_user(args.email)
        else:
            users_parser.print_help()
    
    elif args.command == 'creds':
        cred_mgr = CredentialManager()
        
        if args.cred_action == 'show':
            cred_mgr.show_all_credentials()
        elif args.cred_action == 'generate':
            cred_mgr.generate_new_secrets()
        else:
            creds_parser.print_help()
    
    elif args.command == 'services':
        svc_mgr = ServiceManager()
        
        if args.service_action == 'status':
            svc_mgr.status()
        elif args.service_action == 'restart':
            svc_mgr.restart_service(args.service)
        else:
            services_parser.print_help()

if __name__ == '__main__':
    main()