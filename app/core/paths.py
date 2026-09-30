"""Валидация имён и работа с логическими путями внутри бакета.

Путь папки не начинается и не заканчивается на «/», корень — пустая строка.
Ключ объекта в S3 — это путь папки и имя файла через «/».
"""
import posixpath

from core.exceptions import InvalidNameException

FORBIDDEN_CHARS = ("/", "\\")
RESERVED_NAMES = (".", "..")
MAX_NAME_LENGTH = 255


def validate_name(name: str | None) -> str:
    cleaned = (name or "").strip()

    if not cleaned:
        raise InvalidNameException("Имя не может быть пустым")

    if len(cleaned) > MAX_NAME_LENGTH:
        raise InvalidNameException(
            f"Имя не может быть длиннее {MAX_NAME_LENGTH} символов"
        )

    if cleaned in RESERVED_NAMES:
        raise InvalidNameException(f"Имя «{cleaned}» недопустимо")

    for char in FORBIDDEN_CHARS:
        if char in cleaned:
            raise InvalidNameException(
                f"Имя не может содержать символ «{char}»"
            )

    if any(ord(char) < 32 for char in cleaned):
        raise InvalidNameException(
            "Имя не может содержать управляющие символы"
        )

    return cleaned


def join_path(parent_path: str, name: str) -> str:
    return f"{parent_path}/{name}" if parent_path else name


def folder_prefix(folder_path: str) -> str:
    """Префикс ключей всех объектов внутри папки (включая вложенные)."""
    return f"{folder_path}/" if folder_path else ""


def build_storage_key(folder_path: str, filename: str) -> str:
    return join_path(folder_path, filename)


def path_segments(folder_path: str) -> list[str]:
    return [segment for segment in folder_path.split("/") if segment]


def cumulative_paths(folder_path: str) -> list[str]:
    """['a/b/c'] -> ['a', 'a/b', 'a/b/c'] — для построения хлебных крошек."""
    segments = path_segments(folder_path)
    return [
        "/".join(segments[:index + 1])
        for index in range(len(segments))
    ]


def path_name(folder_path: str) -> str:
    return posixpath.basename(folder_path)


def parent_path_of(folder_path: str) -> str:
    """'a/b/c' -> 'a/b', 'a' -> '', '' -> ''."""
    return posixpath.dirname(folder_path)
