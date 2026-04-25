import aioboto3 #type: ignore

from domain.ports.storage_interface import StorageInterface
from config.settings import settings


class ImageStorage(StorageInterface):
    def __init__(self):
        self._session = aioboto3.Session()
     
    async def _get_client(self):
        return self._session.client(
            service_name="s3",
            endpoint_url=settings.MINIO_ENDPOINT,
            aws_access_key_id=settings.MINIO_ACCESS_KEY,
            aws_secret_access_key=settings.MINIO_SECRET_KEY,
        )

    async def save(
        self,
        prefix: str,
        filename: str | None,
        content: bytes
    ) -> None:
        async with await self._get_client() as client:
            await client.put_object(
                Bucket=settings.MINIO_IMAGE_BUCKET,
                Key=f"{prefix}/{filename}",
                Body=content,
            )

    async def delete(
            self,
            prefix: str,
            filename: str | None,
    ) -> None:
        if filename is None:
            return
        async with await self._get_client() as client:
            await client.delete_object(
                Bucket=settings.MINIO_IMAGE_BUCKET,
                Key=f"{prefix}/{filename}",
            )
