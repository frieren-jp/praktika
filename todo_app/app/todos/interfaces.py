from abc import abstractmethod

from archtool.layers.default_layer_interfaces import ABCController, ABCRepo, ABCService
from web_fractal.http.interfaces import HttpControllerABC


class TodoRepoABC(ABCRepo):
    @abstractmethod
    async def create(self, title: str, user_id: int) -> dict: ...

    @abstractmethod
    async def list_by_user(self, user_id: int) -> list[dict]: ...

    @abstractmethod
    async def complete(self, todo_id: int) -> dict | None: ...


class TodoServiceABC(ABCService):
    @abstractmethod
    async def create_todo(self, title: str, user_id: int) -> dict: ...

    @abstractmethod
    async def list_user_todos(self, user_id: int) -> list[dict]: ...

    @abstractmethod
    async def complete_todo(self, todo_id: int) -> dict: ...


class TodoControllerABC(ABCController, HttpControllerABC):
    pass
