import cloudinary
import cloudinary.uploader
from app.core.config import settings

cloudinary.config(
    cloud_name=settings.cloudinary_cloud_name,
    api_key=settings.cloudinary_api_key,
    api_secret=settings.cloudinary_api_secret,
    secure=True
)

def upload_image(file: bytes, folder: str = "property") -> dict:
    result: dict = cloudinary.uploader.upload(file, folder=folder)
    return {
        "url": result["secure_url"],
        "public_id": result["public_id"]
    }

def delete_image(public_id: str) -> None:
    cloudinary.uploader.destroy(public_id)