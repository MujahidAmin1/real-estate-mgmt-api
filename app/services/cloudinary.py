from dataclasses import dataclass

import cloudinary
import cloudinary.uploader
from cloudinary.exceptions import Error as CloudinaryError
from fastapi import UploadFile

from app.core.config import settings

cloudinary.config(
    cloud_name=settings.cloudinary_cloud_name,
    api_key=settings.cloudinary_api_key,
    api_secret=settings.cloudinary_api_secret,
    secure=True
)


@dataclass(frozen=True)
class UploadedImage:
    image_url: str
    public_id: str


class ImageUploadError(Exception):
    pass


class InvalidImageFileError(ImageUploadError):
    pass


class CloudinaryUploadError(ImageUploadError):
    pass


def delete_image(public_id: str) -> None:
    cloudinary.uploader.destroy(public_id)


def validate_image_file(file: UploadFile) -> None:
    if not file.content_type or not file.content_type.startswith("image/"):
        filename = file.filename or "uploaded file"
        raise InvalidImageFileError(f"{filename} must be a valid image file")


def upload_image(file: UploadFile, folder: str = "properties") -> UploadedImage:
    validate_image_file(file)

    try:
        result = cloudinary.uploader.upload(
            file.file,
            folder=folder,
            resource_type="image",
        )
    except CloudinaryError as exc:
        filename = file.filename or "uploaded file"
        raise CloudinaryUploadError(f"Failed to upload {filename}") from exc

    secure_url = result.get("secure_url")
    public_id = result.get("public_id")

    if not secure_url or not public_id:
        filename = file.filename or "uploaded file"
        raise CloudinaryUploadError(f"Cloudinary did not return a URL for {filename}")

    return UploadedImage(image_url=secure_url, public_id=public_id)


def upload_images(files: list[UploadFile], folder: str = "properties") -> list[UploadedImage]:
    if not files:
        raise InvalidImageFileError("At least one image is required")

    for file in files:
        validate_image_file(file)

    uploaded_images: list[UploadedImage] = []
    try:
        for file in files:
            uploaded_images.append(upload_image(file, folder=folder))
    except ImageUploadError:
        for image in uploaded_images:
            delete_image(image.public_id)
        raise

    return uploaded_images
