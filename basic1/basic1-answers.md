# BASIC-1. Изучение archtool и web_fractal

## Источники

- Документация archtool: https://0nliner.github.io/archtool/
- GitHub archtool: https://github.com/0nliner/archtool
- PyPI web_fractal: https://pypi.org/project/web_fractal/
- Пример интеграции: https://0nliner.github.io/archtool/examples/web_fractal/

## 1. Что такое `DependencyInjector` и какую проблему он решает?

`DependencyInjector` в archtool - это объект, который собирает приложение из заранее описанных модулей и связывает зависимости между классами. Его задача - убрать ручную "разводку" объектов в точке входа.

В обычном проекте без DI часто получается так: разработчик вручную создает репозиторий, потом сервис, потом присваивает `service.repo = repo`, потом другой сервис, контроллер и так далее. Чем больше модулей, тем легче забыть одну связь или подключить не ту реализацию.

archtool предлагает другой подход:

```python
injector = DependencyInjector(
    modules_list=[
        AppModule("app.users"),
        AppModule("app.orders"),
    ],
    project_root=ROOT,
)
injector.inject()
```

После этого archtool сам находит интерфейсы и реализации в модулях. Например, если есть `UserRepoABC` в `interfaces.py`, реализация `UserRepo` в `repos.py`, а в сервисе написано:

```python
class UserService(UserServiceABC):
    repo: UserRepoABC
```

то `DependencyInjector` создаст `UserRepo`, создаст `UserService` и подставит репозиторий в поле `repo`. Сервис зависит от абстракции `UserRepoABC`, а не от конкретного класса `UserRepo`. Это напрямую связано с принципом Dependency Inversion из SOLID.

## 2. Двухпроходной алгоритм инъекции: Pass 1 и Pass 2

archtool использует двухпроходную сборку, потому что сначала надо создать все объекты, а уже потом связывать их между собой.

### Pass 1 - discover

На первом проходе archtool ищет компоненты.

Для каждого `AppModule` и каждого слоя он:

1. Открывает `interfaces.py`.
2. Ищет абстрактные классы, которые наследуют маркеры слоя, например `ABCRepo`, `ABCService`, `ABCController`.
3. Переходит в соответствующий файл реализации, например `repos.py`, `services.py`, `controllers.py`.
4. Ищет конкретный класс, который реализует найденный интерфейс.
5. Создает экземпляр этого класса через вызов без аргументов: `Class()`.
6. Кладет объект в реестр зависимостей по ключу интерфейса.

Пример: `UserRepoABC` найден в `interfaces.py`, `UserRepo` найден в `repos.py`, после этого в контейнере появляется связь `UserRepoABC -> UserRepo()`.

Важно: из-за этого реализации в archtool не должны требовать аргументы в `__init__`. Если объект надо создать особым способом, его регистрируют вручную через `injector.register(...)`.

### Между проходами

После обнаружения archtool проверяет правила слоев. Если включен контроль слоев, он смотрит, не зависит ли нижний слой от верхнего. Например, сервис не должен зависеть от контроллера.

Также строится граф зависимостей и выполняется топологическая сортировка. Это нужно, чтобы внедрять зависимости в нормальном порядке.

### Pass 2 - inject

На втором проходе archtool уже не ищет классы, а связывает созданные объекты.

Он читает классовые аннотации конкретных классов:

```python
class OrderService(OrderServiceABC):
    repo: OrderRepoABC
    user_service: UserServiceABC
```

Потом для каждой аннотации ищет готовый объект в реестре и делает примерно следующее:

```python
order_service.repo = order_repo
order_service.user_service = user_service
```

В итоге объект получает все зависимости без ручного создания и без прямого импорта конкретных реализаций.

## 3. Что такое `Layer` в archtool и зачем нужен контроль слоев?

`Layer` - это описание архитектурного слоя: какие файлы он сканирует, какие интерфейсы считает компонентами и от какого слоя может зависеть.

Во встроенной схеме archtool есть четыре слоя:

| Слой | Файл | Маркер интерфейса | Может зависеть от |
|---|---|---|---|
| `InfrastructureLayer` | `repos.py` | `ABCRepo` | ни от кого |
| `DomainLayer` | `services.py` | `ABCService` | `InfrastructureLayer` |
| `ApplicationLayer` | `controllers.py` | `ABCController` | `DomainLayer` |
| `PresentationLayer` | `views.py` | `ABCView` | `ApplicationLayer` |

Контроль слоев нужен, чтобы архитектура была не просто договоренностью в README, а проверяемым правилом. Без такой проверки проект постепенно начинает смешиваться: контроллеры лезут в базу, сервисы импортируют внешние HTTP-обработчики, репозитории знают о бизнес-сценариях.

Если сервис попытается импортировать контроллер или зависеть от интерфейса контроллера, это будет зависимость нижнего слоя от верхнего. При запуске `injector.inject()` archtool должен выбросить `TopLevelLayerUsingException`. То есть ошибка обнаружится при старте приложения, а не случайно в продакшене.

Смысл правила: внутренние слои должны быть устойчивыми и независимыми от внешних. Контроллер может знать о сервисе, потому что контроллер - внешний слой. Сервис не должен знать о контроллере, потому что бизнес-логика не должна зависеть от способа доставки запроса.

## 4. Что такое `AppModule` и как он связан с bounded context?

`AppModule` - это описание одного модуля приложения, который archtool должен просканировать. Внутри него передается dotted import path:

```python
AppModule("app.users")
AppModule("app.orders")
AppModule("app.payments.gateway")
```

Для archtool это означает: "зайди в этот Python-пакет и найди там `interfaces.py`, `repos.py`, `services.py`, `controllers.py` и другие файлы по слоям".

С точки зрения архитектуры `AppModule` удобно считать bounded context, то есть ограниченным контекстом предметной области. Например:

- `app.users` отвечает за пользователей;
- `app.orders` отвечает за заказы;
- `app.payments` отвечает за платежи.

У каждого такого контекста есть свои интерфейсы, свои сервисы, свои репозитории и свои правила. Если одному контексту нужно использовать другой, зависимость объявляется явно через интерфейс. Например, `OrderService` может зависеть от `UserServiceABC`, но не должен напрямую создавать `UserService`.

Это помогает держать модули независимыми. Новый разработчик может открыть `app/orders/interfaces.py` и понять, что умеет модуль заказов, не читая всю реализацию.

## 5. Что дает `web_fractal` поверх archtool?

`archtool` отвечает за архитектурную сборку: интерфейсы, реализации, слои, DI. `web_fractal` добавляет практические инструменты для backend-приложения на FastAPI и async SQLAlchemy.

Ключевые утилиты:

1. `UnitOfWork`

   Контекстный менеджер для async SQLAlchemy-сессии. Он открывает сессию, дает ее репозиториям, а при выходе из блока делает `commit`, если ошибок не было, или `rollback`, если возникло исключение.

2. `BaseRepo`

   Базовый класс для репозиториев. В нем есть поле `session_maker`, которое может быть внедрено через archtool, и вспомогательные методы для работы с сессией и преобразования ORM-моделей в DTO.

3. `Base`

   Базовый SQLAlchemy `DeclarativeBase` с поддержкой async-атрибутов. От него удобно наследовать ORM-модели проекта.

4. `initialize_controllers_api(injector, app)`

   Функция, которая берет из DI-контейнера все HTTP-контроллеры, вызывает у них `init_http_routes()` и подключает их `router` к FastAPI-приложению через `app.include_router(...)`.

5. `import_all_models(Base)`

   Функция, которая проходит по зарегистрированным `AppModule`, импортирует их `models.py` и собирает ORM-модели. Это нужно, чтобы `Base.metadata` знал обо всех таблицах до вызова `create_all()`.

6. `HttpControllerABC`

   Абстрактная база для HTTP-контроллеров. Она требует метод `init_http_routes()` и поле `router: APIRouter`. Также дает вспомогательный метод `reg_route()` для регистрации маршрута по методу контроллера.

Итого: `web_fractal` не заменяет archtool, а дополняет его типовыми backend-деталями: транзакции, репозитории, ORM-модели, FastAPI-роутеры.

## 6. Как `UnitOfWork` управляет транзакциями?

`UnitOfWork` хранит `session_maker` и текущую `AsyncSession`. Его используют как async context manager:

```python
async with UnitOfWork(session_maker) as uow:
    session = uow.get_session()
    ...
```

Когда выполнение входит в блок, `UnitOfWork` создает сессию. Когда блок завершается:

- если исключения не было, вызывается `commit()`;
- если было исключение, вызывается `rollback()`;
- после этого сессия закрывается через `close()`.

Так транзакционная логика не размазывается по каждому методу. Код репозитория или сервиса работает с `uow`, а решение "закоммитить или откатить" находится в одном месте.

### Сессия на метод

Подход "сессия на метод" означает, что каждый метод репозитория сам открывает свой `UnitOfWork`:

```python
async def create_user(...):
    async with UnitOfWork(self.session_maker) as uow:
        session = uow.get_session()
        ...
```

Это удобно для простых операций: один метод - одна транзакция. Например, просто создать пользователя или получить запись по ID.

Минус: если сервис вызывает несколько методов репозиториев подряд, каждый метод может иметь отдельную транзакцию. Тогда сложно гарантировать атомарность всей бизнес-операции.

### Общая транзакция через UoW

Для сложного сценария сервис сам открывает `UnitOfWork` и передает его в несколько репозиториев:

```python
async with UnitOfWork(self.session_maker) as uow:
    user = await self.user_repo.get_by_id_in_uow(user_id, uow)
    order = await self.order_repo.create_in_uow(user["id"], items, uow)
```

Здесь все действия идут через одну сессию и одну транзакцию. Если создание заказа упадет после проверки пользователя, весь блок откатится. Это лучше для бизнес-сценариев вроде "создать заказ, списать остатки, записать платеж", где нельзя сохранить только половину операции.

## 7. Типичная структура проекта на archtool + web_fractal

Пример структуры:

```text
myapp/
  pyproject.toml
  entrypoints/
    run.py
  app/
    config.py
    archtool_conf/
      custom_layers.py
      bundle_project.py
    users/
      __init__.py
      interfaces.py
      models.py
      repos.py
      services.py
      controllers.py
    orders/
      __init__.py
      interfaces.py
      models.py
      repos.py
      services.py
      controllers.py
```

Что за что отвечает:

`entrypoints/run.py`

Точка входа приложения. Создает `FastAPI`, вызывает функцию сборки DI, запускает `uvicorn`.

`app/config.py`

Настройки проекта: DSN базы данных, host, port, режимы запуска.

`app/archtool_conf/custom_layers.py`

Здесь лежит список модулей:

```python
APPS = [
    AppModule("app.users"),
    AppModule("app.orders"),
]
```

Также здесь можно объявить набор слоев, если проект использует не только стандартные слои archtool.

`app/archtool_conf/bundle_project.py`

Главная функция сборки приложения. Обычно она:

1. Создает `DependencyInjector`.
2. Создает SQLAlchemy `engine` и `async_sessionmaker`.
3. Регистрирует инфраструктурные объекты через `injector.register(...)`.
4. Вызывает `import_all_models(Base)`.
5. Запускает `injector.inject()`.
6. Кладет инжектор в `app.state.injector`.
7. Вызывает `initialize_controllers_api(injector, app)`.

`app/users/interfaces.py`

Контракты модуля пользователей: `UserRepoABC`, `UserServiceABC`, `UserControllerABC`. Это главный файл для понимания возможностей bounded context.

`app/users/models.py`

ORM-модели SQLAlchemy, например `UserORM(Base)`.

`app/users/repos.py`

Репозитории. Работают с базой данных через SQLAlchemy и `UnitOfWork`. Наследуют интерфейсы из `interfaces.py`.

`app/users/services.py`

Бизнес-логика. Сервисы зависят от репозиториев через интерфейсы, например `repo: UserRepoABC`.

`app/users/controllers.py`

HTTP-контроллеры FastAPI. Контроллер наследует `HttpControllerABC` или свой интерфейс контроллера, содержит `router = APIRouter(...)`, объявляет зависимость на сервис и регистрирует маршруты в `init_http_routes()`.

`app/orders/...`

Такой же набор файлов для bounded context заказов. Если заказам нужен пользователь, `OrderService` объявляет зависимость на `UserServiceABC`, а archtool подставляет реализацию из `app.users`.

Упрощенная схема зависимостей:

```text
FastAPI app
  -> controllers.py / HttpControllerABC
      -> services.py / ABCService
          -> repos.py / ABCRepo
              -> SQLAlchemy session через UnitOfWork
```

При этом код зависит не от конкретных классов, а от интерфейсов из `interfaces.py`. archtool собирает эти зависимости, а web_fractal помогает подключить базу данных и HTTP-роутеры.

## Короткий вывод

archtool задает архитектурный каркас: bounded contexts, интерфейсы, слои и автоматическую DI-сборку. web_fractal добавляет практический backend-слой для FastAPI и SQLAlchemy: транзакции через `UnitOfWork`, базовые репозитории, ORM-базу и автоматическую регистрацию контроллеров.

Связь с SOLID такая: интерфейсы фиксируют контракты, DI заставляет зависеть от абстракций, слои ограничивают направления зависимостей, а `AppModule` помогает держать каждый bounded context отдельно.
