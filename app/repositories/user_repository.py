from sqlalchemy import select
from sqlalchemy.orm import Session

from models.models import User


class UserRepository:
    def __init__(self, session) -> None:
        self.session = session

    async def get(self):
        pass