from sqlalchemy import select
from sqlalchemy.orm import Session

from models.models import Users
from core.exceptions import UserAlreadyExistsException, UserNotFoundException


class AuthRepository:
    def __init__(self, session) -> None:
        self.session = session

    async def create_user(self, data):
        check_query = select(Users.id).where(Users.login == data.login)
        check_result = await self.session.execute(check_query)

        if check_result.scalar_one_or_none():
            raise UserAlreadyExistsException("логином", data.login)

        user = Users(**data.model_dump())
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)

        return user

    async def get_by_login(self, login):
        query = select(Users).where(Users.login == login)
        result = await self.session.execute(query)
        user = result.scalar_one_or_none()

        if not user:
            raise UserNotFoundException(f"логином: {login}")

        return user

    async def get_pass_by_login(self, login):
        query = select(Users).where(Users.login == login)
        result = await self.session.execute(query)
        user = result.scalar_one_or_none()

        if not user:
            raise UserNotFoundException(f"логином: {login}")

        return user

    async def get_by_id(self, id):
        query = select(Users).where(Users.id == id)
        result = await self.session.execute(query)
        user = result.scalar_one_or_none()

        if not user:
            raise UserNotFoundException(id)

        return True
