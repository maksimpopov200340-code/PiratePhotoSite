from fastapi import APIRouter
from fastapi.responses import Response

from ..storage import get_media_response


router = APIRouter(tags=["media"])


@router.get("/media/{file_path:path}", include_in_schema=False)
def get_media(file_path: str) -> Response:
    return get_media_response(file_path)
