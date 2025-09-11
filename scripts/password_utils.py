"""
Password hashing utilities for EcoleHub CLI
Compatible with backend authentication system
"""

import os
import sys
import subprocess
import tempfile

def hash_password_via_backend(password: str) -> str:
    """
    Hash password using the backend's password hashing system
    This ensures compatibility with the login system
    """
    
    # Create a temporary Python script to run in the backend container
    hash_script = f'''
import sys
sys.path.append("/app")
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
password = "{password}"
hash_result = pwd_context.hash(password)
print(hash_result)
'''
    
    try:
        # Write script to temp file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(hash_script)
            temp_script = f.name
        
        # Execute in backend container
        result = subprocess.run([
            'docker', 'compose', '-f', 'docker-compose.stage4.yml', 
            'exec', '-T', 'backend', 'python', '-c', hash_script
        ], capture_output=True, text=True, 
        cwd=os.path.dirname(__file__) + '/..')
        
        # Clean up temp file
        os.unlink(temp_script)
        
        if result.returncode == 0:
            return result.stdout.strip()
        else:
            raise Exception(f"Password hashing failed: {result.stderr}")
            
    except Exception as e:
        print(f"❌ Failed to hash password: {e}")
        # Fallback to simple hash (not recommended for production)
        import hashlib
        return hashlib.sha256(password.encode()).hexdigest()

def verify_password_via_backend(password: str, hash_value: str) -> bool:
    """
    Verify password using the backend's password verification system
    """
    
    verify_script = f'''
import sys
sys.path.append("/app")
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
password = "{password}"
hash_value = "{hash_value}"
result = pwd_context.verify(password, hash_value)
print("True" if result else "False")
'''
    
    try:
        result = subprocess.run([
            'docker', 'compose', '-f', 'docker-compose.stage4.yml', 
            'exec', '-T', 'backend', 'python', '-c', verify_script
        ], capture_output=True, text=True,
        cwd=os.path.dirname(__file__) + '/..')
        
        if result.returncode == 0:
            return result.stdout.strip() == "True"
        else:
            return False
            
    except Exception:
        return False

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python password_utils.py <password>")
        sys.exit(1)
    
    password = sys.argv[1]
    hash_result = hash_password_via_backend(password)
    print(f"Password: {password}")
    print(f"Hash: {hash_result}")
    
    # Verify the hash works
    if verify_password_via_backend(password, hash_result):
        print("✅ Verification successful")
    else:
        print("❌ Verification failed")