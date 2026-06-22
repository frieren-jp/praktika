# ПОДСКАЗКА: services.py - DomainLayer для задач.
# Здесь находится бизнес-логика todos и кросс-модульная зависимость на users.

# TodoRepoABC - интерфейс репозитория задач.
# TodoServiceABC - интерфейс сервиса задач.
from app.todos.interfaces import TodoRepoABC, TodoServiceABC

# UserServiceABC - интерфейс сервиса пользователей из другого bounded context.
# Это главный пример кросс-модульной зависимости.
from app.users.interfaces import UserServiceABC


# ПОДСКАЗКА: TodoService реализует TodoServiceABC.
class TodoService(TodoServiceABC):
    # repo будет внедрен archtool как реализация TodoRepoABC -> TodoRepo.
    repo: TodoRepoABC

    # user_service будет внедрен archtool из другого модуля: UserServiceABC -> UserService.
    user_service: UserServiceABC

    # Создание задачи.
    async def create_todo(self, title: str, user_id: int) -> dict:
        # Перед созданием задачи проверяем, что пользователь существует.
        # Если пользователя нет, UserService бросит ValueError.
        await self.user_service.get_user(user_id)
        # Если пользователь есть, создаем задачу через репозиторий.
        return await self.repo.create(title=title, user_id=user_id)

    # Получение задач пользователя.
    async def list_user_todos(self, user_id: int) -> list[dict]:
        # Сначала снова проверяем существование пользователя.
        await self.user_service.get_user(user_id)
        # Потом возвращаем список задач этого пользователя.
        return await self.repo.list_by_user(user_id=user_id)

    # Отметить задачу выполненной.
    async def complete_todo(self, todo_id: int) -> dict:
        # Репозиторий пытается найти задачу и поставить completed=True.
        todo = await self.repo.complete(todo_id=todo_id)
        # Если задачи нет, сервис превращает None в бизнес-ошибку.
        if not todo:
            raise ValueError("Todo not found")
        # Если задача найдена, возвращаем обновленные данные.
        return todo
