from __future__ import annotations

import uuid

from sqlalchemy.orm import Session

from app.modules.properties.property_models import Property
from app.modules.users.auth_models import User


class AdminUserRepository:
    def __init__(self, db: Session):
        self.db = db

    def find_by_id(self, user_id: uuid.UUID) -> User | None:
        return self.db.query(User).filter(User.id == user_id).first()

    def delete(self, user: User) -> None:
        self.db.delete(user)
        self.db.commit()

    def ban(self, user: User) -> User:
        user.is_active = False
        self.db.commit()
        self.db.refresh(user)
        return user

    def find_all_by_role(self, role: str) -> list[User]:
        return self.db.query(User).filter(User.role == role).all()


class AdminPropertyRepository:
    def __init__(self, db: Session):
        self.db = db

    def find_all(self) -> list[Property]:
        return self.db.query(Property).all()
