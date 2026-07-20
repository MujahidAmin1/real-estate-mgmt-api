from fastapi import APIRouter, Depends
from app.db.database import get_db
from app.modules.profile.profile_schemas import (
    AgentProfileResponse,
    AgentProfileUpdate,
    UserProfileResponse,
    UserProfileUpdate,
)
from app.modules.profile.profile_service import ProfileService
from app.modules.users.auth_models import User
from app.utils.dependencies import get_current_user
from sqlalchemy.orm import Session


router = APIRouter(prefix="/profile", tags=["Profile"])


@router.put("", response_model=UserProfileResponse)
def upsert_profile(
    data: UserProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    service = ProfileService(db)
    return service.upsert_user_profile(
        current_user.id, data.model_dump(exclude_unset=True)
    )


@router.get("", response_model=UserProfileResponse)
def get_user_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    service = ProfileService(db)
    return service.get_user_profile(current_user.id)


@router.put("/agent_profile", response_model=AgentProfileResponse)
def upsert_agent_profile(
    data: AgentProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    service = ProfileService(db)
    return service.upsert_agent_profile(
        current_user.id, data.model_dump(exclude_unset=True), current_user
    )


@router.get("/agent_profile", response_model=AgentProfileResponse)
def get_agent_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    service = ProfileService(db)
    return service.get_agent_profile(current_user.id)
