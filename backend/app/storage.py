import mimetypes
import shutil
from io import BytesIO
from pathlib import Path
from typing import Optional
from uuid import uuid4

from fastapi import HTTPException, UploadFile
from fastapi.responses import FileResponse, Response
from minio import Minio
from minio.error import S3Error

from .config import (
    ALLOWED_IMAGE_TYPES,
    MEDIA_DIR,
    MINIO_ACCESS_KEY,
    MINIO_BUCKET,
    MINIO_ENDPOINT,
    MINIO_REGION,
    MINIO_SECRET_KEY,
    MINIO_SECURE,
    POSTS_MEDIA_DIR,
    STORAGE_BACKEND,
    ensure_directories,
)


ensure_directories()


def get_minio_client() -> Minio:
    return Minio(
        endpoint=MINIO_ENDPOINT,
        access_key=MINIO_ACCESS_KEY,
        secret_key=MINIO_SECRET_KEY,
        secure=MINIO_SECURE,
    )


def prepare_storage() -> None:
    ensure_directories()
    if STORAGE_BACKEND == "local":
        return

    if STORAGE_BACKEND != "minio":
        raise RuntimeError(f"Unsupported storage backend: {STORAGE_BACKEND}")

    client = get_minio_client()
    try:
        if client.bucket_exists(MINIO_BUCKET):
            return

        if MINIO_REGION:
            client.make_bucket(MINIO_BUCKET, location=MINIO_REGION)
        else:
            client.make_bucket(MINIO_BUCKET)
    except Exception as error:
        raise RuntimeError(
            f"Could not prepare MinIO bucket '{MINIO_BUCKET}'."
        ) from error


def save_post_image(
    post_id: int,
    image: Optional[UploadFile],
) -> Optional[tuple[str, str]]:
    if image is None:
        return None

    if image.content_type not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(status_code=400, detail="Unsupported image type.")

    suffix = Path(image.filename or "").suffix.lower()
    file_name = f"{uuid4().hex}{suffix}"
    file_path = f"posts/{post_id}/{file_name}"

    try:
        if STORAGE_BACKEND == "minio":
            save_minio_image(file_path=file_path, image=image)
        elif STORAGE_BACKEND == "local":
            save_local_image(post_id=post_id, file_name=file_name, image=image)
        else:
            raise RuntimeError(f"Unsupported storage backend: {STORAGE_BACKEND}")
    except Exception as error:
        raise HTTPException(status_code=500, detail="Could not save image.") from error

    return file_name, file_path


def build_media_url(file_path: Optional[str]) -> Optional[str]:
    if not file_path:
        return None

    return f"/media/{file_path}"


def get_media_response(file_path: str) -> Response:
    if STORAGE_BACKEND == "minio":
        return get_minio_media(file_path)

    if STORAGE_BACKEND == "local":
        return get_local_media(file_path)

    raise HTTPException(status_code=500, detail="Storage backend is misconfigured.")


def save_local_image(post_id: int, file_name: str, image: UploadFile) -> None:
    post_directory = POSTS_MEDIA_DIR / str(post_id)
    post_directory.mkdir(parents=True, exist_ok=True)

    saved_path = post_directory / file_name
    image.file.seek(0)
    with saved_path.open("wb") as file_buffer:
        shutil.copyfileobj(image.file, file_buffer)


def save_minio_image(file_path: str, image: UploadFile) -> None:
    image.file.seek(0)
    image_bytes = image.file.read()
    image_stream = BytesIO(image_bytes)

    client = get_minio_client()
    client.put_object(
        bucket_name=MINIO_BUCKET,
        object_name=file_path,
        data=image_stream,
        length=len(image_bytes),
        content_type=image.content_type,
    )


def get_local_media(file_path: str) -> FileResponse:
    resolved_path = resolve_local_media_path(file_path)
    return FileResponse(
        path=resolved_path,
        media_type=guess_media_type(file_path),
    )


def get_minio_media(file_path: str) -> Response:
    object_response = None
    try:
        object_response = get_minio_client().get_object(MINIO_BUCKET, file_path)
        content = object_response.read()
        media_type = object_response.headers.get("Content-Type")
    except S3Error as error:
        if error.code in {"NoSuchKey", "NoSuchObject", "NoSuchBucket"}:
            raise HTTPException(status_code=404, detail="File not found.") from error

        raise HTTPException(status_code=500, detail="Could not load image.") from error
    except Exception as error:
        raise HTTPException(status_code=500, detail="Could not load image.") from error
    finally:
        if object_response is not None:
            object_response.close()
            object_response.release_conn()

    return Response(
        content=content,
        media_type=media_type or guess_media_type(file_path),
    )


def resolve_local_media_path(file_path: str) -> Path:
    media_root = MEDIA_DIR.resolve()
    resolved_path = (MEDIA_DIR / file_path).resolve()

    try:
        resolved_path.relative_to(media_root)
    except ValueError as error:
        raise HTTPException(status_code=404, detail="File not found.") from error

    if not resolved_path.is_file():
        raise HTTPException(status_code=404, detail="File not found.")

    return resolved_path


def guess_media_type(file_path: str) -> str:
    media_type, _ = mimetypes.guess_type(file_path)
    return media_type or "application/octet-stream"
