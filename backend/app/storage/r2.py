import boto3
import uuid
from io import BytesIO
from app.config import get_settings

settings = get_settings()


def get_r2_client():
    return boto3.client(
        "s3",
        endpoint_url=f"https://{settings.R2_ACCOUNT_ID}.r2.cloudflarestorage.com",
        aws_access_key_id=settings.R2_ACCESS_KEY_ID,
        aws_secret_access_key=settings.R2_SECRET_ACCESS_KEY,
        region_name="auto",
    )


def upload_image(image_bytes: bytes, content_type: str = "image/jpeg") -> str:
    client = get_r2_client()
    ext = "jpg" if "jpeg" in content_type else content_type.split("/")[-1]
    key = f"food-images/{uuid.uuid4().hex}.{ext}"

    client.upload_fileobj(
        BytesIO(image_bytes),
        settings.R2_BUCKET_NAME,
        key,
        ExtraArgs={"ContentType": content_type},
    )

    if settings.R2_PUBLIC_URL:
        return f"{settings.R2_PUBLIC_URL}/{key}"
    return f"https://{settings.R2_BUCKET_NAME}.{settings.R2_ACCOUNT_ID}.r2.cloudflarestorage.com/{key}"
