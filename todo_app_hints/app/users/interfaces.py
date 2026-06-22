# ПОДСКАЗКА: interfaces.py - архитектурный контракт bounded context users.
# Здесь нет реализации: только "что модуль умеет делать".

# abstractmethod нужен, чтобы методы интерфейса были обязательны для реализации.
from abc import abstractmethod

# ABCController, ABCRepo, ABCService - маркеры слоев archtool.
# По ним archtool понимает, где искать реализации:
# ABCRepo -> repos.py, ABCService -> services.py, ABCController -> controllers.py.
from archtool.layers.default_layer_interfaces import ABCController, ABCRepo, ABCService

# HttpControllerABC - интерфейс web_fractal для FastAPI-контроллеров.
from web_fractal.http.interfaces import HttpControllerABC


# ПОДСКАЗКА: UserRepoABC - контракт репозитория пользователей.
# Репозиторий отвечает за доступ к данным, а не за бизнес-логику.
class UserRepoABC(ABCRepo):
    # create должен сохранить пользователя и вернуть dict.
    @abstractmethod
    async def create(self, email: str, name: str) -> dict: ...

    # get_by_id должен найти пользователя по id или вернуть None.
    @abstractmethod
    async def get_by_id(self, user_id: int) -> dict | None: ...

    # get_by_email нужен сервису, чтобы проверять уникальность email.
    @abstractmethod
    async def get_by_email(self, email: str) -> dict | None: ...


# ПОДСКАЗКА: UserServiceABC - контракт бизнес-логики пользователей.
# Контроллер зависит от этого интерфейса, а не от конкретного UserService.
class UserServiceABC(ABCService):
    # register описывает сценарий регистрации пользователя.
    @abstractmethod
    async def register(self, email: str, name: str) -> dict: ...

    # get_user описывает получение пользователя или ошибку, если его нет.
    @abstractmethod
    async def get_user(self, user_id: int) -> dict: ...


# ПОДСКАЗКА: UserControllerABC принадлежит ApplicationLayer.
# Он одновременно является archtool-контроллером и web_fractal HTTP-контроллером.
class UserControllerABC(ABCController, HttpControllerABC):
    # pass означает, что весь обязательный контракт уже пришел из HttpControllerABC.
    pass
