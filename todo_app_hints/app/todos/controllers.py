# ПОДСКАЗКА: controllers.py - ApplicationLayer для задач.
# Здесь HTTP-запросы превращаются в вызовы TodoService.

# APIRouter нужен для маршрутов /todos.
# HTTPException нужен для HTTP-ошибок.
from fastapi import APIRouter, HTTPException

# BaseModel описывает JSON-тело запроса.
from pydantic import BaseModel

# TodoControllerABC - интерфейс контроллера.
# TodoServiceABC - зависимость от бизнес-логики задач.
from app.todos.interfaces import TodoControllerABC, TodoServiceABC


# ПОДСКАЗКА: DTO для POST /todos/.
class TodoCreate(BaseModel):
    # Название задачи.
    title: str
    # id пользователя, которому принадлежит задача.
    user_id: int


# ПОДСКАЗКА: TodoController реализует TodoControllerABC.
class TodoController(TodoControllerABC):
    # Все маршруты начинаются с /todos.
    router = APIRouter(prefix="/todos", tags=["todos"])

    # todo_service внедряется archtool: TodoServiceABC -> TodoService.
    todo_service: TodoServiceABC

    # web_fractal вызовет этот метод и потом подключит router к FastAPI.
    def init_http_routes(self) -> None:
        # POST /todos/ - создать задачу.
        self.router.add_api_route("/", self.create_todo, methods=["POST"])
        # GET /todos/?user_id=... - список задач пользователя.
        self.router.add_api_route("/", self.list_todos, methods=["GET"])
        # PATCH /todos/{todo_id}/complete - завершить задачу.
        self.router.add_api_route("/{todo_id}/complete", self.complete_todo, methods=["PATCH"])

    # Обработчик POST /todos/.
    async def create_todo(self, payload: TodoCreate) -> dict:
        try:
            # Сервис проверит пользователя и создаст задачу.
            return await self.todo_service.create_todo(title=payload.title, user_id=payload.user_id)
        except ValueError as exc:
            # Если пользователь не найден, возвращаем 404.
            raise HTTPException(status_code=404, detail=str(exc)) from exc

    # Обработчик GET /todos/?user_id=...
    async def list_todos(self, user_id: int) -> list[dict]:
        try:
            # Сервис проверит пользователя и вернет его задачи.
            return await self.todo_service.list_user_todos(user_id=user_id)
        except ValueError as exc:
            # Если пользователь не найден, возвращаем 404.
            raise HTTPException(status_code=404, detail=str(exc)) from exc

    # Обработчик PATCH /todos/{todo_id}/complete.
    async def complete_todo(self, todo_id: int) -> dict:
        try:
            # Сервис попросит репозиторий отметить задачу completed=True.
            return await self.todo_service.complete_todo(todo_id=todo_id)
        except ValueError as exc:
            # Если задача не найдена, возвращаем 404.
            raise HTTPException(status_code=404, detail=str(exc)) from exc
