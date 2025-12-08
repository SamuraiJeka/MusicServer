from fastapi import FastAPI

from entrypoints.login_entypoint import router as login_router
from entrypoints.user_entrypoint import router as user_router

app = FastAPI()


app.include_router(login_router)
app.include_router(user_router)
