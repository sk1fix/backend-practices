from sqlalchemy.ext.asyncio import AsyncSession


class BaseRepository:
    """Общий доступ к сессии и управление транзакцией.

    Все репозитории запроса используют одну и ту же AsyncSession, поэтому
    commit/rollback можно вызывать у любого из них — транзакция общая.
    """

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def commit(self) -> None:
        await self.session.commit()

    async def rollback(self) -> None:
        await self.session.rollback()
