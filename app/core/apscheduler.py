# scheduler.py
from apscheduler.schedulers.background import BackgroundScheduler
from app.db.database import SessionLocal
from app.modules.users.auth_models import RefreshToken
from datetime import datetime, timezone

def delete_expired_tokens():
    db = SessionLocal()
    try:
        deleted = db.query(RefreshToken).filter(
            (RefreshToken.expires_at < datetime.now(timezone.utc)) |
            (RefreshToken.revoked == True)
        ).delete()
        db.commit()
        print(f"Cleaned up {deleted} tokens")
    finally:
        db.close()

scheduler = BackgroundScheduler()  # instance, not the class
scheduler.add_job(delete_expired_tokens, "interval", hours=24)