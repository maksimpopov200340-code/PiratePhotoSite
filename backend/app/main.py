from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import API_PREFIX, CORS_ORIGINS, ensure_directories
from .database import create_db_and_tables
from .routers import comments, health, media, posts, users
from .storage import prepare_storage


@asynccontextmanager
async def lifespan(_: FastAPI):
    ensure_directories()
    prepare_storage()
    create_db_and_tables()
    yield


app = FastAPI(
    title="PiratePhotoSite API",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(media.router)
app.include_router(health.router, prefix=API_PREFIX)
app.include_router(users.router, prefix=API_PREFIX)
app.include_router(posts.router, prefix=API_PREFIX)
app.include_router(comments.router, prefix=API_PREFIX)
