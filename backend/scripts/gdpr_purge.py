#!/usr/bin/env python3
"""
GDPR Purge Script
Purges old privacy events and consolidates anonymization for old deleted users.
Run locally: python backend/scripts/gdpr_purge.py
"""

import os
from datetime import datetime, timedelta

from app.main_stage4 import GDPR_DATA_RETENTION_DAYS
from app.models_stage1 import User
from app.models_stage2 import PrivacyEvent
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


def main():
    db_url = os.getenv("DATABASE_URL", "sqlite:///test.db")
    engine = create_engine(db_url, connect_args={"check_same_thread": False} if db_url.startswith("sqlite") else {})
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()
    try:
        cutoff = datetime.utcnow() - timedelta(days=GDPR_DATA_RETENTION_DAYS)
        old_events = db.query(PrivacyEvent).filter(PrivacyEvent.created_at < cutoff).all()
        events_purged = len(old_events)
        for ev in old_events:
            db.delete(ev)

        old_deleted_users = db.query(User).filter(User.deleted_at.isnot(None)).filter(User.deleted_at < cutoff).all()
        users_anonymized = 0
        for u in old_deleted_users:
            if not (u.email or "").startswith("deleted+"):
                u.email = f"deleted+{u.id}@example.invalid"
            u.first_name = "Deleted"
            u.last_name = "User"
            users_anonymized += 1
            db.add(u)

        db.commit()
        print({"events_purged": events_purged, "users_anonymized": users_anonymized})
    finally:
        db.close()


if __name__ == "__main__":
    main()

