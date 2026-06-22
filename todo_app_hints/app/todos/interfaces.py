# ПОДСКАЗКА: interfaces.py - контракт bounded context todos.
# По этому файлу можно понять возможности модуля без чтения реализации.

# abstractmethod делает методы обязательными для классов-реализаций.
from abc import abstractmethod

# Маркеры слоев archtool.
from archtool.layers.default_layer_interfaces import ABCController, ABCRepo, ABCService

# Базовый HTTP-контроллер web_fractal.
from web_fractal.http.interfaces import HttpControllerABC


# ПОДСКАЗКА: TodoRepoABC - контракт доступа к данным задач.
class TodoRepoABC(ABCRepo):
    # Создать задачу для пользователя.
    @abstractmethod
    async def create(self, title: str, user_id: int) -> dict: ...

    # Получить список задач конкретного пользователя.
    @abstractmethod
    async def list_by_user(self, user_id: int) -> list[dict]: ...

    # Отметить задачу выполненной или вернуть None, если задачи нет.
    @abstractmethod
    async def complete(self, todo_id: int) -> dict | None: ...


# ПОДСКАЗКА: TodoServiceABC - контракт бизнес-логики задач.
class TodoServiceABC(ABCService):
    # Создать задачу. В реализации сервис проверит, существует ли пользователь.
    @abstractmethod
    async def create_todo(self, title: str, user_id: int) -> dict: ...

    # Получить задачи пользователя.
    @abstractmethod
    async def list_user_todos(self, user_id: int) -> list[dict]: ...

    # Завершить задачу или выбросить ошибку, если ее нет.
    @abstractmethod
    async def complete_todo(self, todo_id: int) -> dict: ...


# ПОДСКАЗКА: TodoControllerABC нужен, чтобы archtool нашел TodoController
# в controllers.py, а web_fractal смог подключить FastAPI router.
class TodoControllerABC(ABCController, HttpControllerABC):
    # Дополнительных методов тут не нужно: init_http_routes() требует HttpControllerABC.
    pass
