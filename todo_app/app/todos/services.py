from app.todos.interfaces import TodoRepoABC, TodoServiceABC
from app.users.interfaces import UserServiceABC


class TodoService(TodoServiceABC):
    repo: TodoRepoABC
    user_service: UserServiceABC

    async def create_todo(self, title: str, user_id: int) -> dict:
        await self.user_service.get_user(user_id)
        return await self.repo.create(title=title, user_id=user_id)

    async def list_user_todos(self, user_id: int) -> list[dict]:
        await self.user_service.get_user(user_id)
        return await self.repo.list_by_user(user_id=user_id)

    async def complete_todo(self, todo_id: int) -> dict:
        todo = await self.repo.complete(todo_id=todo_id)
        if not todo:
            raise ValueError("Todo not found")
        return todo
