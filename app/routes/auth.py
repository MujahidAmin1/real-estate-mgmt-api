from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, Request
from app.database import get_db
from app.dependencies import get_current_user
from app.models.usermodels.refresh_tokens import RefreshToken
from app.schemas.user_schema import LoginDto, RefreshSchema, UserCreate, UserResponse
from app.models.usermodels.user import User
from sqlalchemy.orm import Session
from app.utils import jwt
from app.utils.hashing import hash_password, verify_password
from app.utils.jwt import create_access_token, create_refresh_token, verify_refresh_token


router = APIRouter(prefix="/auth", tags=["Auth"])

@router.post("/register", status_code=201, response_model=UserResponse)
def register_user(body: UserCreate, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == body.email).first()
    
    if existing:
        raise HTTPException(status_code=409, detail="Email already registered")
    user = User(email=body.email, password=hash_password(body.password))
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@router.post("/login", response_model=UserResponse)
def login(body: LoginDto, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == body.email).first()

    if not user or not verify_password(body.password, user.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    access_token = create_access_token(str(user.id), user.role)
    refresh_token, jwtid = create_refresh_token(str(user.id))

    # Persist the refresh token
    db_token = RefreshToken(
        jwtid=jwtid,
        user_id=user.id,
        expires_at=datetime.now(timezone.utc) + timedelta(days=7),
    )
    db.add(db_token)
    db.commit()

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "user": user
    }

@router.post("/refresh")
def refresh_tokens(body: RefreshSchema, db: Session = Depends(get_db)):
  
    payload = verify_refresh_token(body.refresh_token)

    if payload.get("type") != "refresh":
        raise HTTPException(status_code=401, detail="Wrong token type")

    jwtid = payload["jwtid"]
    user_id = payload["sub"]

    # Check the token exists and hasn't been revoked
    db_token = db.query(RefreshToken).filter(
        RefreshToken.jwtid == jwtid,
        RefreshToken.revoked == False,
    ).first()

    if not db_token:
        # Token already used or revoked — possible token theft, kill all sessions
        db.query(RefreshToken).filter(RefreshToken.user_id == user_id).update(
            {"revoked": True}
        )
        db.commit()
        raise HTTPException(status_code=401, detail="Token reuse detected")

    # Revoke old refresh token
    db_token.revoked = True
    db.commit()

    # Issue new pair
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    new_access = create_access_token(str(user.id), user.role)
    new_refresh, new_jwtid = create_refresh_token(user_id)

    db.add(RefreshToken(
        jwtid=new_jwtid,
        user_id=user_id,
        expires_at=datetime.now(timezone.utc) + timedelta(days=7),
    ))
    db.commit()

    return {"access_token": new_access, "refresh_token": new_refresh}

@router.post("/logout")
def logout(body: RefreshSchema, db: Session = Depends(get_db)):
    try:
        payload = verify_refresh_token(body.refresh_token)
        jwtid = payload["jwtid"]
        db.query(RefreshToken).filter(RefreshToken.jwtid == jwtid).update({"revoked": True})
        db.commit()
    except jwt.InvalidTokenError: # type: ignore
        pass  # already invalid, that's fine

    return {"message": "Logged out"}

@router.get("/me")
def me(user: User = Depends(get_current_user)):
    return user
