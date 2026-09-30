from fastapi import HTTPException, status


class UserAlreadyExistsException(HTTPException):
    def __init__(self, field: str, value: str):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Пользователь с таким {field} уже существует: {value}"
        )


class UserNotFoundException(HTTPException):
    def __init__(self, identifier: str):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Пользователь не найден: {identifier}"
        )


class InvalidCredentialsException(HTTPException):
    def __init__(self, detail: str = "Неверные учетные данные"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail
        )


class InvalidTokenException(HTTPException):
    def __init__(
            self,
            detail: str = "Недействительный или просроченный токен"
    ):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            headers={"WWW-Authenticate": "Bearer"}
        )


class InsufficientPermissionsException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Недостаточно прав для выполнения операции"
        )


class FolderNotFoundException(HTTPException):
    def __init__(self, identifier: str | int):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Папка не найдена: {identifier}"
        )


class FolderAlreadyExistsException(HTTPException):
    def __init__(self, name: str):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Папка с именем «{name}» уже существует в текущей папке"
        )


class FileNotFoundException(HTTPException):
    def __init__(self, identifier: str | int):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Файл не найден: {identifier}"
        )


class FileAlreadyExistsException(HTTPException):
    def __init__(self, name: str):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                f"Файл с именем «{name}» уже существует. "
                "Подтвердите перезапись."
            )
        )


class InvalidNameException(HTTPException):
    def __init__(self, detail: str):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=detail
        )


class FileTooLargeException(HTTPException):
    def __init__(self, limit: int):
        super().__init__(
            status_code=status.HTTP_413_CONTENT_TOO_LARGE,
            detail=(
                "Файл превышает максимально допустимый размер "
                f"({limit} байт)"
            )
        )


class StorageQuotaExceededException(HTTPException):
    def __init__(self, required: int, available: int):
        super().__init__(
            status_code=status.HTTP_413_CONTENT_TOO_LARGE,
            detail=(
                "Недостаточно свободного места в хранилище: "
                f"требуется {required} байт, доступно {available} байт"
            )
        )


class StorageUnavailableException(HTTPException):
    def __init__(self, detail: str = "Хранилище временно недоступно"):
        super().__init__(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=detail
        )
