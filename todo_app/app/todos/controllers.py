from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.todos.interfaces import TodoControllerABC, TodoServiceABC


class TodoCreate(BaseModel):
    title: str
    user_id: int


class TodoController(TodoControllerABC):
    router = APIRouter(prefix="/todos", tags=["todos"])
    todo_service: TodoServiceABC

    def init_http_routes(self) -> None:
        self.router.add_api_route("/", self.create_todo, methods=["POST"])
        self.router.add_api_route("/", self.list_todos, methods=["GET"])
        self.router.add_api_route("/{todo_id}/complete", self.complete_todo, methods=["PATCH"])

    async def create_todo(self, payload: TodoCreate) -> dict:
        try:
            return await self.todo_service.create_todo(title=payload.title, user_id=payload.user_id)
        except ValueError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc

    async def list_todos(self, user_id: int) -> list[dict]:
        try:
            return await self.todo_service.list_user_todos(user_id=user_id)
        except ValueError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc

    async def complete_todo(self, todo_id: int) -> dict:
        try:
            return await self.todo_service.complete_todo(todo_id=todo_id)
        except ValueError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc
