import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.modules.admin.admin_service import AdminService
from app.modules.properties.property_schemas import PropertyResponse
from app.modules.users.auth_enums import UserRole
from app.modules.users.auth_models import User
from app.modules.users.auth_schemas import UserResponse
from app.utils.dependencies import require_role
from app.utils.exceptions import AppError

router = APIRouter(prefix="/admin", tags=["Admin"])


@router.delete("/users/{user_id}/delete")
def delete_user(
    user_id: uuid.UUID,
    current_user: User = Depends(require_role(UserRole.admin)),
    db: Session = Depends(get_db)
):
    return AdminService(db).delete_user(user_id, current_user)


@router.patch("/users/{user_id}/ban")
def ban_user(
    user_id: uuid.UUID,
    current_user: User = Depends(require_role(UserRole.admin)),
    db: Session = Depends(get_db)
):
    return AdminService(db).ban_user(user_id, current_user)


@router.get("/users/clients", response_model=list[UserResponse])
def get_all_clients(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.admin))
):
    return AdminService(db).get_all_clients()


@router.get("/users/agents", response_model=list[UserResponse])
def get_all_agents(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.admin))
):
    return AdminService(db).get_all_agents()


@router.get("/properties", response_model=list[PropertyResponse])
def get_all_properties(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.admin))
):
    return AdminService(db).get_all_properties()
