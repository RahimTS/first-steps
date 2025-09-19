from fastapi import FastAPI
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase, AsyncIOMotorGridFSBucket
from contextlib import asynccontextmanager
from config.settings import settings
from loguru import logger
from datetime import datetime
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os

from routers.user_router import router as user_router


@asynccontextmanager
async def lifespan(app: FastAPI):

    app.mongo_client: AsyncIOMotorClient = AsyncIOMotorClient(settings.mongo_uri)
    app.mongo_db: AsyncIOMotorDatabase = app.mongo_client[settings.mongo_db]
    app.mongodb_fs: AsyncIOMotorGridFSBucket = AsyncIOMotorGridFSBucket(app.mongo_db)

    logger.info(f"[{datetime.now()}] MongoDB connected to {settings.mongo_uri}/{settings.mongo_db}")

    yield

    app.mongo_client.close()
    logger.info(f" MongoDB disconnected")


app = FastAPI(title=settings.app_name, lifespan=lifespan)

orginins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=orginins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(user_router)

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=int(settings.port),
        reload=settings.debug_mode,
        timeout_keep_alive=5,
        reload_dirs=[os.getcwd()],
    )

    