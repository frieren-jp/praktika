# ПОДСКАЗКА: repos.py - InfrastructureLayer для задач.
# Здесь находится работа с таблицей todos через SQLAlchemy.

# select нужен для SQL SELECT-запросов.
from sqlalchemy import select

# Тип фабрики async-сессий.
from sqlalchemy.ext.asyncio import async_sessionmaker

# UnitOfWork управляет сессией и транзакцией.
from web_fractal.db import UnitOfWork

# Интерфейс репозитория задач.
from app.todos.interfaces import TodoRepoABC

# ORM-модель таблицы todos.
from app.todos.models import TodoORM


# ПОДСКАЗКА: helper превращает TodoORM в dict для ответа API.
def _todo_to_dict(todo: TodoORM) -> dict:
    # Возвращаем id, title, completed и user_id.
    return {
        "id": todo.id,
        "title": todo.title,
        "completed": todo.completed,
        "user_id": todo.user_id,
    }


# ПОДСКАЗКА: TodoRepo реализует TodoRepoABC.
# archtool найдет эту пару: TodoRepoABC -> TodoRepo().
class TodoRepo(TodoRepoABC):
    # session_maker внедряется archtool из injector.register().
    session_maker: async_sessionmaker

    # Создание задачи в БД.
    async def create(self, title: str, user_id: int) -> dict:
        # Открываем UnitOfWork для одной транзакции.
        async with UnitOfWork(self.session_maker) as uow:
            # Берем AsyncSession из UnitOfWork.
            session = uow.get_session()
            # Создаем ORM-объект задачи.
            todo = TodoORM(title=title, user_id=user_id, completed=False)
            # Добавляем задачу в сессию.
            session.add(todo)
            # flush делает INSERT и позволяет получить todo.id.
            await session.flush()
            # refresh обновляет объект из БД.
            await session.refresh(todo)
            # Возвращаем plain dict.
            return _todo_to_dict(todo)

    # Получение всех задач пользователя.
    async def list_by_user(self, user_id: int) -> list[dict]:
        # Открываем UnitOfWork.
        async with UnitOfWork(self.session_maker) as uow:
            # Получаем сессию.
            session = uow.get_session()
            # Выполняем SELECT todos WHERE user_id = ... ORDER BY id.
            result = await session.scalars(
                select(TodoORM).where(TodoORM.user_id == user_id).order_by(TodoORM.id)
            )
            # Превращаем список ORM-объектов в список dict.
            return [_todo_to_dict(todo) for todo in result.all()]

    # Отметка задачи выполненной.
    async def complete(self, todo_id: int) -> dict | None:
        # Открываем UnitOfWork.
        async with UnitOfWork(self.session_maker) as uow:
            # Получаем сессию.
            session = uow.get_session()
            # Ищем задачу по id.
            todo = await session.scalar(select(TodoORM).where(TodoORM.id == todo_id))
            # Если задачи нет - возвращаем None, сервис превратит это в ошибку.
            if not todo:
                return None
            # Меняем поле completed.
            todo.completed = True
            # flush отправляет UPDATE в БД.
            await session.flush()
            # refresh обновляет объект после UPDATE.
            await session.refresh(todo)
            # Возвращаем обновленную задачу.
            return _todo_to_dict(todo)
