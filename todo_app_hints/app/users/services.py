# ПОДСКАЗКА: services.py - DomainLayer.
# Здесь бизнес-логика пользователей, но нет SQLAlchemy и FastAPI.

# UserRepoABC - интерфейс репозитория.
# UserServiceABC - интерфейс сервиса, который реализует этот класс.
from app.users.interfaces import UserRepoABC, UserServiceABC


# ПОДСКАЗКА: UserService реализует UserServiceABC.
# archtool найдет этот класс в services.py и зарегистрирует как реализацию UserServiceABC.
class UserService(UserServiceABC):
    # repo - зависимость от абстракции UserRepoABC.
    # archtool внедрит сюда экземпляр UserRepo.
    repo: UserRepoABC

    # Сценарий регистрации пользователя.
    async def register(self, email: str, name: str) -> dict:
        # Сначала проверяем, нет ли пользователя с таким email.
        existing = await self.repo.get_by_email(email)
        # Если пользователь уже есть, бизнес-логика запрещает дубль.
        if existing:
            raise ValueError("User with this email already exists")
        # Если email свободен, просим репозиторий создать запись.
        return await self.repo.create(email=email, name=name)

    # Сценарий получения пользователя.
    async def get_user(self, user_id: int) -> dict:
        # Репозиторий возвращает dict или None.
        user = await self.repo.get_by_id(user_id)
        # Если пользователя нет, сервис бросает бизнес-ошибку.
        if not user:
            raise ValueError("User not found")
        # Если есть - возвращаем данные выше, в контроллер.
        return user
