from __future__ import annotations

import uuid

from sqlalchemy.orm import Session

from app.modules.properties.property_models import Property
from app.modules.users.auth_enums import UserRole
from app.modules.users.auth_models import User
from app.utils.exceptions import AppError


class AdminService:
    def __init__(self, db: Session):
        self.db = db

    def delete_user(self, user_id: uuid.UUID, current_user: User) -> dict:
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise AppError(404, "User not found")
        self.db.delete(user)
        self.db.commit()
        return {"message": "User deleted successfully"}

    def ban_user(self, user_id: uuid.UUID, current_user: User) -> dict:
        if user_id == current_user.id:
            raise AppError(403, "You cannot ban yourself")

        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise AppError(404, "User not found")

        user.is_active = False
        self.db.commit()
        self.db.refresh(user)
        return {"message": "User banned successfully"}

    def get_all_clients(self) -> list[User]:
        return self.db.query(User).filter(User.role == UserRole.client).all()

    def get_all_agents(self) -> list[User]:
        return self.db.query(User).filter(User.role == UserRole.agent).all()

    def get_all_properties(self) -> list[Property]:
        return self.db.query(Property).all()
