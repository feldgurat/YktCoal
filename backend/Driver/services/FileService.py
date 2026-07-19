import logging
import uuid
from pathlib import Path
from typing import Annotated

from fastapi import Depends, UploadFile

from config import settings
from services.Exceptions import FileNotFoundInStorageError, InvalidUploadError

logger = logging.getLogger(__name__)

# Допустимые типы документов (паспорт, права, страховка, ПТС/СТС).
ALLOWED_CONTENT_TYPES = {
    "image/jpeg",
    "image/png",
    "image/webp",
    "application/pdf",
}

EXTENSION_BY_CONTENT_TYPE = {
    "image/jpeg": ".jpg",
    "image/png": ".png",
    "image/webp": ".webp",
    "application/pdf": ".pdf",
}


class FileService:
    def __init__(self) -> None:
        self._uploads_dir = Path(settings.UPLOADS_DIR)
        self._uploads_dir.mkdir(parents=True, exist_ok=True)
        self._max_bytes = settings.UPLOAD_MAX_BYTES

    async def save_upload(self, file: UploadFile) -> str:
        """
        Сохраняет загруженный файл в UPLOADS_DIR и возвращает имя файла
        (без префикса каталога) — это значение нужно подставлять
        в поля license_url, passport и т.д.
        """
        if file.content_type not in ALLOWED_CONTENT_TYPES:
            raise InvalidUploadError(
                f"Недопустимый тип файла: {file.content_type}. "
                f"Разрешены: {', '.join(sorted(ALLOWED_CONTENT_TYPES))}"
            )

        # Читаем в память (упрощённо, до UPLOAD_MAX_BYTES) с проверкой размера.
        content = await file.read()
        if len(content) > self._max_bytes:
            raise InvalidUploadError(
                f"Файл слишком большой: {len(content)} байт, максимум {self._max_bytes}"
            )
        if len(content) == 0:
            raise InvalidUploadError("Пустой файл")

        ext = EXTENSION_BY_CONTENT_TYPE[file.content_type]
        filename = f"{uuid.uuid4()}{ext}"
        full_path = self._uploads_dir / filename

        # Защита от path traversal: full_path должен быть строго внутри uploads_dir.
        try:
            full_path.resolve().relative_to(self._uploads_dir.resolve())
        except ValueError:
            raise InvalidUploadError("Некорректное имя файла") from None

        full_path.write_bytes(content)
        logger.info("Saved upload: %s (%d bytes)", filename, len(content))
        return filename

    def get_file_path(self, filename: str) -> Path:
        """
        Возвращает абсолютный путь к файлу, проверяя что он лежит внутри UPLOADS_DIR.
        Защита от path traversal через имя вида "../../etc/passwd".
        """
        full_path = (self._uploads_dir / filename).resolve()
        try:
            full_path.relative_to(self._uploads_dir.resolve())
        except ValueError:
            raise FileNotFoundInStorageError() from None

        if not full_path.is_file():
            raise FileNotFoundInStorageError()
        return full_path


def get_file_service() -> FileService:
    return FileService()


FileServiceDep = Annotated[FileService, Depends(get_file_service)]
