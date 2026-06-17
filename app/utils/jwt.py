from uuid import uuid7

from jose import JWTError, jwt
from datetime import datetime, timedelta, timezone

from app.core.config import settings

def create_access_token(user_id: str, role: str) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "sub": user_id,
        "type": "access",
        "role": role,
        "iat": now,
        "exp": now + timedelta(minutes=settings.access_token_expire_minutes),
    }
    return jwt.encode(payload, settings.secret_key, algorithm=settings.algorithm)


def create_refresh_token(user_id: str) -> tuple[str, str]:
    """Returns (encoded_token, jwtid) — store jwtid in DB."""
    now = datetime.now(timezone.utc)
    jwtid = str(uuid7())
    payload = {
        "sub": user_id,
        "type": "refresh",
        "jwtid": jwtid,
        "iat": now,
        "exp": now + timedelta(days=settings.refresh_token_expire_days),
    }
    return jwt.encode(payload, settings.secret_key, algorithm=settings.algorithm), jwtid

def verify_access_token(token: str) -> dict:
    try:
        payload: dict = jwt.decode(token, settings.secret_key, algorithms=settings.algorithm)
        if payload.get("type") != "access":
            raise ValueError('Not an access token')
        return payload
    except JWTError:
        raise ValueError("invalid or expired token")
    
def verify_refresh_token(token: str) -> dict:
    try:
        payload: dict = jwt.decode(token, settings.secret_key, algorithms=settings.algorithm)
        if payload.get("type") != "refresh":
            raise ValueError('Not a refresh token')
        return payload
    except JWTError:
        raise ValueError("invalid or expired token")
    

        
        