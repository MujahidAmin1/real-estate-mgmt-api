
import uuid
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.modules.properties.models.property import Property
from app.modules.properties.property_schema import PropertyResponse
from app.modules.users.models.user import User
from app.modules.users.user_enums import UserRole
from app.modules.users.user_schema import UserResponse
from app.utils.dependencies import require_role
from app.utils.exceptions import ForbiddenException, NotFoundException

router = APIRouter(prefix="/admin", tags=["Admin"])

@router.delete("/users/{user_id}/delete")
def delete_user(
    user_id: uuid.UUID,
    current_user: User = Depends(require_role(UserRole.admin)),
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise NotFoundException()
    
    db.delete(user)
    db.commit()
    return {"message": "User deleted successfully"}


@router.patch("/users/{user_id}/ban")
def ban_user(
    user_id: uuid.UUID,
    current_user: User = Depends(require_role(UserRole.admin)),
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.id == user_id).first()

    if user_id == current_user.id:
        raise ForbiddenException("You cannot ban yourself")
    if not user:
        raise NotFoundException()

    user.is_active = False

    db.commit()
    db.refresh(user)

    return {"message": "User banned successfully"}

@router.get("/users/clients", response_model=list[UserResponse])
def get_all_clients(
    db: Session = Depends(get_db), 
    current_user: User = Depends(require_role(UserRole.admin))
):
    clients = db.query(User).filter(User.role == UserRole.client).all()
    
    return clients

@router.get("/users/agents", response_model=list[UserResponse])
def get_all_agents(
    db: Session = Depends(get_db), 
    current_user: User = Depends(require_role(UserRole.admin))
):
    agents = db.query(User).filter(User.role == UserRole.agent).all()
    
    return agents

@router.get("/properties", response_model=list[PropertyResponse])
def get_all_properties(
    db: Session = Depends(get_db), 
    current_user: User = Depends(require_role(UserRole.admin))
):
    properties = db.query(Property).all()
    
    return properties
        
        