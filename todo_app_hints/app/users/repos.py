# ПОДСКАЗКА: repos.py - InfrastructureLayer.
# Репозиторий знает про SQLAlchemy и БД, но не должен знать про HTTP.

# select строит SQL SELECT-запросы.
from sqlalchemy import select

# async_sessionmaker - тип фабрики async-сессий.
from sqlalchemy.ext.asyncio import async_sessionmaker

# UnitOfWork управляет транзакцией: commit при успехе, rollback при ошибке.
from web_fractal.db import UnitOfWork

# Импортируем интерфейс, который реализует UserRepo.
from app.users.interfaces import UserRepoABC

# Импортируем ORM-модель таблицы users.
from app.users.models import UserORM


# ПОДСКАЗКА: helper для преобразования ORM-объекта в простой dict.
# Контроллеру и сервису не нужно знать про SQLAlchemy-объекты.
def _user_to_dict(user: UserORM) -> dict:
    # Возвращаем только публичные поля пользователя.
    return {"id": user.id, "email": user.email, "name": user.name}


# ПОДСКАЗКА: UserRepo наследует UserRepoABC.
# Так archtool понимает, что UserRepo - реализация интерфейса UserRepoABC.
class UserRepo(UserRepoABC):
    # session_maker будет внедрен archtool во втором проходе.
    # Он зарегистрирован вручную в bundle_project.py через injector.register().
    session_maker: async_sessionmaker

    # Метод создает пользователя в БД.
    async def create(self, email: str, name: str) -> dict:
        # Открываем UnitOfWork: внутри создается сессия и начинается транзакция.
        async with UnitOfWork(self.session_maker) as uow:
            # Получаем текущую AsyncSession из UnitOfWork.
            session = uow.get_session()
            # Создаем ORM-объект, но пока он только в памяти.
            user = UserORM(email=email, name=name)
            # Добавляем ORM-объект в сессию.
            session.add(user)
            # flush отправляет INSERT в БД, чтобы получить id до commit.
            await session.flush()
            # refresh перечитывает объект из БД, чтобы поля точно были актуальны.
            await session.refresh(user)
            # Возвращаем dict, а не ORM-модель.
            return _user_to_dict(user)

    # Метод ищет пользователя по id.
    async def get_by_id(self, user_id: int) -> dict | None:
        # Каждая простая операция открывает свой UnitOfWork.
        async with UnitOfWork(self.session_maker) as uow:
            # Получаем сессию.
            session = uow.get_session()
            # Выполняем SELECT users WHERE id = user_id.
            user = await session.scalar(select(UserORM).where(UserORM.id == user_id))
            # Если пользователь найден - возвращаем dict, иначе None.
            return _user_to_dict(user) if user else None

    # Метод ищет пользователя по email.
    async def get_by_email(self, email: str) -> dict | None:
        # Открываем транзакцию/сессию через UnitOfWork.
        async with UnitOfWork(self.session_maker) as uow:
            # Получаем AsyncSession.
            session = uow.get_session()
            # Выполняем SELECT users WHERE email = email.
            user = await session.scalar(select(UserORM).where(UserORM.email == email))
            # Возвращаем dict или None.
            return _user_to_dict(user) if user else None
