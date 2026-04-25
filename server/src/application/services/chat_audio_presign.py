from __future__ import annotations

import aioboto3  # type: ignore

from config.settings import settings


async def presign_chat_audio(key: str, expires_in: int = 3600) -> str:
    session = aioboto3.Session()
    async with session.client(
        service_name="s3",
        endpoint_url=settings.MINIO_ENDPOINT,
        aws_access_key_id=settings.MINIO_ACCESS_KEY,
        aws_secret_access_key=settings.MINIO_SECRET_KEY,
    ) as client:
        return await client.generate_presigned_url(
            ClientMethod="get_object",
            Params={"Bucket": settings.MINIO_AUDIO_BUCKET, "Key": key},
            ExpiresIn=expires_in,
        )
