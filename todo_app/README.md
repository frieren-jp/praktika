# BASIC-2 ToDo API

Мини-проект на `archtool` + `web_fractal` + FastAPI + async SQLAlchemy.

## Что реализовано

- `users` bounded context:
  - `POST /users/` - создать пользователя;
  - `GET /users/{id}` - получить пользователя.
- `todos` bounded context:
  - `POST /todos/` - создать задачу пользователя;
  - `GET /todos/?user_id=...` - получить задачи пользователя;
  - `PATCH /todos/{id}/complete` - отметить задачу выполненной.

## Архитектура

```text
todo_app/
  entrypoints/
    run.py
  app/
    config.py
    archtool_conf/
      custom_layers.py
      bundle_project.py
    users/
      interfaces.py
      models.py
      repos.py
      services.py
      controllers.py
    todos/
      interfaces.py
      models.py
      repos.py
      services.py
      controllers.py
```

В проекте используются все 4 дефолтных слоя archtool:

- `PresentationLayer`
- `ApplicationLayer`
- `DomainLayer`
- `InfrastructureLayer`

`TodoService` зависит от `UserServiceABC`, то есть кросс-модульная зависимость проходит через интерфейс. Репозитории используют `UnitOfWork` из `web_fractal`. `session_maker` регистрируется через `injector.register()`. Контроллеры наследуют `HttpControllerABC` и подключаются через `initialize_controllers_api()`.

## Запуск

Требуется Python 3.12 и `uv`.

### Windows PowerShell

```powershell
.\run.ps1
```

После запуска открой:

```text
http://127.0.0.1:8000/docs
```

### Ubuntu / WSL

```bash
cd /mnt/c/Users/freezemyself/Desktop/praktika/todo_app
bash run.sh
```

### Ручной запуск

```bash
cd /mnt/c/Users/freezemyself/Desktop/praktika/todo_app
uv sync
uv run uvicorn entrypoints.run:app --host 127.0.0.1 --port 8000
```

База данных SQLite создается автоматически при старте приложения:

```text
todo_app.db
```

Swagger UI:

```text
http://127.0.0.1:8000/docs
```

## Быстрая проверка

Windows PowerShell:

```powershell
.\check.ps1
```

Ubuntu / WSL:

```bash
bash scripts/run_curl_check.sh
```

Скрипт поднимает `uvicorn`, выполняет curl-запросы ко всем эндпоинтам и останавливает сервер.

## Curl-примеры

Создать пользователя:

```bash
curl -X POST http://127.0.0.1:8000/users/ \
  -H "Content-Type: application/json" \
  -d '{"email":"bob@example.com","name":"Bob"}'
```

Получить пользователя:

```bash
curl http://127.0.0.1:8000/users/1
```

Создать задачу:

```bash
curl -X POST http://127.0.0.1:8000/todos/ \
  -H "Content-Type: application/json" \
  -d '{"title":"Prepare BASIC-2","user_id":1}'
```

Получить список задач пользователя:

```bash
curl "http://127.0.0.1:8000/todos/?user_id=1"
```

Отметить задачу выполненной:

```bash
curl -X PATCH http://127.0.0.1:8000/todos/1/complete
```

## Пример успешного вывода

```text
POST /users/
{"id":1,"email":"bob@example.com","name":"Bob"}

GET /users/1
{"id":1,"email":"bob@example.com","name":"Bob"}

POST /todos/
{"id":1,"title":"Prepare BASIC-2","completed":false,"user_id":1}

GET /todos/?user_id=1
[{"id":1,"title":"Prepare BASIC-2","completed":false,"user_id":1}]

PATCH /todos/1/complete
{"id":1,"title":"Prepare BASIC-2","completed":true,"user_id":1}
```
