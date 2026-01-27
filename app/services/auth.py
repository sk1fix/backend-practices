

class AuthService:
    def __init__(self, repo):
        self.repo = repo
        
    async def register_user(self, data):
        result = await self.repo.post(data)
        return result