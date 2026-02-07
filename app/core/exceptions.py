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
