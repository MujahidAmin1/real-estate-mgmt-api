from fastapi import APIRouter, Depends, HTTPException, Request
from app.db.database import get_db
from app.modules.profile.models.agent_profile import AgentProfile
from app.modules.users.models.user import User
from app.modules.users.models.user_profile import UserProfile
from app.modules.users.user_enums import UserRole
from app.utils.dependencies import get_current_user
from sqlalchemy.orm import Session
from app.modules.profile.profile_schema import AgentProfileResponse, AgentProfileUpdate, UserProfileResponse, UserProfileUpdate


router = APIRouter(prefix="/profile", tags=["Profile"])

@router.put("", response_model=UserProfileResponse)
def upsert_profile(
    data: UserProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    profile = (
        db.query(UserProfile)
        .filter(UserProfile.user_id == current_user.id)
        .first()
    )

    if profile:
        for key, value in data.model_dump(exclude_unset=True).items():
            setattr(profile, key, value)
    else:
        profile = UserProfile(
            user_id=current_user.id,
            **data.model_dump(exclude_unset=True)
        )
        db.add(profile)

    db.commit()
    db.refresh(profile)
    return profile

@router.get("", response_model=UserProfileResponse)
def get_user_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    profile = (
        db.query(UserProfile)
        .filter(UserProfile.user_id == current_user.id)
        .first()
    )

    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")

    return profile



@router.put("/agent_profile", response_model=AgentProfileResponse)
def upsert_agent_profile(
    data: AgentProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.role != UserRole.agent:
        raise HTTPException(status_code=403, detail="Only agents can update agent profile")

    profile = (
        db.query(AgentProfile)
        .filter(AgentProfile.user_id == current_user.id)
        .first()
    )

    if profile:
        for key, value in data.model_dump(exclude_unset=True).items():
            setattr(profile, key, value)
    else:
        profile = AgentProfile(
            user_id=current_user.id,
            **data.model_dump(exclude_unset=True)
        )
        db.add(profile)

    db.commit()
    db.refresh(profile)
    return profile

@router.get("/agent_profile", response_model=AgentProfileResponse)
def get_agent_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    profile = (
        db.query(AgentProfile)
        .filter(AgentProfile.user_id == current_user.id)
        .first()
    )

    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")

    return profile
