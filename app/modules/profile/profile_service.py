from __future__ import annotations

import uuid

from sqlalchemy.orm import Session

from app.modules.profile.profile_models import AgentProfile
from app.modules.users.auth_enums import UserRole
from app.modules.users.auth_models import User, UserProfile
from app.utils.exceptions import AppError


class ProfileService:
    def __init__(self, db: Session):
        self.db = db

    def get_user_profile(self, user_id: uuid.UUID) -> UserProfile:
        profile = (
            self.db.query(UserProfile)
            .filter(UserProfile.user_id == user_id)
            .first()
        )
        if not profile:
            raise AppError(404, "Profile not found")
        return profile

    def upsert_user_profile(self, user_id: uuid.UUID, data: dict) -> UserProfile:
        profile = (
            self.db.query(UserProfile)
            .filter(UserProfile.user_id == user_id)
            .first()
        )
        if profile:
            for key, value in data.items():
                setattr(profile, key, value)
        else:
            profile = UserProfile(user_id=user_id, **data)
            self.db.add(profile)
        self.db.commit()
        self.db.refresh(profile)
        return profile

    def get_agent_profile(self, user_id: uuid.UUID) -> AgentProfile:
        profile = (
            self.db.query(AgentProfile)
            .filter(AgentProfile.user_id == user_id)
            .first()
        )
        if not profile:
            raise AppError(404, "Profile not found")
        return profile

    def upsert_agent_profile(
        self, user_id: uuid.UUID, data: dict, current_user: User
    ) -> AgentProfile:
        if current_user.role != UserRole.agent:
            raise AppError(403, "Only agents can update agent profile")

        profile = (
            self.db.query(AgentProfile)
            .filter(AgentProfile.user_id == user_id)
            .first()
        )
        if profile:
            for key, value in data.items():
                setattr(profile, key, value)
        else:
            profile = AgentProfile(user_id=user_id, **data)
            self.db.add(profile)
        self.db.commit()
        self.db.refresh(profile)
        return profile
