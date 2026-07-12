from __future__ import annotations

import uuid

from sqlalchemy.orm import Session

from app.modules.profile.profile_exceptions import ProfileNotFound
from app.modules.profile.profile_repository import (
    AgentProfileRepository,
    UserProfileRepository,
)
from app.modules.users.auth_enums import UserRole
from app.modules.users.auth_models import User


class ProfileService:
    def __init__(self, db: Session):
        self.db = db
        self.user_profile_repo = UserProfileRepository(db)
        self.agent_profile_repo = AgentProfileRepository(db)

    def get_user_profile(self, user_id: uuid.UUID) -> UserProfile:
        profile = self.user_profile_repo.find_by_user_id(user_id)
        if not profile:
            raise ProfileNotFound()
        return profile

    def upsert_user_profile(self, user_id: uuid.UUID, data: dict) -> UserProfile:
        return self.user_profile_repo.upsert(user_id, data)

    def get_agent_profile(self, user_id: uuid.UUID) -> AgentProfile:
        profile = self.agent_profile_repo.find_by_user_id(user_id)
        if not profile:
            raise ProfileNotFound()
        return profile

    def upsert_agent_profile(self, user_id: uuid.UUID, data: dict, current_user: User) -> AgentProfile:
        if current_user.role != UserRole.agent:
            raise PermissionError("Only agents can update agent profile")
        return self.agent_profile_repo.upsert(user_id, data)
