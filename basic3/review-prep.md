# BASIC-3. Подготовка к ревью ToDo API

## 1. Быстрый запуск перед демо

Из PowerShell:

```powershell
cd C:\Users\freezemyself\Desktop\praktika\todo_app
.\check.ps1
```

Эта команда сама:

1. синхронизирует зависимости через `uv sync`;
2. запускает `uvicorn`;
3. выполняет curl-запросы ко всем эндпоинтам;
4. останавливает сервер.

Для интерактивного демо Swagger UI:

```powershell
cd C:\Users\freezemyself\Desktop\praktika\todo_app
.\run.ps1
```

Открыть:

```text
http://127.0.0.1:8000/docs
```

## 2. Что показать на демо

1. Запустить `.\run.ps1`.
2. Открыть Swagger UI.
3. Выполнить `POST /users/`:

```json
{
  "email": "demo@example.com",
  "name": "Demo User"
}
```

4. Выполнить `GET /users/{id}` и показать, что пользователь сохранился.
5. Выполнить `POST /todos/`:

```json
{
  "title": "Show BASIC-3 demo",
  "user_id": 1
}
```

6. Выполнить `GET /todos/?user_id=1` и показать список задач.
7. Выполнить `PATCH /todos/{id}/complete` и показать, что `completed` стал `true`.
8. Можно сказать, что SQLite-файл `todo_app.db` создается автоматически при старте приложения, а данные реально сохраняются в таблицы.

## 3. Что важно объяснить по структуре

Проект разделен на два bounded context:

- `app/users` - пользователи;
- `app/todos` - задачи.

В каждом модуле одинаковая структура:

- `interfaces.py` - контракты;
- `models.py` - SQLAlchemy ORM-модели;
- `repos.py` - доступ к базе;
- `services.py` - бизнес-логика;
- `controllers.py` - HTTP-роуты.

Сборка проекта находится в:

```text
app/archtool_conf/bundle_project.py
```

Там создаются:

- `DependencyInjector`;
- SQLAlchemy `engine`;
- `async_sessionmaker`;
- регистрация `session_maker` через `injector.register()`;
- импорт моделей;
- запуск `injector.inject()`;
- подключение контроллеров через `initialize_controllers_api()`.

## 4. Ответы на ожидаемые вопросы

### Почему зависимость объявлена аннотацией, а не через `__init__`?

Потому что так работает стиль archtool. Реализации создаются автоматически через вызов без аргументов: `Class()`. Если бы зависимости передавались через `__init__`, archtool должен был бы сам разбирать конструкторы и порядок их вызова.

Здесь зависимость объявляется на конкретном классе:

```python
class TodoService(TodoServiceABC):
    repo: TodoRepoABC
    user_service: UserServiceABC
```

На втором проходе archtool читает эти аннотации и делает `setattr`: подставляет реализацию `TodoRepoABC` в `repo`, а `UserServiceABC` в `user_service`.

Плюс в том, что сервис зависит от интерфейса, а не от конкретного класса. Это поддерживает Dependency Inversion: бизнес-логика не знает, какая именно реализация репозитория или сервиса будет подключена.

### Что произойдет, если убрать `layers` из `DependencyInjector`?

В текущей версии archtool, если не передать `layers`, используются четыре стандартных слоя Clean Architecture. То есть проект, скорее всего, продолжит собираться.

Но я передал `layers=app_layers` явно, потому что это требование задания и потому что так в коде видно архитектурное намерение: мы осознанно используем `PresentationLayer`, `ApplicationLayer`, `DomainLayer`, `InfrastructureLayer`.

Если совсем отключить контроль слоев, например через `enforce_layers=False`, то archtool перестанет ловить нарушения границ. Тогда сервис мог бы начать зависеть от контроллера, и ошибка архитектуры не упала бы при старте.

### Зачем нужен `UnitOfWork`, если `session_maker` уже создает сессии?

`session_maker` только умеет создать SQLAlchemy-сессию. Он не отвечает за сценарий транзакции.

`UnitOfWork` задает правило:

- при входе в блок открыть сессию;
- если ошибок нет - сделать `commit`;
- если есть исключение - сделать `rollback`;
- в конце закрыть сессию.

То есть `UnitOfWork` управляет жизненным циклом транзакции, а `session_maker` только фабрика сессий.

В простом проекте каждый метод репозитория открывает свой `UnitOfWork`. В более сложном сценарии можно открыть один `UnitOfWork` в сервисе и передать его в несколько репозиториев, чтобы вся бизнес-операция была одной транзакцией.

### Как archtool понимает, что `UserRepo` - реализация `UserRepoABC`?

Через соглашение структуры и наследование.

В `interfaces.py` есть:

```python
class UserRepoABC(ABCRepo):
    ...
```

`ABCRepo` говорит archtool, что это интерфейс инфраструктурного слоя.

В `repos.py` есть:

```python
class UserRepo(UserRepoABC):
    ...
```

На первом проходе archtool сканирует `interfaces.py`, находит `UserRepoABC`, затем сканирует `repos.py` и ищет конкретный подкласс этого интерфейса. Так он строит пару:

```text
UserRepoABC -> UserRepo()
```

Потом эта пара кладется в DI-реестр.

### Что будет, если добавить третий модуль `notifications`?

Нужно создать папку:

```text
app/notifications/
  __init__.py
  interfaces.py
  models.py
  repos.py
  services.py
  controllers.py
```

И добавить модуль в `app/archtool_conf/custom_layers.py`:

```python
APPS = [
    AppModule("app.users"),
    AppModule("app.todos"),
    AppModule("app.notifications"),
]
```

Если у модуля будут модели, `import_all_models()` или fallback-импорт подтянет `models.py`. Если будут контроллеры, `initialize_controllers_api()` подключит роутеры.

Существующие `users` и `todos` не нужно переписывать. Если `TodoService` должен отправлять уведомления, он объявит зависимость на `NotificationServiceABC` через аннотацию.

## 5. Что было сложнее всего

Самое сложное было не написать FastAPI-эндпоинты, а состыковать реальные версии `archtool` и `web_fractal`.

В процессе выяснилось:

- `web_fractal` 0.0.1 использует зависимости, которые не все указаны в metadata PyPI, поэтому пришлось явно добавить `aiohttp`, `furl`, `pytz`;
- `web_fractal.initialize_controllers_api()` ожидает у инжектора поле `_dependencies`, а у текущего `archtool` публичное поле называется `dependencies`, поэтому в `bundle_project.py` добавлен compatibility bridge;
- `import_all_models()` в `web_fractal` может падать из-за выражения с путями, поэтому добавлен fallback, который явно импортирует `app.users.models` и `app.todos.models`.

Это хороший пример того, почему важно не просто читать документацию, а запускать проект на чистом окружении.

## 6. Что можно улучшить в archtool/web_fractal

Идеи для улучшения:

1. В `web_fractal` стоит поправить зависимости пакета на PyPI, чтобы `pip install web_fractal` сразу ставил все нужное: `aiohttp`, `furl`, `pytz` и другие runtime-зависимости.

2. `initialize_controllers_api()` лучше должен использовать публичное поле `injector.dependencies`, а не приватное `_dependencies`. Тогда не нужен compatibility bridge.

3. `import_all_models()` лучше сделать независимым от странной операции с `pathlib.Path`, а просто импортировать `f"{app.import_path}.models"` для каждого `AppModule`.

4. В `archtool` можно добавить более явную ошибку, если у реализации есть `__init__` с аргументами: подсказать, что нужно использовать классовые аннотации или `injector.register()`.

5. Было бы полезно иметь официальный шаблон `archtool + web_fractal + FastAPI + SQLAlchemy`, который создается одной CLI-командой.

## 7. Мини-речь на 1 минуту

В этом проекте `archtool` отвечает за архитектурную сборку: он сканирует модули `users` и `todos`, находит интерфейсы и реализации, проверяет слои и внедряет зависимости по аннотациям. `web_fractal` добавляет прикладные backend-инструменты: `UnitOfWork` для транзакций, базу SQLAlchemy и автоматическое подключение HTTP-контроллеров.

Главная идея: сервисы и контроллеры не создают зависимости руками и не зависят от конкретных классов. Например, `TodoService` зависит от `TodoRepoABC` и `UserServiceABC`, а конкретные `TodoRepo` и `UserService` подставляет DI-контейнер. Так код лучше соответствует SOLID: зависимости идут через абстракции, а слои не смешиваются.
