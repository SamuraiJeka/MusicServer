from fastapi import FastAPI

from entrypoints.audio_entrypoint import router as audio_router
from entrypoints.auth_entrypoint import router as auth_router
from entrypoints.chat_entrypoint import router as chat_router
from entrypoints.image_entrypoint import router as image_router
from entrypoints.user_entrypoint import router as user_router
from entrypoints.music_entrypoint import router as music_router
from entrypoints.ws_chat_entrypoint import router as ws_chat_router
from adapters.postgres.orm import start_mappers

app = FastAPI()

start_mappers()

app.include_router(auth_router)
app.include_router(user_router)
app.include_router(music_router)
app.include_router(audio_router)
app.include_router(image_router)
app.include_router(chat_router)
app.include_router(ws_chat_router)
