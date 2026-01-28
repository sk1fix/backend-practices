from sqlalchemy import select
from sqlalchemy.orm import Session

from models.models import Users


class AuthRepository:
    def __init__(self, session) -> None:
        self.session = session

    async def post(self, data):
        user = Users(**data.model_dump())
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)

        return user