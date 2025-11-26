from fastapi import FastAPI

from entrypoints.login_entypoint import router as login_router

app = FastAPI()


app.include_router(login_router)
