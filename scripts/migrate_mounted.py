#!/usr/bin/env python3
"""
Migration EcoleHub: SQLite (monté) → PostgreSQL
"""

import sqlite3
import psycopg2
import uuid
import os

def migrate():
    print("🚀 Migration EcoleHub: SQLite → PostgreSQL")
    
    # 1. Lire SQLite depuis le mount
    sqlite_path = "/app/db/ecolehub.db"
    if not os.path.exists(sqlite_path):
        print(f"❌ SQLite non trouvé: {sqlite_path}")
        return False
    
    print(f"📖 Lecture SQLite: {sqlite_path}")
    conn_sqlite = sqlite3.connect(sqlite_path)
    conn_sqlite.row_factory = sqlite3.Row
    cursor_sqlite = conn_sqlite.cursor()
    
    # Lire users
    cursor_sqlite.execute("SELECT * FROM users")
    users = [dict(row) for row in cursor_sqlite.fetchall()]
    
    # Lire children
    cursor_sqlite.execute("SELECT * FROM children") 
    children = [dict(row) for row in cursor_sqlite.fetchall()]
    
    conn_sqlite.close()
    
    print(f"   • {len(users)} utilisateurs")
    print(f"   • {len(children)} enfants")
    
    # 2. Import PostgreSQL
    print("📥 Import PostgreSQL...")
    
    # Nettoyer les tables existantes
    conn_pg = psycopg2.connect(
        host="postgres",
        database="ecolehub",
        user="ecolehub", 
        password=os.getenv("DB_PASSWORD", "ecolehub_secure_password")
    )
    cursor_pg = conn_pg.cursor()
    
    # Clear existing data
    cursor_pg.execute("DELETE FROM sel_balances")
    cursor_pg.execute("DELETE FROM children") 
    cursor_pg.execute("DELETE FROM users")
    
    # Mapping SQLite ID → PostgreSQL UUID
    user_mapping = {}
    
    # Import users
    for user in users:
        new_uuid = str(uuid.uuid4())
        user_mapping[user['id']] = new_uuid
        
        cursor_pg.execute("""
            INSERT INTO users (id, email, first_name, last_name, hashed_password, is_active, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (
            new_uuid, user['email'], user['first_name'], user['last_name'],
            user['hashed_password'], bool(user['is_active']), user['created_at']
        ))
        
        # Créer balance SEL pour chaque utilisateur
        cursor_pg.execute("""
            INSERT INTO sel_balances (user_id, balance)
            VALUES (%s, 120)
        """, (new_uuid,))
    
    # Import children
    for child in children:
        if child['parent_id'] in user_mapping:
            cursor_pg.execute("""
                INSERT INTO children (id, parent_id, first_name, class_name, created_at)
                VALUES (%s, %s, %s, %s, %s)
            """, (
                str(uuid.uuid4()),
                user_mapping[child['parent_id']], 
                child['first_name'],
                child['class_name'],
                child['created_at']
            ))
    
    conn_pg.commit()
    conn_pg.close()
    
    print("✅ Migration terminée !")
    print(f"   • {len(users)} utilisateurs migrés")
    print(f"   • {len(children)} enfants migrés") 
    print(f"   • {len(users)} balances SEL créées (120 unités chacune)")
    
    return True

if __name__ == "__main__":
    migrate()