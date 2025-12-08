import uvicorn
from fastapi import FastAPI

from entrypoints.login_entypoint import router as login_router

app = FastAPI()


app.include_router(login_router)


uvicorn.run(app=app, host="127.0.0.1", port=8000)
