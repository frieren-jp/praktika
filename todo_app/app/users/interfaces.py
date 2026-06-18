from abc import abstractmethod

from archtool.layers.default_layer_interfaces import ABCController, ABCRepo, ABCService
from web_fractal.http.interfaces import HttpControllerABC


class UserRepoABC(ABCRepo):
    @abstractmethod
    async def create(self, email: str, name: str) -> dict: ...

    @abstractmethod
    async def get_by_id(self, user_id: int) -> dict | None: ...

    @abstractmethod
    async def get_by_email(self, email: str) -> dict | None: ...


class UserServiceABC(ABCService):
    @abstractmethod
    async def register(self, email: str, name: str) -> dict: ...

    @abstractmethod
    async def get_user(self, user_id: int) -> dict: ...


class UserControllerABC(ABCController, HttpControllerABC):
    pass
