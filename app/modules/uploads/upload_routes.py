from fastapi import APIRouter, Depends, Query

from app.modules.uploads.upload_schema import UploadSignResponse
from app.modules.users.models.user import User
from app.services.cloudinary import generate_upload_signature
from app.utils.dependencies import get_current_user

router = APIRouter(prefix="/uploads", tags=["Uploads"])


@router.get("/sign", response_model=UploadSignResponse)
def sign_upload(
    folder: str = Query("general", description="Cloudinary folder to upload into"),
    current_user: User = Depends(get_current_user),
):
    return generate_upload_signature(folder=folder)
