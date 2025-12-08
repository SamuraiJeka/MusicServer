from fastapi import APIRouter

router = APIRouter(prefix="/user", tags=["user"])


@router.get("/test", status_code=200)
async def user_test():
    return "test"
