from database.base import session


async def get_db():
    async with session() as db:
        yield db