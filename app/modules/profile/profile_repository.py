from __future__ import annotations

import uuid
from typing import Optional

from sqlalchemy.orm import Session

from app.modules.profile.profile_models import AgentProfile
from app.modules.users.auth_models import UserProfile


class UserProfileRepository:
    def __init__(self, db: Session):
        self.db = db

    def find_by_user_id(self, user_id: uuid.UUID) -> Optional[UserProfile]:
        return (
            self.db.query(UserProfile)
            .filter(UserProfile.user_id == user_id)
            .first()
        )

    def upsert(self, user_id: uuid.UUID, data: dict) -> UserProfile:
        profile = self.find_by_user_id(user_id)
        if profile:
            for key, value in data.items():
                setattr(profile, key, value)
        else:
            profile = UserProfile(user_id=user_id, **data)
            self.db.add(profile)
        self.db.commit()
        self.db.refresh(profile)
        return profile


class AgentProfileRepository:
    def __init__(self, db: Session):
        self.db = db

    def find_by_user_id(self, user_id: uuid.UUID) -> Optional[AgentProfile]:
        return (
            self.db.query(AgentProfile)
            .filter(AgentProfile.user_id == user_id)
            .first()
        )

    def upsert(self, user_id: uuid.UUID, data: dict) -> AgentProfile:
        profile = self.find_by_user_id(user_id)
        if profile:
            for key, value in data.items():
                setattr(profile, key, value)
        else:
            profile = AgentProfile(user_id=user_id, **data)
            self.db.add(profile)
        self.db.commit()
        self.db.refresh(profile)
        return profile
