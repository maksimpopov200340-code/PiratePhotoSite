import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parents[2]
load_dotenv(BASE_DIR / ".env")


def get_bool_env(name: str, default: bool = False) -> bool:
    value = os.environ.get(name)
    if value is None:
        return default

    return value.strip().lower() in {"1", "true", "yes", "on"}


if os.name == "nt" and os.environ.get("LOCALAPPDATA"):
    RUNTIME_ROOT = Path(os.environ["LOCALAPPDATA"]) / "PiratePhotoSite"
else:
    RUNTIME_ROOT = BASE_DIR / ".runtime"

DATA_DIR = RUNTIME_ROOT / "data"
MEDIA_DIR = RUNTIME_ROOT / "media"
POSTS_MEDIA_DIR = MEDIA_DIR / "posts"
DATABASE_PATH = DATA_DIR / "app.db"
DATABASE_URL = f"sqlite:///{DATABASE_PATH.resolve().as_posix()}"
API_PREFIX = "/api"
STORAGE_BACKEND = os.environ.get("STORAGE_BACKEND", "minio").strip().lower()
MINIO_ENDPOINT = os.environ.get("MINIO_ENDPOINT", "127.0.0.1:9000")
MINIO_ACCESS_KEY = os.environ.get("MINIO_ACCESS_KEY", "minioadmin")
MINIO_SECRET_KEY = os.environ.get("MINIO_SECRET_KEY", "minioadmin")
MINIO_BUCKET = os.environ.get("MINIO_BUCKET", "pirate-photo-site")
MINIO_REGION = os.environ.get("MINIO_REGION")
MINIO_SECURE = get_bool_env("MINIO_SECURE", default=False)
CORS_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:5173",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:5173",
]
ALLOWED_IMAGE_TYPES = {
    "image/jpeg",
    "image/png",
    "image/webp",
}


def ensure_directories() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    if STORAGE_BACKEND == "local":
        POSTS_MEDIA_DIR.mkdir(parents=True, exist_ok=True)
