from database.base import session


async def get_db():
    db = session()
    try:
        yield db
    finally:
        await db.close()