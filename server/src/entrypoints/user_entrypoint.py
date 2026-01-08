from fastapi import APIRouter, Depends

from entrypoints.dependencies import get_authenticated_user
from application.schemas.user_schema import UserSchema

router = APIRouter(prefix="/user", tags=["user"])


@router.get("/test", status_code=200)
async def user_test(
    user: UserSchema = Depends(get_authenticated_user),
):
    return f"pass!. USER_ID = {user.id}"
