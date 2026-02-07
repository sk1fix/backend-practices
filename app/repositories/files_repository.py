from sqlalchemy import select
from sqlalchemy.orm import Session

from models.models import Folders


class FilesRepository:
    def __init__(self, session) -> None:
        self.session = session

    async def create_file(self, data):
        pass