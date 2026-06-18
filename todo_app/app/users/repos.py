from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker
from web_fractal.db import UnitOfWork

from app.users.interfaces import UserRepoABC
from app.users.models import UserORM


def _user_to_dict(user: UserORM) -> dict:
    return {"id": user.id, "email": user.email, "name": user.name}


class UserRepo(UserRepoABC):
    session_maker: async_sessionmaker

    async def create(self, email: str, name: str) -> dict:
        async with UnitOfWork(self.session_maker) as uow:
            session = uow.get_session()
            user = UserORM(email=email, name=name)
            session.add(user)
            await session.flush()
            await session.refresh(user)
            return _user_to_dict(user)

    async def get_by_id(self, user_id: int) -> dict | None:
        async with UnitOfWork(self.session_maker) as uow:
            session = uow.get_session()
            user = await session.scalar(select(UserORM).where(UserORM.id == user_id))
            return _user_to_dict(user) if user else None

    async def get_by_email(self, email: str) -> dict | None:
        async with UnitOfWork(self.session_maker) as uow:
            session = uow.get_session()
            user = await session.scalar(select(UserORM).where(UserORM.email == email))
            return _user_to_dict(user) if user else None
