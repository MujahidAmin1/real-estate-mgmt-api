from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session

from app.core.config import settings
from app.modules.users.auth_exceptions import (
    EmailAlreadyRegistered,
    InvalidCredentials,
    TokenReuseDetected,
    UserNotFound,
    WrongTokenType,
)
from app.modules.users.auth_repository import RefreshTokenRepository, UserRepository
from app.utils.hashing import hash_password, verify_password
from app.utils.jwt import create_access_token, create_refresh_token, verify_refresh_token


class AuthService:
    def __init__(self, db: Session):
        self.db = db
        self.user_repo = UserRepository(db)
        self.token_repo = RefreshTokenRepository(db)

    def register(self, email: str, password: str, role: str) -> dict:
        existing = self.user_repo.find_by_email(email)
        if existing:
            raise EmailAlreadyRegistered()

        user = self.user_repo.create(email, hash_password(password), role)
        self.db.commit()
        self.db.refresh(user)

        return self._build_auth_response(user)

    def login(self, email: str, password: str) -> dict:
        user = self.user_repo.find_by_email(email)
        if not user:
            raise UserNotFound()

        if not verify_password(password, user.password):
            raise InvalidCredentials()

        return self._build_auth_response(user)

    def refresh_tokens(self, refresh_token: str) -> dict:
        payload = verify_refresh_token(refresh_token)

        if payload.get("type") != "refresh":
            raise WrongTokenType()

        jwtid = payload["jwtid"]
        user_id = payload["sub"]

        db_token = self.token_repo.find_by_jwtid(jwtid)
        if not db_token:
            self.token_repo.revoke_all_for_user(user_id)
            self.db.commit()
            raise TokenReuseDetected()

        db_token.revoked = True
        self.db.flush()

        user = self.user_repo.find_by_id(user_id)
        if not user:
            raise UserNotFound()

        new_access = create_access_token(str(user.id), user.role)
        new_refresh, new_jwtid = create_refresh_token(user_id)

        self.token_repo.create(
            new_jwtid,
            user.id,
            datetime.now(timezone.utc) + timedelta(days=settings.refresh_token_expire_days),
        )
        self.db.commit()

        return {"access_token": new_access, "refresh_token": new_refresh}

    def logout(self, refresh_token: str) -> None:
        try:
            payload = verify_refresh_token(refresh_token)
            self.token_repo.revoke_by_jwtid(payload["jwtid"])
            self.db.commit()
        except ValueError:
            pass

    def update_onboarding_status(self, user, status) -> None:
        user.onboarding_status = status
        self.db.commit()

    def _build_auth_response(self, user) -> dict:
        access_token = create_access_token(str(user.id), user.role)
        refresh_token, jwtid = create_refresh_token(str(user.id))

        self.token_repo.create(
            jwtid,
            user.id,
            datetime.now(timezone.utc) + timedelta(days=settings.refresh_token_expire_days),
        )
        self.db.commit()

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "user": user,
        }
