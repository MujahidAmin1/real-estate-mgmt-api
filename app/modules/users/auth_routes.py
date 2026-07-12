from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.modules.users.auth_exceptions import (
    EmailAlreadyRegistered,
    InvalidCredentials,
    TokenReuseDetected,
    UserNotFound,
    WrongTokenType,
)
from app.modules.users.auth_models import User
from app.modules.users.auth_schemas import (
    AuthResponse,
    LoginDto,
    OnboardingStatusUpdate,
    RefreshSchema,
    UserCreate,
    UserResponse,
)
from app.modules.users.auth_service import AuthService
from app.utils.dependencies import get_current_user

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register", status_code=201, response_model=AuthResponse)
def register_user(body: UserCreate, db: Session = Depends(get_db)):
    try:
        return AuthService(db).register(body.email, body.password, body.role)
    except EmailAlreadyRegistered:
        raise HTTPException(status_code=409, detail="Email already registered")


@router.post("/login", response_model=AuthResponse)
def login(body: LoginDto, db: Session = Depends(get_db)):
    try:
        return AuthService(db).login(body.email, body.password)
    except UserNotFound:
        raise HTTPException(status_code=404, detail="User not found")
    except InvalidCredentials:
        raise HTTPException(status_code=401, detail="Invalid credentials")


@router.post("/refresh")
def refresh_tokens(body: RefreshSchema, db: Session = Depends(get_db)):
    try:
        return AuthService(db).refresh_tokens(body.refresh_token)
    except WrongTokenType:
        raise HTTPException(status_code=401, detail="Wrong token type")
    except TokenReuseDetected:
        raise HTTPException(status_code=401, detail="Token reuse detected")
    except UserNotFound:
        raise HTTPException(status_code=401, detail="User not found")


@router.post("/logout")
def logout(body: RefreshSchema, db: Session = Depends(get_db)):
    AuthService(db).logout(body.refresh_token)
    return {"message": "Logged out"}


@router.get("/me")
def me(user: User = Depends(get_current_user)):
    return user


@router.patch("/onboarding-status", response_model=UserResponse)
def patch_onboarding_status(
    body: OnboardingStatusUpdate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    AuthService(db).update_onboarding_status(user, body.onboarding_status)
    db.refresh(user)
    return user
