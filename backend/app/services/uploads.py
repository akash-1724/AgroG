import hashlib
import time
from pathlib import Path
from typing import Protocol
from urllib.parse import urlparse

import httpx
from fastapi import HTTPException, UploadFile, status

from app.core.config import settings


class StoredUpload(dict):
    secure_url: str
    public_id: str | None


class StorageProvider(Protocol):
    async def upload_listing_image(self, file: UploadFile, content: bytes) -> StoredUpload:
        ...


def validate_listing_image(file: UploadFile, content: bytes) -> None:
    extension = Path(file.filename or "").suffix.lower()
    if file.content_type not in settings.LISTING_IMAGE_ALLOWED_MIME_TYPES:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Unsupported image MIME type.")
    if extension not in settings.LISTING_IMAGE_ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Unsupported image file extension.")
    max_bytes = settings.MAX_LISTING_IMAGE_UPLOAD_MB * 1024 * 1024
    if len(content) > max_bytes:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Image exceeds {settings.MAX_LISTING_IMAGE_UPLOAD_MB}MB limit.")


class CloudinaryStorageProvider:
    def __init__(self, cloudinary_url: str):
        parsed = urlparse(cloudinary_url)
        self.api_key = parsed.username or ""
        self.api_secret = parsed.password or ""
        self.cloud_name = parsed.hostname or ""
        if not self.api_key or not self.api_secret or not self.cloud_name:
            raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Cloudinary storage is not configured correctly.")

    async def upload_listing_image(self, file: UploadFile, content: bytes) -> StoredUpload:
        timestamp = str(int(time.time()))
        folder = "agroguide/listings"
        signature_payload = f"folder={folder}&timestamp={timestamp}{self.api_secret}"
        signature = hashlib.sha1(signature_payload.encode("utf-8")).hexdigest()
        upload_url = f"https://api.cloudinary.com/v1_1/{self.cloud_name}/image/upload"
        async with httpx.AsyncClient(timeout=20.0) as client:
            response = await client.post(
                upload_url,
                data={
                    "api_key": self.api_key,
                    "timestamp": timestamp,
                    "folder": folder,
                    "signature": signature,
                },
                files={"file": (file.filename, content, file.content_type)},
            )
        if response.status_code >= 400:
            raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail="Image storage provider rejected the upload.")
        data = response.json()
        return StoredUpload(secure_url=data.get("secure_url"), public_id=data.get("public_id"))


def get_storage_provider() -> StorageProvider:
    if not settings.CLOUDINARY_URL:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Listing image storage is not configured.")
    return CloudinaryStorageProvider(settings.CLOUDINARY_URL)
