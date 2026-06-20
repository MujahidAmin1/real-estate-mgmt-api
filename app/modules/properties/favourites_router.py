from __future__ import annotations
from fastapi import APIRouter, Depends
import uuid
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.modules.properties.models.property_favourite import Favorite
from app.modules.users.user_enums import UserRole
from app.modules.properties.models.property import Property
from app.modules.users.models.user import User
from app.utils.dependencies import require_role
from app.utils.exceptions import NotFoundException, ConflictException


router = APIRouter(prefix="/properties", tags=["Properties"])


@router.post("/{property_id}/favorite", status_code=201)
def favourite_property(
    property_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.client)),
):
    property = db.query(Property).filter(Property.id == property_id).first()

    if not property:
        raise NotFoundException("Property not found")

    existing_favorite = db.query(Favorite).filter(
        Favorite.user_id == current_user.id,
        Favorite.property_id == property_id
    ).first()

    if existing_favorite:
        raise ConflictException("Property is already favorited")

    favorite = Favorite(user_id=current_user.id, property_id=property_id)
    db.add(favorite)
    db.commit()
    return {"message": "Property favorited successfully"}

@router.delete("/{property_id}/favorite", status_code=204)
def unfavourite_property(
    property_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.client)),
):
    favorite = db.query(Favorite).filter(
        Favorite.user_id == current_user.id,
        Favorite.property_id == property_id
    ).first()

    if not favorite:
        raise NotFoundException("Favorite not found")

    db.delete(favorite)
    db.commit()