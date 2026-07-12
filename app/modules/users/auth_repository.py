from uuid import UUID

from sqlalchemy.orm import Session

from app.modules.users.auth_models import RefreshToken, User


class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def find_by_email(self, email: str) -> User | None:
        return self.db.query(User).filter(User.email == email).first()

    def find_by_id(self, user_id: str | UUID) -> User | None:
        return self.db.query(User).filter(User.id == user_id).first()

    def create(self, email: str, password: str, role: str) -> User:
        user = User(email=email, password=password, role=role)
        self.db.add(user)
        self.db.flush()
        return user

    def save(self, user: User) -> None:
        self.db.flush()


class RefreshTokenRepository:
    def __init__(self, db: Session):
        self.db = db

    def find_by_jwtid(self, jwtid: str) -> RefreshToken | None:
        return (
            self.db.query(RefreshToken)
            .filter(RefreshToken.jwtid == jwtid, RefreshToken.revoked == False)
            .first()
        )

    def create(self, jwtid: str, user_id: UUID, expires_at) -> RefreshToken:
        token = RefreshToken(jwtid=jwtid, user_id=user_id, expires_at=expires_at)
        self.db.add(token)
        self.db.flush()
        return token

    def revoke_all_for_user(self, user_id: str) -> None:
        self.db.query(RefreshToken).filter(
            RefreshToken.user_id == user_id
        ).update({"revoked": True})
        self.db.flush()

    def revoke_by_jwtid(self, jwtid: str) -> None:
        self.db.query(RefreshToken).filter(
            RefreshToken.jwtid == jwtid
        ).update({"revoked": True})
        self.db.flush()
