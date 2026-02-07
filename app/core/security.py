from datetime import datetime, timedelta

import jwt
from jose import JWTError
from passlib.context import CryptContext

from core.config import settings
from core.exceptions import InvalidTokenException


pwd_context = CryptContext(
    schemes=["argon2"],
    deprecated="auto"
)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def create_token(data: dict) -> str:
    payload = {
        **data,
        "exp": datetime.utcnow() + timedelta(hours=48),
        "iat": datetime.utcnow()
    }

    return jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")


def get_user_data_from_token(token: str) -> dict:
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=["HS256"]
        )

        exp_timestamp = payload.get("exp")
        exp_datetime = datetime.fromtimestamp(exp_timestamp)
        if datetime.utcnow() > exp_datetime:
            raise InvalidTokenException("Срок действия токена истек")

        return {
            "user_id": payload.get("user_id"),
            "username": payload.get("username"),
            "login": payload.get("sub"),
            "is_admin": payload.get("is_admin", False)
        }
    except JWTError:
        return None
