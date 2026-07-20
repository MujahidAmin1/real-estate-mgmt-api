from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session

from app.core.config import settings
from app.modules.users.auth_models import RefreshToken, User
from app.utils.exceptions import AppError
from app.utils.hashing import hash_password, verify_password
from app.utils.jwt import create_access_token, create_refresh_token, verify_refresh_token


class AuthService:
    def __init__(self, db: Session):
        self.db = db

    def register(self, email: str, password: str, role: str) -> dict:
        existing = self.db.query(User).filter(User.email == email).first()
        if existing:
            raise AppError(409, "Email already registered")

        user = User(email=email, password=hash_password(password), role=role)
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)

        return self._build_auth_response(user)

    def login(self, email: str, password: str) -> dict:
        user = self.db.query(User).filter(User.email == email).first()
        if not user:
            raise AppError(404, "User not found")

        if not verify_password(password, user.password):
            raise AppError(401, "Invalid credentials")

        return self._build_auth_response(user)

    def refresh_tokens(self, refresh_token: str) -> dict:
        payload = verify_refresh_token(refresh_token)

        if payload.get("type") != "refresh":
            raise AppError(401, "Wrong token type")

        jwtid = payload["jwtid"]
        user_id = payload["sub"]

        db_token = (
            self.db.query(RefreshToken)
            .filter(RefreshToken.jwtid == jwtid, RefreshToken.revoked == False)
            .first()
        )
        if not db_token:
            self.db.query(RefreshToken).filter(
                RefreshToken.user_id == user_id
            ).update({"revoked": True})
            self.db.commit()
            raise AppError(401, "Token reuse detected")

        db_token.revoked = True
        self.db.flush()

        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise AppError(401, "User not found")

        new_access = create_access_token(str(user.id), user.role)
        new_refresh, new_jwtid = create_refresh_token(user_id)

        self.db.add(
            RefreshToken(
                jwtid=new_jwtid,
                user_id=user.id,
                expires_at=datetime.now(timezone.utc) + timedelta(days=settings.refresh_token_expire_days),
            )
        )
        self.db.commit()

        return {"access_token": new_access, "refresh_token": new_refresh}

    def logout(self, refresh_token: str) -> None:
        try:
            payload = verify_refresh_token(refresh_token)
            self.db.query(RefreshToken).filter(
                RefreshToken.jwtid == payload["jwtid"]
            ).update({"revoked": True})
            self.db.commit()
        except ValueError:
            pass

    def update_onboarding_status(self, user, status) -> None:
        user.onboarding_status = status
        self.db.commit()

    def _build_auth_response(self, user) -> dict:
        access_token = create_access_token(str(user.id), user.role)
        refresh_token, jwtid = create_refresh_token(str(user.id))

        self.db.add(
            RefreshToken(
                jwtid=jwtid,
                user_id=user.id,
                expires_at=datetime.now(timezone.utc) + timedelta(days=settings.refresh_token_expire_days),
            )
        )
        self.db.commit()

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "user": user,
        }
