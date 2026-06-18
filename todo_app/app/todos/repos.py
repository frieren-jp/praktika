from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker
from web_fractal.db import UnitOfWork

from app.todos.interfaces import TodoRepoABC
from app.todos.models import TodoORM


def _todo_to_dict(todo: TodoORM) -> dict:
    return {
        "id": todo.id,
        "title": todo.title,
        "completed": todo.completed,
        "user_id": todo.user_id,
    }


class TodoRepo(TodoRepoABC):
    session_maker: async_sessionmaker

    async def create(self, title: str, user_id: int) -> dict:
        async with UnitOfWork(self.session_maker) as uow:
            session = uow.get_session()
            todo = TodoORM(title=title, user_id=user_id, completed=False)
            session.add(todo)
            await session.flush()
            await session.refresh(todo)
            return _todo_to_dict(todo)

    async def list_by_user(self, user_id: int) -> list[dict]:
        async with UnitOfWork(self.session_maker) as uow:
            session = uow.get_session()
            result = await session.scalars(
                select(TodoORM).where(TodoORM.user_id == user_id).order_by(TodoORM.id)
            )
            return [_todo_to_dict(todo) for todo in result.all()]

    async def complete(self, todo_id: int) -> dict | None:
        async with UnitOfWork(self.session_maker) as uow:
            session = uow.get_session()
            todo = await session.scalar(select(TodoORM).where(TodoORM.id == todo_id))
            if not todo:
                return None
            todo.completed = True
            await session.flush()
            await session.refresh(todo)
            return _todo_to_dict(todo)
