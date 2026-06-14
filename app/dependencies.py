from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.database import get_db

from app.models.usermodels.user import User
from app.utils.jwt import verify_access_token

bearer_scheme = HTTPBearer()

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: Session = Depends(get_db)
) -> User:
    credentials_exception = HTTPException(status_code=401, detail="Invalid credentials")

    try:
        payload = verify_access_token(credentials.credentials)
    except ValueError:
        raise credentials_exception

    user_id = payload.get("user_id")

    if user_id is None:
        raise credentials_exception

    user = db.query(User).filter(User.id == int(user_id)).first()

    if not user:
        raise credentials_exception

    return user