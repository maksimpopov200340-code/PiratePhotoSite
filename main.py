from fastapi import FastAPI, HTTPException, UploadFile, File, Query
from pydantic import BaseModel
import sqlite3
from repos.users_repo import UserRepo
#from models import UserModel
from sqlmodel import create_engine, SQLModel, select
from database import engine, create_db_and_tables, get_session, SessionDep
from models import UserBase, PostBase, CommentBase, PostImage  # импорт моделей
from minio import Minio
from minio.error import S3Error
import uuid
from datetime import timedelta
from respons import UserPublic, PostPublic, PostImagePublic, PostListItem


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


app = FastAPI()

#----------MINIO------------------------



minio_client = Minio(
    "localhost:9000",
    access_key="myAccessKey",
    secret_key="mySecretKey123",
    secure=False,  # потому что у тебя сейчас http, не https
)

BUCKET_NAME = "porno"

@app.on_event("startup")
def on_startup():
    create_db_and_tables()
    if not minio_client.bucket_exists(BUCKET_NAME):
        minio_client.make_bucket(BUCKET_NAME)

@app.get("/health/minio")
def minio_health():
    exists = minio_client.bucket_exists(BUCKET_NAME)
    return {"minio_ok": True, "bucket_exists": exists}


@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    try:
        object_name = f"{uuid.uuid4()}-{file.filename}"

        result = minio_client.put_object(
            BUCKET_NAME,
            object_name,
            data=file.file,
            length=-1,
            part_size=10 * 1024 * 1024,
            content_type=file.content_type,
        )

        return {
            "bucket": BUCKET_NAME,
            "object_name": object_name,
            "etag": result.etag,
            "version_id": result.version_id,
        }
    except S3Error as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@app.get("/files/{object_name}/url")
def get_presigned_url(object_name: str):
    url = minio_client.presigned_get_object(
        BUCKET_NAME,
        object_name,
        expires=timedelta(hours=1),
    )
    return {"url": url}

from typing import Annotated, Optional
from fastapi import FastAPI, Depends, HTTPException, UploadFile, File, Form
from sqlmodel import Session
from uuid import uuid4

ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/webp"}


@app.post("/posts/")
def create_post(
    title: Annotated[str, Form(...)],
    description: Annotated[str, Form(...)],
    user_id: Annotated[int, Form(...)],
    image: Annotated[Optional[UploadFile], File()] = None,
    session: Session = Depends(get_session),
):
    user = session.get(UserBase, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    post = PostBase(
        title=title,
        description=description,
        user_id=user_id,
    )
    session.add(post)
    session.commit()
    session.refresh(post)

    if image is not None:
        if image.content_type not in ALLOWED_IMAGE_TYPES:
            raise HTTPException(status_code=400, detail="Unsupported image type")

        ext = ""
        if image.filename and "." in image.filename:
            ext = "." + image.filename.rsplit(".", 1)[1].lower()

        object_name = f"posts/{post.id}/{uuid4().hex}{ext}"

        result = minio_client.put_object(
            BUCKET_NAME,
            object_name,
            data=image.file,
            length=-1,
            part_size=10 * 1024 * 1024,
            content_type=image.content_type,
            metadata={
                "post_id": str(post.id),
                "user_id": str(user_id),
            },
        )

        post_image = PostImage(
            post_id=post.id,
            bucket_name=BUCKET_NAME,
            object_name=object_name,
            original_filename=image.filename or "unknown",
            content_type=image.content_type,
        )
        session.add(post_image)
        session.commit()

    return {"message": "Post created", "post_id": post.id}

@app.get("/posts/{post_id}", response_model=PostPublic)
def read_post(post_id: int, session: Session = Depends(get_session)):
    post = session.get(PostBase, post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    images = []
    for img in post.images:
        url = minio_client.presigned_get_object(
            img.bucket_name,
            img.object_name,
            expires=timedelta(hours=1),
        )
        images.append(
            PostImagePublic(
                id=img.id,
                original_filename=img.original_filename,
                content_type=img.content_type,
                url=url,
            )
        )

    author = None
    if post.author:
        author = UserPublic(
            id=post.author.id,
            name=post.author.name,
        )

    return PostPublic(
        id=post.id,
        title=post.title,
        description=post.description,
        created_at=post.created_at,
        user_id=post.user_id,
        author=author,
        images=images,
    )

@app.get("/posts/", response_model=list[PostListItem])
def read_posts(
    session: Session = Depends(get_session),
    offset: int = 0,
    limit: int = Query(default=20, le=100),
):
    posts = session.exec(
        select(PostBase).offset(offset).limit(limit)
    ).all()

    result = []
    for post in posts:
        preview_url = None

        if post.images:
            first_image = post.images[0]
            preview_url = minio_client.presigned_get_object(
                first_image.bucket_name,
                first_image.object_name,
                expires=timedelta(hours=1),
            )

        result.append(
            PostListItem(
                id=post.id,
                title=post.title,
                description=post.description,
                created_at=post.created_at,
                user_id=post.user_id,
                image_preview=preview_url,
            )
        )

    return result

#-----------END--------------------------


@app.get("/users")
def get_users(session: SessionDep):
    from .models import UserBase
    users = session.exec(select(UserBase)).all()
    return users



@app.get("/users/{user_id}")
def get_user(user_id: int, session: SessionDep):   
    return UserRepo.get_user_by_id(user_id, session)

@app.post("/users/add")
def add_user(user: UserBase,session: SessionDep):
    return UserRepo.add_user(user.name, user.password, session)
     
# @app.post("/users/update")
# def update_user(user: UserModel):
#     return UserRepo.update_user_name(user.id, user.name)

# @app.delete("/users/{user_id}")
# def delete_user(user_id: int):   
#     return UserRepo.delete_user(user_id)




#connection_my.close()