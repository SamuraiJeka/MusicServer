from fastapi import APIRouter, UploadFile, Depends

from entrypoints.dependencies import get_authenticated_user, get_storage
from domain.ports.storage_interface import StorageInterface
from application.schemas.user_schema import UserSchema

router = APIRouter(prefix="/music", tags=["music"])


@router.post("/add_file")
async def upload_file(
    file: UploadFile,
    user: UserSchema = Depends(get_authenticated_user),
    storage: StorageInterface = Depends(get_storage),
):
    
    content = await file.read()

    await storage.save(
        prefix=str(user.id),
        filename=file.filename,
        content=content,
    )
