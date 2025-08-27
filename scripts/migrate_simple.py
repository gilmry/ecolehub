#!/usr/bin/env python3
"""
Migration simplifiée EcoleHub Stage 0 → Stage 1
Utilise la base SQLite sauvegardée ecolehub-stage0.db
"""

import sqlite3
import psycopg2
import uuid
from datetime import datetime

def migrate_data():
    print("🚀 Migration EcoleHub Stage 0 → Stage 1")
    print("=" * 40)
    
    # 1. Lire SQLite
    print("📖 Lecture données Stage 0...")
    conn_sqlite = sqlite3.connect('ecolehub-stage0.db')
    conn_sqlite.row_factory = sqlite3.Row
    cursor_sqlite = conn_sqlite.cursor()
    
    # Users
    cursor_sqlite.execute("SELECT * FROM users")
    users = [dict(row) for row in cursor_sqlite.fetchall()]
    
    # Children  
    cursor_sqlite.execute("SELECT * FROM children")
    children = [dict(row) for row in cursor_sqlite.fetchall()]
    
    conn_sqlite.close()
    
    print(f"   • {len(users)} utilisateurs")
    print(f"   • {len(children)} enfants")
    
    # 2. Import PostgreSQL
    print("📥 Import vers PostgreSQL...")
    conn_pg = psycopg2.connect(
        host="postgres",
        database="ecolehub", 
        user="ecolehub",
        password="ecolehub_secure_password"
    )
    cursor_pg = conn_pg.cursor()
    
    # Mapping old ID → new UUID
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
            user['hashed_password'], user['is_active'], user['created_at']
        ))
    
    # Import children
    for child in children:
        parent_uuid = user_mapping[child['parent_id']]
        cursor_pg.execute("""
            INSERT INTO children (id, parent_id, first_name, class_name, created_at)
            VALUES (%s, %s, %s, %s, %s) 
        """, (
            str(uuid.uuid4()), parent_uuid, child['first_name'],
            child['class_name'], child['created_at']
        ))
    
    # Créer balances SEL
    for old_id, new_uuid in user_mapping.items():
        cursor_pg.execute("""
            INSERT INTO sel_balances (user_id, balance, total_given, total_received)
            VALUES (%s, 120, 0, 0)
        """, (new_uuid,))
    
    conn_pg.commit()
    conn_pg.close()
    
    print(f"✅ Migration réussie !")
    print(f"   • {len(users)} utilisateurs → PostgreSQL")
    print(f"   • {len(children)} enfants → PostgreSQL") 
    print(f"   • {len(user_mapping)} balances SEL créées (120 unités)")

if __name__ == "__main__":
    migrate_data()