from contextlib import asynccontextmanager
import uvicorn
from fastapi import FastAPI

from api.controllers.login import auth
from core.config import settings



cloud_app = FastAPI()

cloud_app.include_router(auth)

if __name__ == "__main__":
    uvicorn.run(
        "main:cloud_app",
        host=settings.HOST,
        port=settings.PORT,
        reload=True
    )