import time

import cloudinary
import cloudinary.uploader
from cloudinary.utils import api_sign_request

from app.core.config import settings

cloudinary.config(
    cloud_name=settings.cloudinary_cloud_name,
    api_key=settings.cloudinary_api_key,
    api_secret=settings.cloudinary_api_secret,
    secure=True
)


def generate_upload_signature(folder: str = "general") -> dict:
    timestamp = int(time.time())
    params = {
        "timestamp": timestamp,
        "folder": folder,
    }
    signature = api_sign_request(params, settings.cloudinary_api_secret)

    return {
        "cloud_name": settings.cloudinary_cloud_name,
        "api_key": settings.cloudinary_api_key,
        "timestamp": timestamp,
        "signature": signature,
        "folder": folder,
    }


def delete_image(public_id: str) -> None:
    cloudinary.uploader.destroy(public_id)
