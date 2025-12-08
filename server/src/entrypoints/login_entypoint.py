from fastapi import APIRouter

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/registration", status_code=201)
async def registration():
    return "reg"
