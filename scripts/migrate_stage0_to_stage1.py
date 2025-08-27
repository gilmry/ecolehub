#!/usr/bin/env python3
"""
Migration Script: EcoleHub Stage 0 → Stage 1
Migre les données SQLite vers PostgreSQL et ajoute le système SEL.
"""

import sqlite3
import psycopg2
import json
import os
from datetime import datetime
from passlib.context import CryptContext
import uuid

def migrate_stage0_to_stage1():
    """
    Migration complète Stage 0 → Stage 1
    1. Export données SQLite
    2. Import vers PostgreSQL  
    3. Création balances SEL initiales
    """
    print("🚀 Migration EcoleHub Stage 0 → Stage 1")
    print("=" * 50)
    
    # Configuration
    sqlite_db = "backend/app/schoolhub.db"  # ou ecolehub.db
    if not os.path.exists(sqlite_db):
        sqlite_db = "backend/app/ecolehub.db"
    
    if not os.path.exists(sqlite_db):
        print("❌ Aucune base SQLite trouvée. Stage 0 déjà migré ?")
        return False
    
    pg_config = {
        'host': os.getenv('POSTGRES_HOST', 'localhost'),
        'database': 'ecolehub',
        'user': 'ecolehub', 
        'password': os.getenv('DB_PASSWORD', 'ecolehub_secure_password')
    }
    
    print(f"📁 SQLite source: {sqlite_db}")
    print(f"🐘 PostgreSQL target: {pg_config['host']}/{pg_config['database']}")
    print()
    
    try:
        # 1. Export depuis SQLite
        print("📤 Export données SQLite...")
        sqlite_data = export_from_sqlite(sqlite_db)
        print(f"   • {len(sqlite_data['users'])} utilisateurs")
        print(f"   • {len(sqlite_data['children'])} enfants")
        
        # 2. Import vers PostgreSQL
        print("📥 Import vers PostgreSQL...")
        import_to_postgresql(sqlite_data, pg_config)
        
        # 3. Backup SQLite
        backup_path = f"{sqlite_db}.backup-{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        os.rename(sqlite_db, backup_path)
        print(f"💾 Backup SQLite: {backup_path}")
        
        print()
        print("✅ Migration Stage 0 → Stage 1 réussie !")
        print("🎯 Prochaine étape : Utiliser docker-compose.stage1.yml")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur migration: {e}")
        return False

def export_from_sqlite(db_path):
    """Export toutes les données depuis SQLite."""
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    data = {"users": [], "children": []}
    
    # Export users
    cursor.execute("SELECT * FROM users")
    for row in cursor.fetchall():
        data["users"].append({
            "id": row["id"],
            "email": row["email"],
            "first_name": row["first_name"],
            "last_name": row["last_name"],
            "hashed_password": row["hashed_password"],
            "is_active": row["is_active"],
            "created_at": row["created_at"]
        })
    
    # Export children
    cursor.execute("SELECT * FROM children")
    for row in cursor.fetchall():
        data["children"].append({
            "id": row["id"],
            "parent_id": row["parent_id"],
            "first_name": row["first_name"],
            "class_name": row["class_name"],
            "created_at": row["created_at"]
        })
    
    conn.close()
    return data

def import_to_postgresql(data, pg_config):
    """Import données vers PostgreSQL avec UUIDs."""
    conn = psycopg2.connect(**pg_config)
    cursor = conn.cursor()
    
    # Mapping SQLite ID → PostgreSQL UUID
    user_id_mapping = {}
    
    print("   • Import utilisateurs...")
    
    # Import users avec nouveaux UUIDs
    for user in data["users"]:
        new_uuid = str(uuid.uuid4())
        user_id_mapping[user["id"]] = new_uuid
        
        cursor.execute("""
            INSERT INTO users (id, email, first_name, last_name, hashed_password, is_active, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (
            new_uuid,
            user["email"],
            user["first_name"], 
            user["last_name"],
            user["hashed_password"],
            user["is_active"],
            user["created_at"]
        ))
    
    print("   • Import enfants...")
    
    # Import children avec UUIDs mappés
    for child in data["children"]:
        if child["parent_id"] in user_id_mapping:
            cursor.execute("""
                INSERT INTO children (id, parent_id, first_name, class_name, created_at)
                VALUES (%s, %s, %s, %s, %s)
            """, (
                str(uuid.uuid4()),
                user_id_mapping[child["parent_id"]],
                child["first_name"],
                child["class_name"],
                child["created_at"]
            ))
    
    print("   • Création balances SEL initiales...")
    
    # Créer balances SEL pour tous les utilisateurs
    for old_id, new_uuid in user_id_mapping.items():
        cursor.execute("""
            INSERT INTO sel_balances (user_id, balance, total_given, total_received)
            VALUES (%s, 120, 0, 0)
        """, (new_uuid,))
    
    conn.commit()
    conn.close()
    
    print(f"   • {len(data['users'])} utilisateurs migrés")
    print(f"   • {len(data['children'])} enfants migrés")
    print(f"   • {len(user_id_mapping)} balances SEL créées")

def test_migration():
    """Test basique de la migration."""
    try:
        # Test connexion PostgreSQL
        pg_config = {
            'host': os.getenv('POSTGRES_HOST', 'localhost'),
            'database': 'ecolehub',
            'user': 'ecolehub',
            'password': os.getenv('DB_PASSWORD', 'ecolehub_secure_password')
        }
        
        conn = psycopg2.connect(**pg_config)
        cursor = conn.cursor()
        
        # Compter les données migrées
        cursor.execute("SELECT COUNT(*) FROM users")
        users_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM children")
        children_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM sel_balances")
        balances_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM sel_categories")
        categories_count = cursor.fetchone()[0]
        
        conn.close()
        
        print("📊 Validation Migration:")
        print(f"   • Utilisateurs: {users_count}")
        print(f"   • Enfants: {children_count}")
        print(f"   • Balances SEL: {balances_count}")
        print(f"   • Catégories SEL: {categories_count}")
        
        if users_count > 0 and balances_count == users_count and categories_count == 9:
            print("✅ Migration validée avec succès !")
            return True
        else:
            print("❌ Migration incomplète")
            return False
            
    except Exception as e:
        print(f"❌ Erreur validation: {e}")
        return False

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        # Test seulement
        test_migration()
    else:
        # Migration complète
        success = migrate_stage0_to_stage1()
        
        if success:
            print()
            print("🎯 Instructions post-migration:")
            print("1. Arrêter Stage 0: docker-compose down")
            print("2. Lancer Stage 1: docker-compose -f docker-compose.stage1.yml up -d")
            print("3. Tester: curl http://localhost:8000/health")
            print("4. Interface: http://localhost")
        else:
            sys.exit(1)