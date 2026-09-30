from database.base import session


async def get_db():
    """Сессия на запрос: одна транзакция, откат при исключении."""
    async with session() as db:
        try:
            yield db
        except Exception:
            await db.rollback()
            raise
