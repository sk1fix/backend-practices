from sqlalchemy import select
from sqlalchemy.orm import Session

from models.models import Users


class AuthRepository:
    def __init__(self, session) -> None:
        self.session = session

    async def create_user(self, data):
        user = Users(**data.model_dump())
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)

        return user

    async def get_by_login(self, data):
        query = select(Users).where(data == Users.login)
        result = await self.session.execute(query)

        return result.scalars().first()

    async def get_by_username(self, data):
        query = select(Users).where(data == Users.username)
        result = await self.session.execute(query)

        return result.scalars().first()

    async def get_pass_by_login(self, data):
        query = select(Users).where(data == Users.login)
        result = await self.session.execute(query)

        return result.scalars().first()
