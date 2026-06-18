from app.users.interfaces import UserRepoABC, UserServiceABC


class UserService(UserServiceABC):
    repo: UserRepoABC

    async def register(self, email: str, name: str) -> dict:
        existing = await self.repo.get_by_email(email)
        if existing:
            raise ValueError("User with this email already exists")
        return await self.repo.create(email=email, name=name)

    async def get_user(self, user_id: int) -> dict:
        user = await self.repo.get_by_id(user_id)
        if not user:
            raise ValueError("User not found")
        return user
