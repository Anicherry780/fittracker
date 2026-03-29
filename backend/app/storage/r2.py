import boto3
from botocore.config import Config
from app.config import get_settings
import uuid
import logging
from io import BytesIO

logger = logging.getLogger(__name__)
settings = get_settings()


def get_r2_client():
    """Create Cloudflare R2 client (S3-compatible)."""
    return boto3.client(
        "s3",
        endpoint_url=f"https://{settings.R2_ACCOUNT_ID}.r2.cloudflarestorage.com",
        aws_access_key_id=settings.R2_ACCESS_KEY_ID,
        aws_secret_access_key=settings.R2_SECRET_ACCESS_KEY,
        config=Config(signature_version="s3v4"),
        region_name="auto",
    )


async def upload_image(image_bytes: bytes, content_type: str = "image/jpeg", folder: str = "food") -> str:
    """Upload image to R2 and return the public URL."""
    try:
        client = get_r2_client()
        file_ext = "jpg" if "jpeg" in content_type else content_type.split("/")[-1]
        key = f"{folder}/{uuid.uuid4()}.{file_ext}"

        client.upload_fileobj(
            BytesIO(image_bytes),
            settings.R2_BUCKET_NAME,
            key,
            ExtraArgs={"ContentType": content_type},
        )

        # Return public URL
        if settings.R2_PUBLIC_URL:
            return f"{settings.R2_PUBLIC_URL}/{key}"
        return f"https://{settings.R2_BUCKET_NAME}.{settings.R2_ACCOUNT_ID}.r2.cloudflarestorage.com/{key}"

    except Exception as e:
        logger.error(f"R2 upload failed: {e}")
        raise Exception(f"Failed to upload image: {e}")


async def delete_image(key: str) -> bool:
    """Delete image from R2."""
    try:
        client = get_r2_client()
        client.delete_object(Bucket=settings.R2_BUCKET_NAME, Key=key)
        return True
    except Exception as e:
        logger.error(f"R2 delete failed: {e}")
        return False
