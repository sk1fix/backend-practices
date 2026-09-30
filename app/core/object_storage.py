import logging
from collections.abc import Iterable, Iterator

from minio import Minio
from minio.commonconfig import CopySource
from minio.deleteobjects import DeleteObject
from minio.error import S3Error

from core.config import settings
from core.exceptions import (
    FileNotFoundException,
    StorageUnavailableException
)

logger = logging.getLogger(__name__)

CHUNK_SIZE = 1024 * 1024
DELETE_BATCH_SIZE = 1000


class ObjectStorage:
    """Обёртка над minio-py.

    Клиент minio-py блокирующий, поэтому все методы синхронные: вызывать их
    следует через anyio.to_thread / starlette.concurrency.iterate_in_threadpool.
    """

    def __init__(
            self,
            endpoint: str,
            access_key: str,
            secret_key: str,
            secure: bool = False,
            region: str = "us-east-1",
    ):
        self.endpoint = endpoint
        self._client = Minio(
            endpoint=endpoint,
            access_key=access_key,
            secret_key=secret_key,
            secure=secure,
            region=region,
        )

    @staticmethod
    def bucket_name(user_id: int) -> str:
        """Бакет на пользователя: допускается только [a-z0-9-], 3-63 символа."""
        return f"user-{user_id}"

    def ensure_bucket(self, bucket: str) -> None:
        try:
            if not self._client.bucket_exists(bucket):
                self._client.make_bucket(bucket)
                logger.info("Создан бакет %s", bucket)
        except S3Error as error:
            if error.code in ("BucketAlreadyOwnedByYou", "BucketAlreadyExists"):
                return
            raise self._unavailable("не удалось создать бакет", error) from error

    def list_keys(self, bucket: str, prefix: str = "") -> Iterator[str]:
        try:
            for obj in self._client.list_objects(
                    bucket, prefix=prefix, recursive=True):
                yield obj.object_name
        except S3Error as error:
            raise self._unavailable("не удалось получить список объектов", error)

    def put_object(
            self,
            bucket: str,
            key: str,
            stream,
            length: int,
            content_type: str,
    ) -> None:
        try:
            self._client.put_object(
                bucket,
                key,
                stream,
                length,
                content_type=content_type,
            )
        except S3Error as error:
            if error.code == "NoSuchBucket":
                self.ensure_bucket(bucket)
                if hasattr(stream, "seek"):
                    stream.seek(0)
                self.put_object(bucket, key, stream, length, content_type)
                return
            raise self._unavailable("не удалось загрузить объект", error) from error

    def iter_object(
            self,
            bucket: str,
            key: str,
            chunk_size: int = CHUNK_SIZE,
    ) -> Iterator[bytes]:
        response = self._open_object(bucket, key)

        try:
            for chunk in response.stream(chunk_size):
                if chunk:
                    yield chunk
        finally:
            response.close()
            response.release_conn()

    def stat_object(self, bucket: str, key: str) -> None:
        """Проверяет наличие объекта, не начиная читать его тело."""
        try:
            self._client.stat_object(bucket, key)
        except S3Error as error:
            if error.code in ("NoSuchKey", "NoSuchBucket"):
                raise FileNotFoundException(key) from error
            raise self._unavailable("не удалось получить объект", error) from error

    def copy_object(self, bucket: str, source_key: str, target_key: str) -> None:
        try:
            self._client.copy_object(
                bucket,
                target_key,
                CopySource(bucket, source_key),
            )
        except S3Error as error:
            raise self._unavailable("не удалось скопировать объект", error) from error

    def remove_object(self, bucket: str, key: str) -> None:
        try:
            self._client.remove_object(bucket, key)
        except S3Error as error:
            if error.code in ("NoSuchKey", "NoSuchBucket"):
                return
            raise self._unavailable("не удалось удалить объект", error) from error

    def remove_objects(self, bucket: str, keys: Iterable[str]) -> int:
        """Пакетное удаление. Возвращает число успешно удалённых объектов."""
        objects = list(keys)
        removed = 0

        for start in range(0, len(objects), DELETE_BATCH_SIZE):
            batch = [
                DeleteObject(key)
                for key in objects[start:start + DELETE_BATCH_SIZE]
            ]
            try:
                errors = list(self._client.remove_objects(bucket, batch))
            except S3Error as error:
                raise self._unavailable("не удалось удалить объекты", error) from error

            for delete_error in errors:
                logger.error(
                    "Не удалось удалить объект %s: %s",
                    delete_error.object_name,
                    delete_error.message,
                )

            removed += len(batch) - len(errors)

        return removed

    def remove_prefix(self, bucket: str, prefix: str) -> int:
        keys = list(self.list_keys(bucket, prefix))
        if not keys:
            return 0

        removed = self.remove_objects(bucket, keys)
        logger.info("Удалено объектов по префиксу %s/%s: %s", bucket, prefix, removed)
        return removed

    def move_prefix(self, bucket: str, old_prefix: str, new_prefix: str) -> int:
        """Перемещает все объекты с одного префикса на другой (copy + delete)."""
        keys = list(self.list_keys(bucket, old_prefix))
        if not keys:
            return 0

        moved_keys: list[str] = []

        for key in keys:
            target_key = f"{new_prefix}{key[len(old_prefix):]}"
            self.copy_object(bucket, key, target_key)
            moved_keys.append(key)

        self.remove_objects(bucket, moved_keys)
        logger.info(
            "Перемещено объектов %s -> %s: %s",
            old_prefix,
            new_prefix,
            len(moved_keys),
        )
        return len(moved_keys)

    def health(self) -> bool:
        try:
            self._client.list_buckets()
            return True
        except Exception as error:  # noqa: BLE001 - health-check не должен падать
            logger.error("MinIO недоступен: %s", error)
            return False

    def _open_object(self, bucket: str, key: str):
        try:
            return self._client.get_object(bucket, key)
        except S3Error as error:
            if error.code in ("NoSuchKey", "NoSuchBucket"):
                raise FileNotFoundException(key) from error
            raise self._unavailable("не удалось прочитать объект", error) from error

    @staticmethod
    def _unavailable(action: str, error: Exception) -> StorageUnavailableException:
        logger.error("MinIO: %s (%s): %s", action, error.__class__.__name__, error)
        return StorageUnavailableException()


def get_object_storage() -> ObjectStorage:
    return ObjectStorage(
        endpoint=settings.MINIO_ENDPOINT,
        access_key=settings.MINIO_ROOT_USER,
        secret_key=settings.MINIO_ROOT_PASSWORD,
        secure=settings.MINIO_SECURE,
        region=settings.MINIO_REGION,
    )
