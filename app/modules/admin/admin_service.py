from __future__ import annotations

import uuid

from sqlalchemy.orm import Session

from app.modules.admin.admin_exceptions import CannotBanSelf
from app.modules.admin.admin_repository import AdminPropertyRepository, AdminUserRepository
from app.modules.properties.property_models import Property
from app.modules.users.auth_enums import UserRole
from app.modules.users.auth_models import User
from app.utils.exceptions import ForbiddenException, NotFoundException


class AdminService:
    def __init__(self, db: Session):
        self.db = db
        self.user_repo = AdminUserRepository(db)
        self.property_repo = AdminPropertyRepository(db)

    def delete_user(self, user_id: uuid.UUID, current_user: User) -> dict:
        user = self.user_repo.find_by_id(user_id)
        if not user:
            raise NotFoundException()
        self.user_repo.delete(user)
        return {"message": "User deleted successfully"}

    def ban_user(self, user_id: uuid.UUID, current_user: User) -> dict:
        if user_id == current_user.id:
            raise ForbiddenException("You cannot ban yourself")
        user = self.user_repo.find_by_id(user_id)
        if not user:
            raise NotFoundException()
        self.user_repo.ban(user)
        return {"message": "User banned successfully"}

    def get_all_clients(self) -> list[User]:
        return self.user_repo.find_all_by_role(UserRole.client)

    def get_all_agents(self) -> list[User]:
        return self.user_repo.find_all_by_role(UserRole.agent)

    def get_all_properties(self) -> list[Property]:
        return self.property_repo.find_all()
