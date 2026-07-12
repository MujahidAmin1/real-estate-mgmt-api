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
from app.utils.exceptions import ForbiddenException, NotFoundException

router = APIRouter(prefix="/admin", tags=["Admin"])


@router.delete("/users/{user_id}/delete")
def delete_user(
    user_id: uuid.UUID,
    current_user: User = Depends(require_role(UserRole.admin)),
    db: Session = Depends(get_db)
):
    service = AdminService(db)
    try:
        return service.delete_user(user_id, current_user)
    except NotFoundException:
        raise HTTPException(status_code=404, detail="User not found")


@router.patch("/users/{user_id}/ban")
def ban_user(
    user_id: uuid.UUID,
    current_user: User = Depends(require_role(UserRole.admin)),
    db: Session = Depends(get_db)
):
    service = AdminService(db)
    try:
        return service.ban_user(user_id, current_user)
    except NotFoundException:
        raise HTTPException(status_code=404, detail="User not found")
    except ForbiddenException as exc:
        raise HTTPException(status_code=403, detail=str(exc))


@router.get("/users/clients", response_model=list[UserResponse])
def get_all_clients(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.admin))
):
    service = AdminService(db)
    return service.get_all_clients()


@router.get("/users/agents", response_model=list[UserResponse])
def get_all_agents(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.admin))
):
    service = AdminService(db)
    return service.get_all_agents()


@router.get("/properties", response_model=list[PropertyResponse])
def get_all_properties(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.admin))
):
    service = AdminService(db)
    return service.get_all_properties()
