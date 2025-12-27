from fastapi import FastAPI

from entrypoints.auth_entrypoint import router as auth_router
from entrypoints.user_entrypoint import router as user_router
from adapters.postgres.orm import start_mappers

app = FastAPI()

start_mappers()

app.include_router(auth_router)
app.include_router(user_router)
