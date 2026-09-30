from urllib.parse import quote

from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    Query,
    UploadFile,
    status
)
from fastapi.responses import StreamingResponse
from starlette.concurrency import iterate_in_threadpool

from api.dependencies import (
    enforce_content_length,
    get_current_user,
    get_files_service
)
from models.models import Users
from schemas.storage import FileRenameDto, FileResponseDto
from services.files import FilesService

files = APIRouter(prefix="/files", tags=["Files"])


def _content_disposition(filename: str) -> str:
    """RFC 6266/5987: ASCII-фолбэк + UTF-8 имя для браузеров."""
    ascii_name = filename.encode("ascii", "ignore").decode("ascii")
    ascii_name = ascii_name.replace('"', "").strip() or "file"

    return (
        f'attachment; filename="{ascii_name}"; '
        f"filename*=UTF-8''{quote(filename, safe='')}"
    )


@files.post(
    "/upload",
    summary="Загрузить файл",
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(enforce_content_length)],
)
async def upload(
        file: UploadFile = File(...),
        folder_id: int | None = Query(
            default=None,
            description="ID папки; не указан — корень",
        ),
        overwrite: bool = Query(
            default=False,
            description="Перезаписать файл с таким же именем",
        ),
        folder_id_field: int | None = Form(
            default=None,
            alias="folder_id",
            description="То же, что query-параметр folder_id",
        ),
        overwrite_field: bool | None = Form(
            default=None,
            alias="overwrite",
            description="То же, что query-параметр overwrite",
        ),
        user: Users = Depends(get_current_user),
        service: FilesService = Depends(get_files_service),
) -> FileResponseDto:
    resolved_folder_id = folder_id if folder_id is not None else folder_id_field
    resolved_overwrite = overwrite or bool(overwrite_field)

    return await service.upload(
        user, file, resolved_folder_id, resolved_overwrite)


@files.get("/{file_id}/download", summary="Скачать файл")
async def download(
        file_id: int,
        user: Users = Depends(get_current_user),
        service: FilesService = Depends(get_files_service),
) -> StreamingResponse:
    file, iterator = await service.open_download(user, file_id)

    return StreamingResponse(
        iterate_in_threadpool(iterator),
        media_type=file.mime_type,
        headers={
            "Content-Length": str(file.size),
            "Content-Disposition": _content_disposition(file.filename),
            "X-Content-Type-Options": "nosniff",
        },
    )


@files.patch("/{file_id}", summary="Переименовать файл")
async def rename_file(
        file_id: int,
        data: FileRenameDto,
        user: Users = Depends(get_current_user),
        service: FilesService = Depends(get_files_service),
) -> FileResponseDto:
    return await service.rename_file(user, file_id, data.filename)


@files.delete(
    "/{file_id}",
    summary="Удалить файл",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_file(
        file_id: int,
        user: Users = Depends(get_current_user),
        service: FilesService = Depends(get_files_service),
) -> None:
    await service.delete_file(user, file_id)
