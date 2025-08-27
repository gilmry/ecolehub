#!/usr/bin/env python3
"""
Migration EcoleHub Stage 0 → Stage 1 depuis l'hôte
Utilise docker exec pour accéder à PostgreSQL
"""

import sqlite3
import subprocess
import json
import uuid

def run_postgres_query(query, params=None):
    """Exécute une requête PostgreSQL via docker exec."""
    if params:
        # Échapper les paramètres pour SQL
        param_str = ", ".join([f"'{p}'" if isinstance(p, str) else str(p) for p in params])
        query = query.replace('%s', '{}').format(*[f"'{p}'" if isinstance(p, str) else str(p) for p in params])
    
    cmd = [
        'docker-compose', '-f', 'docker-compose.stage1.yml', 'exec', '-T', 'postgres', 
        'psql', '-U', 'ecolehub', '-d', 'ecolehub', '-c', query
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.returncode == 0, result.stdout, result.stderr

def migrate():
    print("🚀 Migration EcoleHub Stage 0 → Stage 1")
    print("=" * 40)
    
    # 1. Lire SQLite
    sqlite_path = "db/ecolehub.db"
    if not os.path.exists(sqlite_path):
        print(f"❌ SQLite non trouvé: {sqlite_path}")
        return False
        
    print(f"📖 Lecture SQLite: {sqlite_path}")
    conn = sqlite3.connect(sqlite_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Export users
    cursor.execute("SELECT * FROM users")
    users = [dict(row) for row in cursor.fetchall()]
    
    # Export children
    cursor.execute("SELECT * FROM children")
    children = [dict(row) for row in cursor.fetchall()]
    
    conn.close()
    
    print(f"   • {len(users)} utilisateurs")
    print(f"   • {len(children)} enfants")
    
    # 2. Clear PostgreSQL data
    print("🗑️ Nettoyage PostgreSQL...")
    run_postgres_query("DELETE FROM sel_balances;")
    run_postgres_query("DELETE FROM children;")
    run_postgres_query("DELETE FROM users;")
    
    # 3. Import users
    print("📥 Import utilisateurs...")
    user_mapping = {}
    
    for user in users:
        new_uuid = str(uuid.uuid4())
        user_mapping[user['id']] = new_uuid
        
        success, _, _ = run_postgres_query("""
            INSERT INTO users (id, email, first_name, last_name, hashed_password, is_active, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (
            new_uuid, user['email'], user['first_name'], user['last_name'],
            user['hashed_password'], user['is_active'], user['created_at']
        ))
        
        if not success:
            print(f"❌ Erreur import user {user['email']}")
            return False
            
        # Créer balance SEL
        run_postgres_query("""
            INSERT INTO sel_balances (user_id, balance) VALUES (%s, 120)
        """, (new_uuid,))
    
    # 4. Import children  
    print("📥 Import enfants...")
    for child in children:
        if child['parent_id'] in user_mapping:
            success, _, _ = run_postgres_query("""
                INSERT INTO children (id, parent_id, first_name, class_name, created_at)
                VALUES (%s, %s, %s, %s, %s)
            """, (
                str(uuid.uuid4()),
                user_mapping[child['parent_id']],
                child['first_name'],
                child['class_name'], 
                child['created_at']
            ))
    
    print("✅ Migration réussie !")
    print(f"   • {len(users)} utilisateurs → PostgreSQL")
    print(f"   • {len(children)} enfants → PostgreSQL")
    print(f"   • {len(users)} balances SEL créées")
    
    # 5. Backup SQLite
    backup_path = f"{sqlite_path}.backup-migrated"
    os.rename(sqlite_path, backup_path)
    print(f"💾 Backup SQLite: {backup_path}")
    
    return True

if __name__ == "__main__":
    import os
    os.chdir("/home/user/schoolhub")
    migrate()